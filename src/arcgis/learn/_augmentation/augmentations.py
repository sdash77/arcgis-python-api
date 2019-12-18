#!/usr/bin/env python
# coding: utf-8
import torch
from torch import nn
import random



# batch Flip Store
def do_nothing(tensor_batch):
    return tensor_batch
    
def vertical_flip(tensor_batch):
    return torch.flip(tensor_batch, dims=(-2,))

def horizontal_flip(tensor_batch):
    return torch.flip(tensor_batch, dims=(-1,))

def dihedral_flip(tensor_batch):
    return torch.flip(tensor_batch, [-2,-1])
    
## RandomFlip
class RandomFlip(nn.Module):
    def __init__(self, transforms=None, dihedral=True, nothing=True, do_y=True):
        super(RandomFlip, self).__init__()
        self.do_y = do_y
        if transforms is not None:
            self.transforms = transforms
        else:
            self.transforms = [
                vertical_flip,
                horizontal_flip
            ]
            if nothing:
                self.transforms.append(do_nothing)
            if dihedral:
                self.transforms.append(dihedral_flip)            
            self.refresh()
    
    def forward(self, tensor_batch, transforms=None, return_transforms=True):
        # Get Transforms
        if transforms is None:
            transforms = self.transforms
        
        transform_mask = torch.arange(tensor_batch.shape[0]) % len(self.transforms)
        tensor_batch_return = tensor_batch.clone()
        for i in range(0, len(self.transforms)):
            tensor_batch_return[transform_mask == i] = self.transforms[i](tensor_batch_return[transform_mask == i])
        
        if return_transforms:
            return tensor_batch_return, self.transforms
        return tensor_batch_return
    
    def refresh(self):
        random.shuffle(self.transforms)
    
## Crop
class Crop(nn.Module):
    def __init__(self, target_size: int, shift_factor=0.5, do_y=True):
        super(Crop, self).__init__()
        self.do_y = do_y
        self.target_size = target_size
        self.shift_factor = shift_factor
        
    def forward(self, tensor_batch: torch.tensor, return_transforms=False):
        if return_transforms == True:
            raise Exception('return_transforms should be always false for Non Random Transforms')
        shift = round((tensor_batch.shape[-1] - self.target_size) * self.shift_factor )
        return tensor_batch[:, :, shift:shift + self.target_size, shift:shift + self.target_size].clone()
    
## Center Crop
class CenterCrop(Crop):
    def __init__(self, target_size: int, do_y=True):
        super(CenterCrop, self).__init__(target_size, shift_factor=0.5, do_y=do_y)
        

## Random Crop
class RandomCrop(nn.Module):
    def __init__(self, target_size: int, shift_factor: float=None, do_y=True):
        super(RandomCrop, self).__init__()
        self.do_y = do_y
        self.target_size = target_size
        self.refresh()
        
    def forward(self, tensor_batch: torch.tensor, return_transforms=True):
        shift = torch.round((tensor_batch.shape[-1] - self.target_size) * self.shift_factor).long()
        print(shift)
        return tensor_batch[:, :, shift:shift + self.target_size, shift:shift + self.target_size].clone()
    
    def refresh(self):
        self.shift_factor = torch.rand(1)[0]
        

## Random Resized Crop
class RandomResizedCrop(nn.Module):
    def __init__(self, max_scale_factor: float=.2, target_size=None, n_transforms: int=4, do_y=True):
        super(RandomResizedCrop, self).__init__()
        self.do_y = do_y
        self.max_scale_factor = max_scale_factor
        self.n_transforms = n_transforms
        self.target_size = target_size
        self.refresh()
        
    def forward(self, tensor_batch, transforms=None, return_transforms=True):
        # Get Transforms
        if transforms is None:
            transforms = self.transforms
        
        orig_size = tensor_batch.shape[-1]
        target_size = self.target_size
        if target_size is None:
            target_size = orig_size
        transform_mask = torch.arange(tensor_batch.shape[0]) % len(self.transforms)
        tensor_batch_return = torch.zeros([*tensor_batch.shape[:-2], target_size, target_size]).to(tensor_batch)
        for i in range(0, len(self.transforms)):
            transform = self.transforms[i].item()
            scale_factor = transform * self.max_scale_factor
            scaled_size = round(orig_size*(1+scale_factor))
            scaled = torch.nn.functional.interpolate(tensor_batch[transform_mask == i].float(), scaled_size)
            shift = round((scaled_size - target_size) * transform)
            #print(shift)
            tensor_batch_return[transform_mask == i] = scaled[:, :, shift:shift + target_size, shift:shift + target_size].to(tensor_batch_return)
            
        if return_transforms:
            return tensor_batch_return, self.transforms
        return tensor_batch_return
    
    def refresh(self):
        self.transforms = torch.rand((self.n_transforms,))
        random.shuffle(self.transforms)


## Random Rotate
class RandomRotate(nn.Module):
    def __init__(self, max_angle: int=20, n_transforms: int=4, center: tuple=None, do_y=True):
        super(RandomRotate, self).__init__()
        self.do_y = do_y
        self.max_angle = max_angle
        self.n_transforms = n_transforms
        self.refresh()
        if center is not None:
            self.center = center
        else:
            self.center = (0.5, 0.5)
        
    def forward(self, tensor_batch, center=None, transforms=None, return_transforms=True):
        # Get Transforms
        if transforms is None:
            transforms = self.transforms
            
        # Get center
        if center is None:
            center = self.center
        orig_size = tensor_batch.shape[-1]
        c_x = orig_size*self.center[0]
        c_y = orig_size*self.center[0]
        
        # Get Indexes
        indexes = torch.stack(torch.meshgrid([torch.arange(0, orig_size), torch.arange(0, orig_size)]), dim=-1).float()
        indexes[:, :, 1]-=c_x
        indexes[:, :, 0]-=c_y
        
        transform_mask = torch.arange(tensor_batch.shape[0]) % len(self.transforms)
        tensor_batch_return = torch.zeros(tensor_batch.shape).to(tensor_batch)
        for i in range(0, len(self.transforms)):
            
            # Get rotation matrix
            angle = self.transforms[i] * self.max_angle * 22 / (7 *180)
            rotation_matrix = torch.tensor(
                [
                    [
                        torch.cos(angle), -torch.sin(angle)
                    ],
                    [
                        torch.sin(angle), torch.cos(angle)
                    ]    
                ]
            )
            
            # Rotate Tensor
            rotated_indexes = (rotation_matrix @ indexes.unsqueeze(-1)).squeeze()
            rotated_indexes[:, :, 1]+=c_x
            rotated_indexes[:, :, 0]+=c_y    
            no_data_mask = ( (rotated_indexes < 0) + (rotated_indexes >= orig_size) ).any(dim=-1) # Get mask to blacken
            rotated_indexes = torch.clamp(rotated_indexes, 0, orig_size-1).round().long()
            rows = rotated_indexes[:, :, 0]
            cols = rotated_indexes[:, :, 1]
            a = tensor_batch[transform_mask == i][:, :, rows, cols]
            a[:, :, no_data_mask] = 0 # Make the out of range values black 
            tensor_batch_return[transform_mask == i] = a
    
        if return_transforms:
            return tensor_batch_return, self.transforms
        return tensor_batch_return
    
    def refresh(self):
        self.transforms = ( torch.rand((self.n_transforms,)) - .5) * 2
        

## Random Resized Rotate
class RandomResizedRotate(nn.Module):
    def __init__(self, max_angle: int=15, n_transforms: int=4, center: tuple=None, do_y=True):
        super(RandomResizedRotate, self).__init__()
        self.do_y = do_y
        self.max_angle = max_angle
        self.n_transforms = n_transforms
        self.refresh()
        if center is not None:
            self.center = center
        else:
            self.center = (0.5, 0.5)
        
    def forward(self, tensor_batch, center=None, transforms=None, return_transforms=True):
        # Get Transforms
        if transforms is None:
            transforms = self.transforms
            
        # Get center
        if center is None:
            center = self.center
        orig_size = tensor_batch.shape[-1]
        c_x = orig_size*self.center[0]
        c_y = orig_size*self.center[0]
        
        # Get Indexes
        indexes = torch.stack(torch.meshgrid([torch.arange(0, orig_size), torch.arange(0, orig_size)]), dim=-1).float()
        indexes[:, :, 1]-=c_x
        indexes[:, :, 0]-=c_y
        
        transform_mask = torch.arange(tensor_batch.shape[0]) % len(self.transforms)
        tensor_batch_return = torch.zeros(tensor_batch.shape).to(tensor_batch)
        for i in range(0, len(self.transforms)):
            
            # Get rotation matrix
            angle = self.transforms[i] * self.max_angle * 22 / (7 *180)
            rotation_matrix = torch.tensor(
                [
                    [
                        torch.cos(angle), -torch.sin(angle)
                    ],
                    [
                        torch.sin(angle), torch.cos(angle)
                    ]    
                ]
            )
            
            # Rotate Tensor
            rotated_indexes = (rotation_matrix @ indexes.unsqueeze(-1)).squeeze()
            rotated_indexes[:, :, 1]+=c_x
            rotated_indexes[:, :, 0]+=c_y    
            #no_data_mask = ( (rotated_indexes < 0) + (rotated_indexes >= orig_size) ).any(dim=-1) # Get mask to blacken
            rotated_indexes = torch.clamp(rotated_indexes, 0, orig_size-1).round().long()
            rows = rotated_indexes[:, :, 0]
            cols = rotated_indexes[:, :, 1]
            tensor_batch_return[transform_mask == i] = tensor_batch[transform_mask == i][:, :, rows, cols]
            #tensor_batch_return[transform_mask == i][:, :, no_data_mask] = 0 # Make the out of range values black
           
            # Crop it
            angle = self.transforms[i].abs() * self.max_angle * 22 / (7 *180)
            crop_size = torch.round(orig_size / ( torch.sin(angle) + torch.cos(angle) )).long()
            shift = torch.round((orig_size - crop_size).float() * .5 ).long()
            croped = tensor_batch_return[transform_mask == i][:, :, shift:shift + crop_size, shift:shift + crop_size]
            
            # Resize it Back to original size
            tensor_batch_return[transform_mask == i] = torch.nn.functional.interpolate(croped, orig_size)
            
    
        if return_transforms:
            return tensor_batch_return, self.transforms
        return tensor_batch_return
    
    def refresh(self):
        self.transforms = ( torch.rand((self.n_transforms,)) - .5) * 2
        


## Lighting Transforms

## Random Brightness
class RandomBrightness(nn.Module):
    def __init__(self, max_factor: float=.4, n_transforms: int=10, do_y=False):
        super(RandomBrightness, self).__init__()
        self.do_y = do_y
        self.max_factor = max_factor
        self.n_transforms = n_transforms
        self.refresh()
        
    def forward(self, tensor_batch, transforms=None, return_transforms=True):
        # Get Transforms
        if transforms is None:
            transforms = self.transforms
        
        transform_mask = torch.arange(tensor_batch.shape[0]) % 2
        transform_mask[transform_mask==0]-=1
        brightness_factors = 1 + torch.linspace(*self.transforms, steps=tensor_batch.shape[0])*transform_mask.float()   
        tensor_batch_return = tensor_batch * brightness_factors.view(-1, 1, 1, 1).to(tensor_batch)
    
        if return_transforms:
            return tensor_batch_return, self.transforms
        return tensor_batch_return
    
    def refresh(self):
        self.transforms = torch.rand((2,)) * self.max_factor


## Random Contrast
class RandomContrast(nn.Module):
    def __init__(self, max_factor: float=.3, n_transforms: int=10, do_y=False):
        super(RandomContrast, self).__init__()
        self.do_y = do_y
        self.max_factor = max_factor
        self.n_transforms = n_transforms
        self.refresh()
        
    def forward(self, tensor_batch, transforms=None, return_transforms=True):
        # Get Transforms
        if transforms is None:
            transforms = self.transforms

        transform_mask = torch.arange(tensor_batch.shape[0]) % 2
        transform_mask[transform_mask==0]-=1
        contrast_factors = torch.linspace(0, *self.transforms, steps=tensor_batch.shape[0])*transform_mask.float()  
        max_vals = tensor_batch.view(tensor_batch.shape[0], tensor_batch.shape[1], -1).max(dim=2)[0].view(tensor_batch.shape[0], tensor_batch.shape[1], 1, 1)
        mean_vals = tensor_batch.view(tensor_batch.shape[0], tensor_batch.shape[1], -1).mean(dim=2).view(tensor_batch.shape[0], tensor_batch.shape[1], 1, 1)
        if mean_vals.mean().item() < 1:
            #mean_vals+=.05
            new_mean = contrast_factors.to(mean_vals).view(-1, 1, 1, 1)*(mean_vals)
            contrast_shift_factor = .05
        else:
            new_mean = contrast_factors.to(mean_vals).view(-1, 1, 1, 1)*mean_vals
            contrast_shift_factor = .05
        factors = (max_vals+(max_vals*contrast_shift_factor)) * ( new_mean + max_vals ) / ( max_vals*(max_vals+(max_vals*contrast_shift_factor) - new_mean ) + .001 ) # 
        tensor_batch_return = ( factors * ( tensor_batch - mean_vals ) ) + mean_vals
    
        if return_transforms:
            return tensor_batch_return, self.transforms
        return tensor_batch_return
    
    def refresh(self):
        self.transforms = torch.rand((1,)) * self.max_factor


# Classified Tiles Piepline     
class ClassifiedTilesPipeline(nn.Module):
    def __init__(self, target_size, transforms: list=None, type_transforms: str='training', lighting_transforms: bool=True):
        super(ClassifiedTilesPipeline, self).__init__()
        self.type_transforms = type_transforms
        if transforms is not None:
            self.transforms = transforms
        else:
            if type_transforms == 'training': 
                l_transforms = []
                if lighting_transforms:
                    l_transforms = [
                        RandomBrightness(do_y = False),
                        RandomContrast(do_y = False)
                    ]
                self.transforms = [
                    *l_transforms,
                    RandomFlip(),
                    RandomResizedRotate(),
                    RandomResizedCrop(target_size=target_size)
                ]
            elif type_transforms == 'validation':
                self.transforms = [
                    CenterCrop(target_size=target_size)
                ]
            else:
                raise Exception('invalid type_transforms expected one of the folowing values `training` `validation`')

        
    def forward(self, tensor_batch):
        (x, y) = tensor_batch
        y = y.float()
        for transform in self.transforms:
            if self.type_transforms == 'training':
                transform.refresh()
            x = transform(x, return_transforms=False)
            if getattr(transform, 'do_y', True):
                y = transform(y, return_transforms=False)
        return (x,y.round().long())


