import os
from pathlib import Path
from functools import partial
import xml.etree.ElementTree as ET
import math
import sys
import json

try:
    from fastai.vision.data import imagenet_stats, ImageList, bb_pad_collate
    from fastai.vision.transform import crop, rotate, dihedral_affine, brightness, contrast, skew, rand_zoom, get_transforms, flip_lr
    from fastai.vision import ImageDataBunch
    from fastai.torch_core import data_collate
    import torch
    from .models._ssd_utils import SSDObjectItemList
    from .models._unet_utils import ArcGISSegmentationItemList
    HAS_FASTAI = True
except:
    HAS_FASTAI = False


def _raise_fastai_import_error():
    raise Exception('This module requires fastai, PyTorch and torchvision as its dependencies. Install it using "conda install -c pytorch -c fastai fastai pytorch torchvision"')


def _bb_pad_collate(samples, pad_idx=0):
    "Function that collect `samples` of labelled bboxes and adds padding with `pad_idx`."
    if isinstance(samples[0][1], int):
        return data_collate(samples)
    max_len = max([len(s[1].data[1]) for s in samples])
    bboxes = torch.zeros(len(samples), max_len, 4)
    labels = torch.zeros(len(samples), max_len).long() + pad_idx
    imgs = []
    for i,s in enumerate(samples):
        imgs.append(s[0].data[None])
        bbs, lbls = s[1].data

        if not (bbs.nelement() == 0):
            bboxes[i,-len(lbls):] = bbs
            labels[i,-len(lbls):] = torch.tensor(lbls, device=bbs.device).long()
    return torch.cat(imgs,0), (bboxes,labels)    


def _get_bbox_classes(xmlfile, class_mapping):
    tree = ET.parse(xmlfile)
    xmlroot = tree.getroot()
    bboxes = []
    classes = []
    for tag_obj in xmlroot.findall('object'):
        bnd_box = tag_obj.find('bndbox')
        xmin, ymin, xmax, ymax = float(bnd_box.find('xmin').text), \
                                 float(bnd_box.find('ymin').text), \
                                 float(bnd_box.find('xmax').text), \
                                 float(bnd_box.find('ymax').text)
        bboxes.append([ymin, xmin, ymax, xmax])
        data_class_text = tag_obj.find('name').text

        if data_class_text.isnumeric():
            data_class_mapping = class_mapping[data_class_text] if class_mapping.get(data_class_text) else class_mapping[int(data_class_text)]
        else:
            data_class_mapping = class_mapping[data_class_text]

        classes.append(data_class_mapping)

    return [bboxes, classes]


def _get_bbox_lbls(imagefile, class_mapping):
    xmlfile = imagefile.parents[1] / 'labels' / imagefile.name.replace('{ims}'.format(ims=imagefile.suffix), '.xml')
    return _get_bbox_classes(xmlfile, class_mapping)


def _get_lbls(imagefile, class_mapping):
    xmlfile = imagefile.parents[1] / 'labels' / imagefile.name.replace('{ims}'.format(ims=imagefile.suffix), '.xml')
    return _get_bbox_classes(xmlfile, class_mapping)[1][0]


def _check_esri_files(path):
    if os.path.exists(path / 'esri_model_definition.emd') \
        and os.path.exists(path / 'map.txt') \
            and os.path.exists(path / 'esri_accumulated_stats.json'):
        return True

    return False


def _get_class_mapping(path):
    class_mapping = {}
    for xmlfile in os.listdir(path):
        if not xmlfile.endswith('.xml'):
            continue
        tree = ET.parse(os.path.join(path, xmlfile))
        xmlroot = tree.getroot()
        for tag_obj in xmlroot.findall('object'):
            class_mapping[tag_obj.find('name').text] = tag_obj.find('name').text

    return class_mapping


def prepare_data(path, class_mapping=None, chip_size=224, val_split_pct=0.1, batch_size=64, transforms=None, collate_fn=_bb_pad_collate, seed=42, dataset_type=None, resize_to=None):
    """
    Prepares a Fast.ai DataBunch from the exported Pascal VOC image chips
    exported by Export Training Data tool in ArcGIS Pro or Image Server.
    This DataBunch consists of training and validation DataLoaders with the
    specified transformations, chip size, batch size, split percentage.

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    path                    Required string. Path to data directory.
    ---------------------   -------------------------------------------
    class_mapping           Optional dictionary. Mapping from id to
                            its string label.
    ---------------------   -------------------------------------------
    chip_size               Optional integer. Size of the image to train the
                            model.
    ---------------------   -------------------------------------------
    val_split_pct           Optional float. Percentage of training data to keep
                            as validation.
    ---------------------   -------------------------------------------
    batch_size              Optional integer. Batch size for mini batch gradient
                            descent (Reduce it if getting CUDA Out of Memory
                            Errors).
    ---------------------   -------------------------------------------
    transforms              Optional tuple. Fast.ai transforms for data
                            augmentation of training and validation datasets
                            respectively (We have set good defaults which work
                            for satellite imagery well). If transforms is set
                            to `False` no transformation will take place and 
                            `chip_size` parameter will also not take effect.
    ---------------------   -------------------------------------------
    collate_fn              Optional function. Passed to PyTorch to collate data
                            into batches(usually default works).
    ---------------------   -------------------------------------------
    seed                    Optional integer. Random seed for reproducible
                            train-validation split.
    ---------------------   -------------------------------------------
    dataset_type            Optional string. `prepare_data` function will infer 
                            the `dataset_type` on its own if it contains a 
                            map.txt file. If the path does not contain the 
                            map.txt file pass either of 'PASCAL_VOC_rectangles', 
                            'RCNN_Masks' and 'Classified_Tiles'                    
    ---------------------   -------------------------------------------
    resize_to            Optional integer. Resize the image to given size.
    =====================   ===========================================

    :returns: fastai DataBunch object
    """

    if not HAS_FASTAI:
        _raise_fastai_import_error()

    if type(path) is str:
        path = Path(path)

    databunch_kwargs = {'num_workers':0} if sys.platform == 'win32' else {}

    has_esri_files = _check_esri_files(path)
    alter_class_mapping = False
    color_mapping = None

    if dataset_type is None and not has_esri_files:
        raise Exception("Could not infer dataset type.")

    if dataset_type != "Imagenet" and has_esri_files:
        stats_file = path / 'esri_accumulated_stats.json'
        with open(stats_file) as f:
            stats = json.load(f)
            dataset_type = stats['MetaDataMode']

        with open(path / 'map.txt') as f:
            line = f.readline()

        right = line.split()[1].split('.')[-1].lower()

        json_file = path / 'esri_model_definition.emd'
        with open(json_file) as f:
            emd = json.load(f)

        if class_mapping is None:
            try:
                class_mapping = {i['Value']: i['Name'] for i in emd['Classes']}
            except KeyError:
                class_mapping = {i['ClassValue']: i['ClassName'] for i in emd['Classes']}

        color_mapping = {(i.get('Value') or i.get('ClassValue')): i['Color'] for i in emd.get('Classes', [])}
    elif dataset_type == 'PASCAL_VOC_rectangles' and not has_esri_files:
        if class_mapping is None:
            class_mapping = _get_class_mapping(path / 'labels')
            alter_class_mapping = True

    if dataset_type in ['RCNN_Masks', 'Classified_Tiles']:

        def get_y_func(x, ext=right):
            return x.parents[1] / 'labels' / (x.stem + '.{}'.format(ext))
        
        src = (ArcGISSegmentationItemList.from_folder(path/'images')
                .split_by_rand_pct(val_split_pct, seed=seed)
                .label_from_func(get_y_func, classes=['NoData'] + list(class_mapping.values()), class_mapping=class_mapping, color_mapping=color_mapping)) # TODO : Handel NoData case

        if transforms is None:
            transforms = get_transforms(flip_vert=True,
                                        max_rotate=90.,
                                        max_zoom=3.0,
                                        max_lighting=0.5)

        data = (src.transform(transforms, size=chip_size, tfm_y=True)
                .databunch(bs=batch_size, **databunch_kwargs)
                .normalize(imagenet_stats))
    elif dataset_type == 'PASCAL_VOC_rectangles':
        get_y_func = partial(_get_bbox_lbls, class_mapping=class_mapping)

        src = (SSDObjectItemList.from_folder(path/'images')
                .split_by_rand_pct(val_split_pct, seed=seed)
                .label_from_func(get_y_func))

        if transforms is None:
            ranges = (0,1)
            train_tfms = [crop(size=chip_size, p=1., row_pct=ranges, col_pct=ranges), dihedral_affine(), brightness(change=(0.4, 0.6)), contrast(scale=(0.75, 1.5)), rand_zoom(scale=(0.75, 1.5))]
            val_tfms = [crop(size=chip_size, p=1., row_pct=0.5, col_pct=0.5)]
            transforms = (train_tfms, val_tfms)

        kwargs_transforms = {
            'tfm_y': True
        }
        if resize_to is not None:
            kwargs_transforms['size'] = resize_to

        data = (src
                .transform(transforms, **kwargs_transforms)
                .databunch(bs=batch_size, collate_fn=collate_fn, **databunch_kwargs)
                .normalize(imagenet_stats))
        
    elif dataset_type == 'Labeled_Tiles':
        get_y_func = partial(_get_lbls, class_mapping=class_mapping)

        src = (ImageList.from_folder(path/'images')
                .split_by_rand_pct(val_split_pct, seed=42)
                .label_from_func(get_y_func))

        if transforms is None:
            ranges = (0, 1)
            train_tfms = [
                rotate(degrees=30, p=0.5),
                crop(size=chip_size, p=1., row_pct=ranges, col_pct=ranges),
                dihedral_affine(), brightness(change=(0.4, 0.6)), contrast(scale=(0.75, 1.5)),
            ]
            val_tfms = [crop(size=chip_size, p=1.0, row_pct=0.5, col_pct=0.5)]
            transforms = (train_tfms, val_tfms)

        data = (src
                .transform(transforms, size=chip_size)
                .databunch(bs=batch_size, **databunch_kwargs)
                .normalize(imagenet_stats))

    elif dataset_type == 'Imagenet':
        if transforms is None:
            train_tfms = [
                rotate(degrees=30, p=0.5),
                flip_lr(),
                brightness(change=(0.4, 0.6)),
                contrast(scale=(0.75, 1.5))
            ]
            val_tfms = []
            transforms = (train_tfms, val_tfms)  

        data = ImageDataBunch.from_folder(path, ds_tfms=transforms, size=chip_size, **databunch_kwargs).normalize(imagenet_stats)
    else:
        raise NotImplementedError('Unknown dataset_type="{}".'.format(dataset_type))    

    data.chip_size = data.x[0].shape[-1] if transforms is False else chip_size
    if alter_class_mapping:
        new_mapping = {}
        for i, class_name in enumerate(class_mapping.keys()):
            new_mapping[i+1] = class_name
        class_mapping = new_mapping

    data.class_mapping = class_mapping
    data.color_mapping = color_mapping
    show_batch_func = data.show_batch
    show_batch_func = partial(show_batch_func, rows=min(int(math.sqrt(batch_size)), 5))
    data.show_batch = show_batch_func
    data.orig_path = path
    data.resize_to = resize_to
    
    return data
