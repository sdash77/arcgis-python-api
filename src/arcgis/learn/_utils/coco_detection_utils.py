# ------------------------------------------------------------------------
# Deformable DETR
# Copyright (c) 2020 SenseTime. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 [see LICENSE for details]
# ------------------------------------------------------------------------
# Modified from DETR (https://github.com/facebookresearch/detr)
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
# ------------------------------------------------------------------------

"""
COCO dataset which returns image_id for evaluation.

Mostly copy-paste from https://github.com/pytorch/vision/blob/13b35ff/references/detection/coco_utils.py
"""
from pathlib import Path
import numpy as np
import torch
import torch.utils.data
from pycocotools import mask as coco_mask
import torch.distributed as dist
from typing import Optional, List
from torch import Tensor
import matplotlib.pyplot as plt

# from torchvision.ops.misc import _NewEmptyTensorOp
from torchvision.datasets.vision import VisionDataset
from PIL import Image
import os
import os.path
import tqdm
from io import BytesIO
from torchvision.ops.boxes import box_area

"""
Transforms and data augmentation for both image + bbox.
"""
import random
import torchvision.transforms.functional_tensor as TF

import PIL
import torch
import torchvision.transforms as T
import torchvision.transforms.functional as F
from torchvision.transforms import RandomResizedCrop


def interpolate(
    input, size=None, scale_factor=None, mode="nearest", align_corners=None
):
    # type: (Tensor, Optional[List[int]], Optional[float], str, Optional[bool]) -> Tensor
    """
    Equivalent to nn.functional.interpolate, but with support for empty batch sizes.
    This will eventually be supported natively by PyTorch, and this
    class can go away.
    """
    if float(torchvision.__version__[:3]) < 0.7:
        if input.numel() > 0:
            return torch.nn.functional.interpolate(
                input, size, scale_factor, mode, align_corners
            )

        output_shape = _output_size(2, input, size, scale_factor)
        output_shape = list(input.shape[:-2]) + list(output_shape)
        if float(torchvision.__version__[:3]) < 0.5:
            return _NewEmptyTensorOp.apply(input, output_shape)
        return _new_empty_tensor(input, output_shape)
    else:
        return torchvision.ops.misc.interpolate(
            input, size, scale_factor, mode, align_corners
        )


def inverse_sigmoid(x, eps=1e-5):
    x = x.clamp(min=0, max=1)
    x1 = x.clamp(min=eps)
    x2 = (1 - x).clamp(min=eps)
    return torch.log(x1 / x2)


def box_iou(boxes1, boxes2):
    area1 = box_area(boxes1)
    area2 = box_area(boxes2)

    lt = torch.max(boxes1[:, None, :2], boxes2[:, :2])  # [N,M,2]
    rb = torch.min(boxes1[:, None, 2:], boxes2[:, 2:])  # [N,M,2]

    wh = (rb - lt).clamp(min=0)  # [N,M,2]
    inter = wh[:, :, 0] * wh[:, :, 1]  # [N,M]

    union = area1[:, None] + area2 - inter

    iou = inter / union
    return iou, union


def generalized_box_iou(boxes1, boxes2):
    """
    Generalized IoU from https://giou.stanford.edu/

    The boxes should be in [x0, y0, x1, y1] format

    Returns a [N, M] pairwise matrix, where N = len(boxes1)
    and M = len(boxes2)
    """
    # degenerate boxes gives inf / nan results
    # so do an early check
    # print(boxes1)
    # print((boxes1[:, 2:] >= boxes1[:, :2]).all())
    # assert (boxes1[:, 2:] >= boxes1[:, :2]).all()
    # assert (boxes2[:, 2:] >= boxes2[:, :2]).all()
    iou, union = box_iou(boxes1, boxes2)

    lt = torch.min(boxes1[:, None, :2], boxes2[:, :2])
    rb = torch.max(boxes1[:, None, 2:], boxes2[:, 2:])

    wh = (rb - lt).clamp(min=0)  # [N,M,2]
    area = wh[:, :, 0] * wh[:, :, 1]

    return iou - (area - union) / area


def box_cxcywh_to_xyxy(x):
    x_c, y_c, w, h = x.unbind(-1)
    b = [(x_c - 0.5 * w), (y_c - 0.5 * h), (x_c + 0.5 * w), (y_c + 0.5 * h)]
    return torch.stack(b, dim=-1)


def box_xyxy_to_cxcywh(x):
    x0, y0, x1, y1 = x.unbind(-1)
    b = [(x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0), (y1 - y0)]
    return torch.stack(b, dim=-1)


def crop(image, target, region):
    cropped_image = F.crop(image, *region)

    target = target.copy()
    i, j, h, w = region

    # should we do something wrt the original size?
    target["size"] = torch.tensor([h, w])

    fields = ["labels", "area", "iscrowd", "patches"]

    if "boxes" in target:
        boxes = target["boxes"]
        max_size = torch.as_tensor([w, h], dtype=torch.float32)
        cropped_boxes = boxes - torch.as_tensor([j, i, j, i])
        cropped_boxes = torch.min(cropped_boxes.reshape(-1, 2, 2), max_size)
        cropped_boxes = cropped_boxes.clamp(min=0)
        area = (cropped_boxes[:, 1, :] - cropped_boxes[:, 0, :]).prod(dim=1)
        target["boxes"] = cropped_boxes.reshape(-1, 4)
        target["area"] = area
        fields.append("boxes")

    if "masks" in target:
        # FIXME should we update the area here if there are no boxes?
        target["masks"] = target["masks"][:, i : i + h, j : j + w]
        fields.append("masks")

    # remove elements for which the boxes or masks that have zero area
    if "boxes" in target or "masks" in target:
        # favor boxes selection when defining which elements to keep
        # this is compatible with previous implementation
        if "boxes" in target:
            cropped_boxes = target["boxes"].reshape(-1, 2, 2)
            keep = torch.all(cropped_boxes[:, 1, :] > cropped_boxes[:, 0, :], dim=1)
        else:
            keep = target["masks"].flatten(1).any(1)

        for field in fields:
            if field in target:
                target[field] = target[field][keep]

    return cropped_image, target


def hflip(image, target):
    flipped_image = F.hflip(image)

    w, h = image.size

    target = target.copy()
    if "boxes" in target:
        boxes = target["boxes"]
        boxes = boxes[:, [2, 1, 0, 3]] * torch.as_tensor(
            [-1, 1, -1, 1]
        ) + torch.as_tensor([w, 0, w, 0])
        target["boxes"] = boxes

    if "masks" in target:
        target["masks"] = target["masks"].flip(-1)

    return flipped_image, target


def resize(image, target, size, max_size=None):
    # size can be min_size (scalar) or (w, h) tuple

    def get_size_with_aspect_ratio(image_size, size, max_size=None):
        w, h = image_size
        if max_size is not None:
            min_original_size = float(min((w, h)))
            max_original_size = float(max((w, h)))
            if max_original_size / min_original_size * size > max_size:
                size = int(round(max_size * min_original_size / max_original_size))

        if (w <= h and w == size) or (h <= w and h == size):
            return (h, w)

        if w < h:
            ow = size
            oh = int(size * h / w)
        else:
            oh = size
            ow = int(size * w / h)

        return (oh, ow)

    def get_size(image_size, size, max_size=None):
        if isinstance(size, (list, tuple)):
            return size[::-1]
        else:
            return get_size_with_aspect_ratio(image_size, size, max_size)

    size = get_size(image.size, size, max_size)
    rescaled_image = F.resize(image, size)

    if target is None:
        return rescaled_image, None

    ratios = tuple(
        float(s) / float(s_orig) for s, s_orig in zip(rescaled_image.size, image.size)
    )
    ratio_width, ratio_height = ratios

    target = target.copy()
    if "boxes" in target:
        boxes = target["boxes"]
        scaled_boxes = boxes * torch.as_tensor(
            [ratio_width, ratio_height, ratio_width, ratio_height]
        )
        target["boxes"] = scaled_boxes

    if "area" in target:
        area = target["area"]
        scaled_area = area * (ratio_width * ratio_height)
        target["area"] = scaled_area

    h, w = size
    target["size"] = torch.tensor([h, w])

    if "masks" in target:
        target["masks"] = (
            interpolate(target["masks"][:, None].float(), size, mode="nearest")[:, 0]
            > 0.5
        )

    return rescaled_image, target


def pad(image, target, padding):
    # assumes that we only pad on the bottom right corners
    padded_image = F.pad(image, (0, 0, padding[0], padding[1]))
    if target is None:
        return padded_image, None
    target = target.copy()
    # should we do something wrt the original size?
    target["size"] = torch.tensor(padded_image[::-1])
    if "masks" in target:
        target["masks"] = torch.nn.functional.pad(
            target["masks"], (0, padding[0], 0, padding[1])
        )
    return padded_image, target


class RandomCrop(object):
    def __init__(self, size):
        self.size = size

    def __call__(self, img, target):
        region = T.RandomCrop.get_params(img, self.size)
        return crop(img, target, region)


class RandomSizeCrop(object):
    def __init__(self, min_size: int, max_size: int):
        self.min_size = min_size
        self.max_size = max_size

    def __call__(self, img: PIL.Image.Image, target: dict):
        w = random.randint(self.min_size, min(img.width, self.max_size))
        h = random.randint(self.min_size, min(img.height, self.max_size))
        region = T.RandomCrop.get_params(img, [h, w])
        return crop(img, target, region)


class CenterCrop(object):
    def __init__(self, size):
        self.size = size

    def __call__(self, img, target):
        image_width, image_height = img.size
        crop_height, crop_width = self.size
        crop_top = int(round((image_height - crop_height) / 2.0))
        crop_left = int(round((image_width - crop_width) / 2.0))
        return crop(img, target, (crop_top, crop_left, crop_height, crop_width))


class RandomHorizontalFlip(object):
    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, img, target):
        if random.random() < self.p:
            return hflip(img, target)
        return img, target


class RandomResize(object):
    def __init__(self, sizes, max_size=None):
        assert isinstance(sizes, (list, tuple))
        self.sizes = sizes
        self.max_size = max_size

    def __call__(self, img, target=None):
        size = random.choice(self.sizes)
        return resize(img, target, size, self.max_size)


class RandomPad(object):
    def __init__(self, max_pad):
        self.max_pad = max_pad

    def __call__(self, img, target):
        pad_x = random.randint(0, self.max_pad)
        pad_y = random.randint(0, self.max_pad)
        return pad(img, target, (pad_x, pad_y))


class RandomSelect(object):
    """
    Randomly selects between transforms1 and transforms2,
    with probability p for transforms1 and (1 - p) for transforms2
    """

    def __init__(self, transforms1, transforms2, p=0.5):
        self.transforms1 = transforms1
        self.transforms2 = transforms2
        self.p = p

    def __call__(self, img, target):
        if random.random() < self.p:
            return self.transforms1(img, target)
        return self.transforms2(img, target)


class ToTensor(object):
    def __call__(self, img, target):
        return F.to_tensor(img), target


class RandomErasing(object):
    def __init__(self, *args, **kwargs):
        self.eraser = T.RandomErasing(*args, **kwargs)

    def __call__(self, img, target):
        return self.eraser(img), target


class Normalize(object):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, image, target=None):
        image = F.normalize(image, mean=self.mean, std=self.std)
        if target is None:
            return image, None
        target = target.copy()
        h, w = image.shape[-2:]
        if "boxes" in target:
            boxes = target["boxes"]
            boxes = box_xyxy_to_cxcywh(boxes)
            boxes = boxes / torch.tensor([w, h, w, h], dtype=torch.float32)
            target["boxes"] = boxes
        return image, target


class Compose(object):
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, image, target):
        for t in self.transforms:
            image, target = t(image, target)
        return image, target

    def __repr__(self):
        format_string = self.__class__.__name__ + "("
        for t in self.transforms:
            format_string += "\n"
            format_string += "    {0}".format(t)
        format_string += "\n)"
        return format_string


def random_image_box_translation(img, boxes):
    boxes = boxes.clone()
    im_shape = img.shape
    h = random.randint(int(img.shape[2] / 4), img.shape[2] - int(img.shape[2] / 4))
    w = random.randint(int(img.shape[3] / 4), img.shape[3] - int(img.shape[3] / 4))
    img = torch.nn.functional.interpolate(img, (h, w), mode="bilinear")
    new_img2 = torch.zeros(im_shape).to(img)
    i = random.randint(0, im_shape[2] - h)
    j = random.randint(0, im_shape[2] - w)
    new_img2[:, :, i : i + h, j : j + w] = img

    factor_h = h / (im_shape[-1] - 1)
    factor_w = w / (im_shape[-2] - 1)
    i = i / (im_shape[-1] - 1)
    j = j / (im_shape[-2] - 1)
    boxes = box_cxcywh_to_xyxy(boxes)
    boxes[..., 0] = boxes[..., 0] * factor_w + j
    boxes[..., 1] = boxes[..., 1] * factor_h + i
    boxes[..., 2] = boxes[..., 2] * factor_w + j
    boxes[..., 3] = boxes[..., 3] * factor_h + i
    boxes = box_xyxy_to_cxcywh(boxes)
    img = new_img2
    return img, boxes


def h_flip(x, y):
    y = y.clone()
    x = TF.hflip(x)
    y[..., 0] = 1 - y[..., 0]
    return x, y


def v_flip(x, y):
    y = y.clone()
    x = TF.vflip(x)
    y[..., 1] = 1 - y[..., 1]
    return x, y


def random_translate(image, mask, box_scale, box_shift):
    im_shape = image.shape
    h = random.randint(int(im_shape[1] / 4), im_shape[1] - int(im_shape[1] / 4))
    w = random.randint(int(im_shape[2] / 4), im_shape[2] - int(im_shape[2] / 4))
    img = torch.nn.functional.interpolate(image.unsqueeze(0), (h, w), mode="bilinear")[
        0
    ]
    m = torch.nn.functional.interpolate(
        mask.unsqueeze(0).type(torch.float), (h, w), mode="nearest"
    )[0].type(torch.bool)
    new_img2 = torch.zeros(im_shape).to(img)
    new_mask2 = torch.zeros(mask.shape).to(mask)
    i = random.randint(0, im_shape[1] - h)
    j = random.randint(0, im_shape[2] - w)
    new_img2[:, i : i + h, j : j + w] = img
    new_mask2[:, i : i + h, j : j + w] = m
    factor_h = h / (im_shape[1] - 1)
    factor_w = w / (im_shape[2] - 1)
    i = i / (im_shape[1] - 1)
    j = j / (im_shape[2] - 1)
    box_scale[0::2] *= factor_w
    box_scale[1::2] *= factor_h
    box_shift[0] = box_shift[0] * factor_w + j
    box_shift[1] = box_shift[1] * factor_h + i
    return new_img2, new_mask2, box_scale, box_shift


@torch.no_grad()
def get_random_image_and_perm(image, mask):
    box_scale = torch.ones((4))
    box_shift = torch.zeros((4))
    new_img2 = image.clone()
    new_mask2 = mask.clone()
    new_mask2 = new_mask2.unsqueeze(0)
    new_img2, new_mask2, box_scale, box_shift = random_crop_and_resize(
        new_img2, new_mask2, box_scale, box_shift
    )

    if random.random() > 0.5:
        new_img2, new_mask2, box_scale, box_shift = random_translate(
            new_img2, new_mask2, box_scale, box_shift
        )

    if random.random() > 0.5:
        new_img2 = TF.hflip(new_img2)
        new_mask2 = TF.hflip(new_mask2)
        box_shift[0] = 1 - box_shift[0]
        box_scale[0] *= -1
    if random.random() > 0.5:
        new_img2 = TF.vflip(new_img2)
        new_mask2 = TF.vflip(new_mask2)
        box_shift[1] = 1 - box_shift[1]
        box_scale[1] *= -1

    box_trans = torch.stack([box_scale, box_shift], dim=-1)
    return box_trans, new_img2, new_mask2[0]


def random_crop_and_resize(new_img2, new_mask2, box_scale, box_shift):
    box_scale = box_scale.clone()
    box_shift = box_shift.clone()
    i, j, h, w = RandomResizedCrop.get_params(
        new_img2, scale=(0.5, 1.0), ratio=(1.0 / 4.0, 4.0 / 3.0)
    )
    orig_w = new_img2.shape[2]
    orig_h = new_img2.shape[1]
    new_img2 = TF.crop(new_img2, i, j, h, w)
    new_mask2 = TF.crop(new_mask2, i, j, h, w)
    new_img2 = torch.nn.functional.interpolate(
        new_img2.unsqueeze(0), (orig_h, orig_w), mode="bilinear"
    )[0]
    new_mask2 = torch.nn.functional.interpolate(
        new_mask2.unsqueeze(0).type(torch.float), (orig_h, orig_w), mode="nearest"
    )[0].type(torch.bool)
    i = i / (orig_h - 1)
    j = j / (orig_w - 1)
    f_h = orig_h / h
    f_w = orig_w / w
    box_shift[1] = (box_shift[1] - i) * f_h
    box_shift[0] = (box_shift[0] - j) * f_w
    box_scale[1] *= box_scale[1] * f_h
    box_scale[0] *= box_scale[0] * f_w
    box_scale[3] *= f_h
    box_scale[2] *= f_w
    return new_img2, new_mask2, box_scale, box_shift


class TvCocoDetection(VisionDataset):
    """`MS Coco Detection <http://mscoco.org/dataset/#detections-challenge2016>`_ Dataset.
    Args:
        root (string): Root directory where images are downloaded to.
        annFile (string): Path to json annotation file.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.ToTensor``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        transforms (callable, optional): A function/transform that takes input sample and its target as entry
            and returns a transformed version.
    """

    def __init__(
        self,
        root,
        annFile,
        transform=None,
        target_transform=None,
        transforms=None,
        cache_mode=False,
        local_rank=0,
        local_size=1,
    ):
        super(TvCocoDetection, self).__init__(
            root, transforms, transform, target_transform
        )
        from pycocotools.coco import COCO

        self.coco = COCO(annFile)
        self.ids = list(sorted(self.coco.imgs.keys()))
        self.cache_mode = cache_mode
        self.local_rank = local_rank
        self.local_size = local_size
        if cache_mode:
            self.cache = {}
            self.cache_images()

    def cache_images(self):
        self.cache = {}
        for index, img_id in zip(tqdm.trange(len(self.ids)), self.ids):
            if index % self.local_size != self.local_rank:
                continue
            path = self.coco.loadImgs(img_id)[0]["file_name"]
            with open(os.path.join(self.root, path), "rb") as f:
                self.cache[path] = f.read()

    def get_image(self, path):
        if self.cache_mode:
            if path not in self.cache.keys():
                with open(os.path.join(self.root, path), "rb") as f:
                    self.cache[path] = f.read()
            return Image.open(BytesIO(self.cache[path])).convert("RGB")
        return Image.open(os.path.join(self.root, path)).convert("RGB")

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: Tuple (image, target). target is the object returned by ``coco.loadAnns``.
        """
        coco = self.coco
        img_id = self.ids[index]
        ann_ids = coco.getAnnIds(imgIds=img_id)
        target = coco.loadAnns(ann_ids)

        path = coco.loadImgs(img_id)[0]["file_name"]

        img = self.get_image(path)
        if self.transforms is not None:
            img, target = self.transforms(img, target)

        return img, target

    def __len__(self):
        return len(self.ids)


def is_dist_avail_and_initialized():
    if not dist.is_available():
        return False
    if not dist.is_initialized():
        return False
    return True


def get_rank():
    if not is_dist_avail_and_initialized():
        return 0
    return dist.get_rank()


def is_main_process():
    return get_rank() == 0


def get_local_size():
    if not is_dist_avail_and_initialized():
        return 1
    return int(os.environ["LOCAL_SIZE"])


def get_local_rank():
    if not is_dist_avail_and_initialized():
        return 0
    return int(os.environ["LOCAL_RANK"])


class CocoDetection(TvCocoDetection):
    def __init__(
        self,
        img_folder,
        ann_file,
        transforms,
        return_masks,
        cache_mode=False,
        local_rank=0,
        local_size=1,
        no_cats=False,
        filter_pct=-1,
    ):
        super(CocoDetection, self).__init__(
            img_folder,
            ann_file,
            cache_mode=cache_mode,
            local_rank=local_rank,
            local_size=local_size,
        )
        self._transforms = transforms
        self.prepare = ConvertCocoPolysToMask(return_masks)
        self.no_cats = no_cats
        if filter_pct > 0:
            num_keep = float(len(self.ids)) * filter_pct
            self.ids = np.random.choice(
                self.ids, size=round(num_keep), replace=False
            ).tolist()

    def __getitem__(self, idx):
        img, target = super(CocoDetection, self).__getitem__(idx)
        image_id = self.ids[idx]
        target = {"image_id": image_id, "annotations": target}
        img, target = self.prepare(img, target)
        if self._transforms is not None:
            img, target = self._transforms(img, target)
        if self.no_cats:
            target["labels"][:] = 1
        return img, target


def convert_coco_poly_to_mask(segmentations, height, width):
    masks = []
    for polygons in segmentations:
        rles = coco_mask.frPyObjects(polygons, height, width)
        mask = coco_mask.decode(rles)
        if len(mask.shape) < 3:
            mask = mask[..., None]
        mask = torch.as_tensor(mask, dtype=torch.uint8)
        mask = mask.any(dim=2)
        masks.append(mask)
    if masks:
        masks = torch.stack(masks, dim=0)
    else:
        masks = torch.zeros((0, height, width), dtype=torch.uint8)
    return masks


class ConvertCocoPolysToMask(object):
    def __init__(self, return_masks=False):
        self.return_masks = return_masks

    def __call__(self, image, target):
        w, h = image.size

        image_id = target["image_id"]
        image_id = torch.tensor([image_id])

        anno = target["annotations"]

        anno = [obj for obj in anno if "iscrowd" not in obj or obj["iscrowd"] == 0]

        boxes = [obj["bbox"] for obj in anno]
        # guard against no boxes via resizing
        boxes, keep = preprocess_xywh_boxes(boxes, h, w)

        classes = [obj["category_id"] for obj in anno]
        classes = torch.tensor(classes, dtype=torch.int64)

        if self.return_masks:
            segmentations = [obj["segmentation"] for obj in anno]
            masks = convert_coco_poly_to_mask(segmentations, h, w)

        keypoints = None
        if anno and "keypoints" in anno[0]:
            keypoints = [obj["keypoints"] for obj in anno]
            keypoints = torch.as_tensor(keypoints, dtype=torch.float32)
            num_keypoints = keypoints.shape[0]
            if num_keypoints:
                keypoints = keypoints.view(num_keypoints, -1, 3)

        classes = classes[keep]
        if self.return_masks:
            masks = masks[keep]
        if keypoints is not None:
            keypoints = keypoints[keep]

        target = {}
        target["boxes"] = boxes
        target["labels"] = classes
        if self.return_masks:
            target["masks"] = masks
        target["image_id"] = image_id
        if keypoints is not None:
            target["keypoints"] = keypoints

        # for conversion to coco api
        area = torch.tensor([obj["area"] for obj in anno])
        iscrowd = torch.tensor(
            [obj["iscrowd"] if "iscrowd" in obj else 0 for obj in anno]
        )
        target["area"] = area[keep]
        target["iscrowd"] = iscrowd[keep]

        target["orig_size"] = torch.as_tensor([int(h), int(w)])
        target["size"] = torch.as_tensor([int(h), int(w)])

        return image, target


def preprocess_xywh_boxes(boxes, h, w):
    boxes = torch.as_tensor(boxes, dtype=torch.float32).reshape(-1, 4)
    boxes[:, 2:] += boxes[:, :2]
    boxes[:, 0::2].clamp_(min=0, max=w)
    boxes[:, 1::2].clamp_(min=0, max=h)
    keep = (boxes[:, 3] > boxes[:, 1]) & (boxes[:, 2] > boxes[:, 0])
    boxes = boxes[keep]
    return boxes, keep


def make_coco_transforms(image_set):

    normalize = Compose(
        [ToTensor(), Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])]
    )

    scales = [480, 512, 544, 576, 608, 640, 672, 704, 736, 768, 800]

    if image_set == "train":
        return Compose(
            [
                RandomHorizontalFlip(),
                RandomSelect(
                    RandomResize(scales, max_size=1333),
                    Compose(
                        [
                            RandomResize([400, 500, 600]),
                            RandomSizeCrop(384, 600),
                            RandomResize(scales, max_size=1333),
                        ]
                    ),
                ),
                normalize,
            ]
        )

    if image_set == "val":
        return Compose(
            [
                RandomResize([800], max_size=1333),
                normalize,
            ]
        )

    raise ValueError(f"unknown {image_set}")


def build(image_set, image_path, ann_path):
    # print('Debug10')
    # root = Path(coco_data_path)
    # assert root.exists(), f'provided COCO path {root} does not exist'
    mode = "instances"

    if image_set == "train":
        ann_file = os.path.join(ann_path, "instances_train2017.json")
    else:
        ann_file = os.path.join(ann_path, "instances_val2017.json")
    # print(img_folder)
    # print(ann_file)

    no_cats = False
    filter_pct = -1
    dataset = CocoDetection(
        image_path,
        ann_file,
        transforms=make_coco_transforms(image_set),
        return_masks=False,
        cache_mode=False,
        local_rank=get_local_rank(),
        local_size=get_local_size(),
        no_cats=no_cats,
        filter_pct=filter_pct,
    )
    return dataset


def collate_fn(batch):
    batch = list(zip(*batch))
    batch[0] = nested_tensor_from_tensor_list(batch[0])
    return tuple(batch)


def _max_by_axis(the_list):
    # type: (List[List[int]]) -> List[int]
    maxes = the_list[0]
    for sublist in the_list[1:]:
        for index, item in enumerate(sublist):
            maxes[index] = max(maxes[index], item)
    return maxes


def nested_tensor_from_tensor_list(tensor_list: List[Tensor]):
    # TODO make this more general
    if tensor_list[0].ndim == 3:
        # TODO make it support different-sized images
        max_size = _max_by_axis([list(img.shape) for img in tensor_list])
        # min_size = tuple(min(s) for s in zip(*[img.shape for img in tensor_list]))
        batch_shape = [len(tensor_list)] + max_size
        b, c, h, w = batch_shape
        dtype = tensor_list[0].dtype
        device = tensor_list[0].device
        tensor = torch.zeros(batch_shape, dtype=dtype, device=device)
        mask = torch.ones((b, h, w), dtype=torch.bool, device=device)
        for img, pad_img, m in zip(tensor_list, tensor, mask):
            pad_img[: img.shape[0], : img.shape[1], : img.shape[2]].copy_(img)
            m[: img.shape[1], : img.shape[2]] = False
    else:
        raise ValueError("not supported")
    return NestedTensor(tensor, mask)


class NestedTensor(object):
    def __init__(self, tensors, mask: Optional[Tensor]):
        self.tensors = tensors
        self.mask = mask

    def to(self, device, non_blocking=False):
        # type: (Device) -> NestedTensor # noqa
        cast_tensor = self.tensors.to(device, non_blocking=non_blocking)
        mask = self.mask
        if mask is not None:
            assert mask is not None
            cast_mask = mask.to(device, non_blocking=non_blocking)
        else:
            cast_mask = None
        return NestedTensor(cast_tensor, cast_mask)

    def record_stream(self, *args, **kwargs):
        self.tensors.record_stream(*args, **kwargs)
        if self.mask is not None:
            self.mask.record_stream(*args, **kwargs)

    def decompose(self):
        return self.tensors, self.mask

    def __repr__(self):
        return str(self.tensors)


def rescale_bboxes(out_bbox, size):
    img_w, img_h = size
    b = box_cxcywh_to_xyxy(out_bbox)
    b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32).to(out_bbox)
    return b


def plot_prediction(image, boxes, logits, ax=None, plot_prob=True):
    bboxes_scaled0 = rescale_bboxes(boxes[0], list(image.shape[2:])[::-1])
    probas = logits.softmax(-1)[0, :, :-1]
    keep = probas.max(-1).values > 0.001
    if ax is None:
        ax = plt.gca()
    plot_results(
        image[0].permute(1, 2, 0).detach().cpu().numpy(),
        probas[keep],
        bboxes_scaled0[keep],
        ax,
        plot_prob=plot_prob,
    )


def plot_results(pil_img, prob, boxes, ax, plot_prob=True, norm=True):
    from matplotlib import pyplot as plt

    image = plot_image(ax, pil_img, norm)
    if prob is not None and boxes is not None:
        for p, (xmin, ymin, xmax, ymax) in zip(prob, boxes.tolist()):
            ax.add_patch(
                plt.Rectangle(
                    (xmin, ymin),
                    xmax - xmin,
                    ymax - ymin,
                    fill=False,
                    color="r",
                    linewidth=1,
                )
            )
            if plot_prob:
                text = f"{p:0.2f}"
                ax.text(
                    xmin,
                    ymin,
                    text,
                    fontsize=15,
                    bbox=dict(facecolor="yellow", alpha=0.5),
                )
    ax.grid("off")


def plot_image(ax, img, norm):
    if norm:
        img = img * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])
        img = img * 255
    img = img.astype("uint8")
    ax.imshow(img)


@torch.no_grad()
def accuracy(output, target, topk=(1,)):
    """Computes the precision@k for the specified values of k"""
    if target.numel() == 0:
        return [torch.zeros([], device=output.device)]
    maxk = max(topk)
    batch_size = target.size(0)

    _, pred = output.topk(maxk, 1, True, True)
    pred = pred.t()
    correct = pred.eq(target.view(1, -1).expand_as(pred))

    res = []
    for k in topk:
        correct_k = correct[:k].view(-1).float().sum(0)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res
