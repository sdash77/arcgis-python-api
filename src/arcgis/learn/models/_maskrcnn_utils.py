from fastai.vision import ImageSegment, Image
from fastai.vision.image import open_image, show_image, pil2tensor
from fastai.vision.data import SegmentationProcessor, ImageList
from fastai.layers import CrossEntropyFlat
from fastai.callbacks import LearnerCallback
import torch
import warnings
import PIL
import numpy as np
from skimage import io
import matplotlib.pyplot as plt

class ArcGISImageSegment(Image):
    "Support applying transforms to segmentation masks data in `px`."
    def __init__(self, x, cmap=None, norm=None):
        super(ArcGISImageSegment, self).__init__(x)
        self.cmap = cmap
        self.mplnorm = norm
        self.type = np.unique(x)

    def lighting(self, func, *args, **kwargs):
        return self

    def refresh(self):
        self.sample_kwargs['mode'] = 'nearest'
        return super().refresh()

    @property
    def data(self):
        "Return this image pixels as a `LongTensor`."
        return self.px.long()

    def show(self, ax = None, figsize = (3,3), title = None, hide_axis = True, cmap='tab20', alpha = 0.5, **kwargs):

        if ax is None: fig,ax = plt.subplots(figsize=figsize)
        masks = self.data[0].numpy()
        for i in range(1, self.data.shape[0]):
            max_unique = np.max(np.unique(masks))
            mask = np.where(self.data[i]>0, self.data[i] + max_unique, self.data[i])
            masks += mask
        ax.imshow(masks, cmap=cmap, alpha=alpha, **kwargs)
        if hide_axis: ax.axis('off')
        if title: ax.set_title(title)


def is_no_color(color_mapping):
    if isinstance(color_mapping, dict):
        color_mapping = list(color_mapping.values())
    return (np.array(color_mapping) == [-1., -1., -1.]).any()

class ArcGISSegmentationLabelList(ImageList):
    "`ItemList` for segmentation masks."
    _processor = SegmentationProcessor
    def __init__(self, items, chip_size, classes=None, class_mapping=None, color_mapping=None, **kwargs):
        super().__init__(items, **kwargs)
        self.class_mapping = class_mapping
        self.color_mapping = color_mapping
        self.copy_new.append('classes')
        self.classes, self.loss_func = classes, CrossEntropyFlat(axis=1)
        self.chip_size = chip_size
        self.inverse_class_mapping = {}
        for k, v in self.class_mapping.items():
            self.inverse_class_mapping[v] = k
        if is_no_color(list(color_mapping.values())):
            self.cmap = 'tab20'  ## compute cmap from palette
            import matplotlib as mpl
            bounds = list(color_mapping.keys())
            if len(bounds) < 3: # Two handle two classes i am adding one number to the classes which is not already in bounds
                bounds = bounds + [max(bounds)+1]
            self.mplnorm = mpl.colors.BoundaryNorm(bounds, len(bounds))
        else:
            import matplotlib as mpl
            bounds = list(color_mapping.keys())
            if len(bounds) < 3: # Two handle two classes i am adding one number to the classes which is not already in bounds
                bounds = bounds + [max(bounds)+1]
            self.cmap = mpl.colors.ListedColormap(np.array(list(color_mapping.values()))/255)
            self.mplnorm = mpl.colors.BoundaryNorm(bounds, self.cmap.N)

        if len(color_mapping.keys()) == 1:
            self.cmap = 'tab20'
            self.mplnorm = None

    def open(self, fn):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning) # EXIF warning from TiffPlugin
            if len(fn) != 0:
                img_shape = io.imread(fn[0]).shape
            else:
                labeled_mask = torch.zeros((len(self.class_mapping), self.chip_size, self.chip_size))
                return ArcGISImageSegment(labeled_mask, cmap=self.cmap, norm=self.mplnorm)
            k = 0

            labeled_mask = np.zeros((1, img_shape[0], img_shape[1]))

            for j in range(len(self.class_mapping)):

                if k < len(fn):
                    lbl_name = int(self.inverse_class_mapping[fn[k].parent.name])
                else:
                    lbl_name = len(self.class_mapping) + 2
                if lbl_name == j+1:                    
                    img = io.imread(fn[k])
                    k = k + 1
                    if len(img.shape)==3:
                        img = img.transpose(2,0,1)
                        img_mask = img[0]
                        for i in range(1, img.shape[0]):
                            max_unique = np.max(np.unique(img_mask))
                            img_i = np.where(img[i]>0, img[i] + max_unique, img[i])
                            img_mask += img_i
                        img_mask = np.expand_dims(img_mask, axis = 0)
                    else:
                        img_mask = np.expand_dims(img, axis = 0)
                else:
                    img_mask = np.zeros((1, img_shape[0], img_shape[1]))
                labeled_mask = np.append(labeled_mask, img_mask, axis = 0)
            labeled_mask = labeled_mask[1:,:,:]
            labeled_mask = torch.Tensor(list(labeled_mask))
        return ArcGISImageSegment(labeled_mask, cmap=self.cmap, norm=self.mplnorm)

    def reconstruct(self, t): 
        return ArcGISImageSegment(t, cmap=self.cmap, norm=self.mplnorm)

class ArcGISInstanceSegmentationItemList(ImageList):
    "`ItemList` suitable for segmentation tasks."
    _label_cls, _square_show_res = ArcGISSegmentationLabelList, False

def mask_rcnn_loss(loss_value, *args):

    final_loss = 0.
    for i in loss_value.values():
        if not (torch.isnan(i) or torch.isinf(i)):
            final_loss += i
            
    return final_loss

class train_callback(LearnerCallback):

    def __init__(self, learn):
        super().__init__(learn)
   
    def on_batch_begin(self, last_input, last_target, **kwargs):
        "Handle new batch `xb`,`yb` in `train` or validation."

        target_list = []
        for i in range(len(last_target)):

            boxes =  []
            masks = np.zeros((1, last_target[i].shape[1], last_target[i].shape[2]))
            labels = []
            for j in range(last_target[i].shape[0]):

                mask = np.array(last_target[i].data[j])
                obj_ids = np.unique(mask)

                if len(obj_ids)==1:
                    continue

                obj_ids = obj_ids[1:]
                mask_j = mask == obj_ids[:, None, None]
                num_objs = len(obj_ids)
                for k in range(num_objs):
                    pos = np.where(mask_j[k])
                    xmin = np.min(pos[1])
                    xmax = np.max(pos[1])
                    ymin = np.min(pos[0])
                    ymax = np.max(pos[0])
                    boxes.append([xmin, ymin, xmax, ymax])

                masks = np.append(masks, mask_j, axis = 0)
                labels_j = torch.ones((num_objs,), dtype=torch.int64)
                labels_j = labels_j*(j+1)
                labels.append(labels_j)
            
            if(masks.shape[0]==1): # if no object in image
                masks[0,50:51,50:51] = 1
                labels = torch.tensor([0])
                boxes = torch.tensor([[50.,50.,51.,51.]])
            else:
                labels = torch.cat(labels)
                boxes = torch.as_tensor(boxes, dtype=torch.float32)
                masks = masks[1:,:,:]
            masks = torch.as_tensor(masks, dtype=torch.uint8)
            target = {}
            target["boxes"] = boxes.cuda()
            target["labels"] = labels.cuda()
            target["masks"] = masks.cuda()
            target_list.append(target)

        self.learn.model.train()
        last_input = [last_input, target_list]
        last_target = [torch.tensor([1]) for i in last_target]
        return {'last_input':last_input, 'last_target':last_target}            