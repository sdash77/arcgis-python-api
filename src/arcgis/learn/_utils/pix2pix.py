from fastai.vision import ItemBase, ItemList, Tensor, ImageList, Tuple, Path, get_transforms, random, open_image, Image, math, plt, torch, Learner, partial, optim, ifnone

import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import torch
from scipy import linalg
from torch.nn.functional import adaptive_avg_pool2d
import numpy as np
from .._utils.cyclegan import get_activations, InceptionV3

class ImageTuple(ItemBase):
    def __init__(self, img1, img2):
        self.img1,self.img2 = img1,img2
        self.obj,self.data = (img1,img2),[-1+2*img1.data,-1+2*img2.data]
        self.data2 = [-1+2*img2.data,-1+2*img1.data]
        self.shape = img1.shape
    
    def apply_tfms(self, tfms, **kwargs):
        self.img1 = self.img1.apply_tfms(tfms, **kwargs)
        self.img2 = self.img2.apply_tfms(tfms, **kwargs)
        return self
    
    def to_one(self): 
        return Image(0.5+torch.cat(self.data,2)/2)
    def to_one_pred(self): 
        return Image(0.5+(self.data2[0])/2)
    
    def __repr__(self):
         return f'{self.__class__.__name__}{(self.img1.shape, self.img2.shape)}'

class TargetTupleList(ItemList):
    def reconstruct(self, t:Tensor): 
        if len(t.size()) == 0: return t
        return ImageTuple(Image(t[0]/2+0.5),Image(t[1]/2+0.5))

class ImageTupleList2(ImageList):
    _label_cls=TargetTupleList
    def __init__(self, items, itemsB=None, itemsB_valid=None, **kwargs):
        self.itemsB = itemsB
        self.itemsB_valid = itemsB_valid
        super().__init__(items, **kwargs)
    
    def new(self, items, **kwargs):
        return super().new(items, itemsB=self.itemsB, itemsB_valid=self.itemsB_valid, **kwargs)
    
    def get(self, i):
        
        if len(self.items) == len(self.itemsB):
            img1 = super().get(i)
            fn = self.itemsB[i]
        else:
            img1 = super().get(i)
            fn = self.itemsB_valid[i]
        return ImageTuple(img1, open_image(fn))
    
    def reconstruct(self, t:Tensor): 
        return ImageTuple(Image(t[0]/2+0.5),Image(t[1]/2+0.5))
    
    @classmethod
    def from_folders(cls, path, folderA, folderB, **kwargs):
        itemsB = ImageList.from_folder(path/folderB).items
        res = super().from_folder(path/folderA, itemsB=itemsB, itemsB_valid =itemsB, **kwargs)
        res.path = path
        return res
    
    def split_by_idxs(self, train_idx, valid_idx):
        "Split the data between `train_idx` and `valid_idx`."
        self.itemsB_valid = self.itemsB_valid[valid_idx]
        self.itemsB = self.itemsB[train_idx]
        return self.split_by_list(self[train_idx], self[valid_idx])
    
    def show_xys(self, xs, ys, figsize:Tuple[int,int]=(12,6), **kwargs):
        "Show the `xs` and `ys` on a figure of `figsize`. `kwargs` are passed to the show method."
        rows = int(math.sqrt(len(xs)))
        fig, axs = plt.subplots(rows,rows,figsize=figsize)
        for i, ax in enumerate(axs.flatten() if rows > 1 else [axs]):
            xs[i].to_one().show(ax=ax, **kwargs)
        plt.tight_layout()
    
    def show_xyzs(self, xs, ys, zs, figsize:Tuple[int,int]=None, **kwargs):
        """Show `xs` (inputs), `ys` (targets) and `zs` (predictions) on a figure of `figsize`.
        `kwargs` are passed to the show method."""
        
        figsize = ifnone(figsize, (12,3*len(xs)))
        fig,axs = plt.subplots(len(xs), 2, figsize=figsize)
        ax=axs[1,0]
        fig.suptitle('Ground truth / Predictions', weight='bold', size=14)
        for i,(x,z) in enumerate(zip(xs,zs)):
            x.to_one().show(ax=axs[i,0], **kwargs)
            z.to_one_pred().show(ax=axs[i,1], **kwargs)

def calculate_activation_statistics(batch_size, data_len, batch_list):
    act = get_activations(batch_size, data_len, batch_list)
    mu = np.mean(act, axis=0)
    sigma = np.cov(act, rowvar=False)
    return mu, sigma