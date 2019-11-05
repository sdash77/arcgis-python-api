import os
from pathlib import Path
from functools import partial
import xml.etree.ElementTree as ET
import math
import sys
import json 
import logging      
import types                                                                                                                                                            

try:
    import numpy as np
    from fastai.vision.data import imagenet_stats, ImageList, bb_pad_collate
    from fastai.vision.transform import crop, rotate, dihedral_affine, brightness, contrast, skew, rand_zoom, get_transforms, flip_lr
    from fastai.vision import ImageDataBunch
    from fastai.torch_core import data_collate
    import torch
    from .models._ssd_utils import SSDObjectItemList
    from .models._unet_utils import ArcGISSegmentationItemList, ArcGISSegmentationMSItemList, _show_batch_unet_multispectral
    from .models._maskrcnn_utils import ArcGISInstanceSegmentationItemList
    from .models._ner_utils import ner_prepare_data
    HAS_FASTAI = True
except:
    HAS_FASTAI = False

band_abrevation_lib = {
    'b': 'BLUE',
    'c': 'CIRRUS',
    'ca': 'COASTAL AEROSOL',
    'g': 'GREEN',
    'nir': 'NEAR INFRARED',
    'nnir': 'NARROW NEAR INFRARED',
    'p': 'PANCHROMATIC',
    'r': 'RED',
    'swir': 'SHORT WAVELENGTH INFRARED',
    'swirc': 'SHORT WAVELENGTH INFRARED – Cirrus',
    'tir': 'THERMAL INFRARED',
    'vre': 'Vegetation red edge',
    'wv': 'WATER VAPOUR'
}

imagery_type_lib = {
    'landsat8': {
        "bands": ['ca', 'b', 'g', 'r', 'nir', 'swir', 'swir', 'c', 'qa', 'tir', 'tir'],
        "bands_info": { # incomplete
        }
    },
    "naip": {
        "bands": ['r', 'g', 'b', 'nir'],
        "bands_info": { # incomplete
        }
    },
    'sentinel2': { 
        "bands": ['ca', 'b', 'g', 'r', 'vre', 'vre', 'vre', 'nir', 'nnir', 'wv', 'swirc', 'swir', 'swir'],
        "bands_info": { # incomplete
            "b1": {
                "Name": "costal",
                "max": 10000,
                "min": 10000
            },            
            "b2": {
                "Name": "blue",
                "max": 10000,
                "min": 10000
            }
        }
    }
}

def _raise_fastai_import_error():
    raise Exception("""This module requires fastai, PyTorch, torchvision and scikit-image as its dependencies. 
Install them using 'conda install -c pytorch -c fastai fastai=1.0.54 pytorch=1.1.0 torchvision scikit-image'""")

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

        if not (bbs.nelement() == 0) or list(bbs) == [[0,0,0,0]]:
            bboxes[i,-len(lbls):] = bbs
            labels[i,-len(lbls):] = torch.tensor(lbls, device=bbs.device).long()
    return torch.cat(imgs,0), (bboxes,labels)    


def _get_bbox_classes(xmlfile, class_mapping, not_label_count=[0], height_width=[]):
    if not os.path.exists(xmlfile):
        not_label_count[0] += 1
        return [[[0, 0, 0, 0]], [list(class_mapping.values())[0]]]

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
        data_class_text = tag_obj.find('name').text
        
        if (not data_class_text.isnumeric() and not class_mapping.get(data_class_text))\
             or (data_class_text.isnumeric() and not(class_mapping.get(data_class_text) or class_mapping.get(int(data_class_text)))):
            continue

        if data_class_text.isnumeric():
            data_class_mapping = class_mapping[data_class_text] if class_mapping.get(data_class_text) else class_mapping[int(data_class_text)]
        else:
            data_class_mapping = class_mapping[data_class_text]

        classes.append(data_class_mapping)
        bboxes.append([ymin, xmin, ymax, xmax])
        height_width.append(((xmax - xmin)*1.25, (ymax - ymin)*1.25))
    
    if len(bboxes) == 0:
        return [[[0, 0, 0, 0]], [list(class_mapping.values())[0]]]
    return [bboxes, classes]


def _get_bbox_lbls(imagefile, class_mapping, not_label_count, height_width):
    xmlfile = imagefile.parents[1] / 'labels' / imagefile.name.replace('{ims}'.format(ims=imagefile.suffix), '.xml')
    return _get_bbox_classes(xmlfile, class_mapping, not_label_count, height_width)


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

def _get_batch_stats(image_list, norm_pct=1, _band_std_values=False):
    n_normalization_samples = round(len(image_list)*norm_pct)
    #n_normalization_samples = max(256, n_normalization_samples)
    random_indexes = np.random.randint(0, len(image_list), size=min(n_normalization_samples, len(image_list)))

    # Original Band Stats
    min_values_store = []
    max_values_store = []
    mean_values_store = []

    data_shape = image_list[0].data.shape
    n_bands = data_shape[0]
    feasible_chunk = round(512*4*400/(n_bands*data_shape[1])) # ~3gb footprint
    chunk = min(feasible_chunk, n_normalization_samples)
    i = 0
    for i in range(0, n_normalization_samples, chunk):
        x_tensor_chunk = torch.stack([ x.data for x in image_list[random_indexes[i:i+chunk]] ] )
        """
        min_values = torch.zeros(n_bands)
        max_values = torch.zeros(n_bands)
        mean_values = torch.zeros(n_bands)
        for bi in range(n_bands):
            min_values[bi] = x_tensor_chunk[:, bi].min()
            max_values[bi] = x_tensor_chunk[:, bi].max()
            mean_values[bi] = x_tensor_chunk[:, bi].mean()
        """
        min_values = x_tensor_chunk.min(dim=0)[0].min(dim=1)[0].min(dim=1)[0]
        max_values = x_tensor_chunk.max(dim=0)[0].max(dim=1)[0].max(dim=1)[0]
        mean_values = x_tensor_chunk.mean((0, 2, 3))
        min_values_store.append(min_values)
        max_values_store.append(max_values)
        mean_values_store.append(mean_values)

    band_max_values = torch.stack(max_values_store).max(dim=0)[0]
    band_min_values = torch.stack(min_values_store).min(dim=0)[0]
    band_mean_values = torch.stack(mean_values_store).mean(dim=0)
    
    view_shape = _get_view_shape(image_list[0].data, band_mean_values)

    if _band_std_values:
        std_values_store = []
        for i in range(0, n_normalization_samples, chunk):
            x_tensor_chunk = torch.stack([ x.data for x in image_list[random_indexes[i:i+chunk]] ] )
            std_values = (x_tensor_chunk - band_mean_values.view(view_shape)).pow(2).sum((0, 2, 3))
            std_values_store.append(std_values)
        band_std_values = (torch.stack(std_values_store).sum(dim=0) / ((n_normalization_samples * data_shape[1] * data_shape[2])-1)).sqrt()
    else:
        band_std_values = None

    # Scaled Stats
    scaled_min_values = torch.tensor([0 for i in range(n_bands)], dtype=torch.float32)
    scaled_max_values = torch.tensor([1 for i in range(n_bands)], dtype=torch.float32)
    scaled_mean_values = _tensor_scaler(band_mean_values, band_min_values, band_max_values, mode='minmax')
    
    scaled_std_values_store = []
    for i in range(0, n_normalization_samples, chunk):
        x_tensor_chunk = torch.stack([ x.data for x in image_list[random_indexes[i:i+chunk]] ] )
        x_tensor_chunk = _tensor_scaler(x_tensor_chunk, band_min_values, band_max_values, mode='minmax')
        std_values = (x_tensor_chunk - scaled_mean_values.view(view_shape)).pow(2).sum((0, 2, 3))
        scaled_std_values_store.append(std_values)
    scaled_std_values = (torch.stack(scaled_std_values_store).sum(dim=0) / ((n_normalization_samples * data_shape[1] * data_shape[2])-1)).sqrt()

    #return band_min_values, band_max_values, band_mean_values, band_std_values, scaled_min_values, scaled_max_values, scaled_mean_values, scaled_std_values
    return {
        "band_min_values": band_min_values, 
        "band_max_values": band_max_values, 
        "band_mean_values": band_mean_values, 
        "band_std_values": band_std_values, 
        "scaled_min_values": scaled_min_values, 
        "scaled_max_values": scaled_max_values, 
        "scaled_mean_values": scaled_mean_values, 
        "scaled_std_values": scaled_std_values
    }


def _get_view_shape(tensor_batch, band_factors):
    view_shape = [1 for i in range(len(tensor_batch.shape))]
    view_shape[tensor_batch.shape.index(band_factors.shape[0])] = band_factors.shape[0]
    return tuple(view_shape)

def _tensor_scaler(tensor_batch, min_values, max_values, mode='minmax', create_view=True):
    if create_view:
        view_shape = _get_view_shape(tensor_batch, min_values)
        max_values = max_values.view(view_shape)
        min_values = min_values.view(view_shape)
    if mode=='minmax':
        # new_value = (((old_value - old_min) / (old_max-old_min))*(new_max-new_min))+new_min
        scaled_tensor_batch = (tensor_batch - min_values) / (max_values - min_values)
    return scaled_tensor_batch

def _tensor_scaler_tfm(tensor_batch, min_values, max_values, mode='minmax'):
    x = tensor_batch[0]
    y = tensor_batch[1]
    max_values = max_values.view(1, -1, 1, 1).to(x.device)
    min_values = min_values.view(1, -1, 1, 1).to(x.device)
    x = _tensor_scaler(x, min_values, max_values, mode, create_view=False)
    return (x, y)

def _extract_bands_tfm(tensor_batch, band_indices):
    x_batch = tensor_batch[0][:, band_indices]
    y_batch = tensor_batch[1]
    return (x_batch, y_batch)

def prepare_data(path,
                 class_mapping=None, 
                 chip_size=224, 
                 val_split_pct=0.1, 
                 batch_size=64, 
                 transforms=None, 
                 collate_fn=_bb_pad_collate, 
                 seed=42, 
                 dataset_type=None, 
                 resize_to=None,
                 **kwargs):
    """
    Prepares a data object from training sample exported by the 
    Export Training Data tool in ArcGIS Pro or Image Server, or training 
    samples in the supported dataset formats. This data object consists of 
    training and validation data sets with the specified transformations, 
    chip size, batch size, split percentage, etc. 
    -For object detection, use Pascal_VOC_rectangles format.
    -For feature categorization use Labelled Tiles or ImageNet format.
    -For pixel classification, use Classified Tiles format.
    -For entity extraction from text, use BIO, LBIOU or ner_json formats. 

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    path                    Required string. Path to data directory.
    ---------------------   -------------------------------------------
    class_mapping           Optional dictionary. Mapping from id to
                            its string label.
                            For dataset_type=BIO, LBIOU or ner_json:
                                Provide address field as class mapping
                                in below format:
                                class_mapping={'address_tag':'address_field'}
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
    resize_to               Optional integer. Resize the image to given size.
    =====================   ===========================================

    :returns: data object
    """
    """kwargs documentation
    imagery_type='RGB'
    bands=None
    rgb_bands=[0, 1, 2]
    """

    height_width = []

    if not HAS_FASTAI:
        _raise_fastai_import_error()

    if type(path) is str:
        path = Path(path)

    databunch_kwargs = {'num_workers':0} if sys.platform == 'win32' else {}
    databunch_kwargs['bs'] = batch_size

    kwargs_transforms = {}
    if resize_to:
        kwargs_transforms['size'] = resize_to

    has_esri_files = _check_esri_files(path)
    alter_class_mapping = False
    color_mapping = None

    # Multispectral Kwargs init
    _bands = None
    _imagery_type = None
    _is_multispectral = False
    _show_batch_multispectral = None

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

        # Create Class Mapping from EMD if not specified by user
        if class_mapping is None:
            try:
                class_mapping = {i['Value']: i['Name'] for i in emd['Classes']}
            except KeyError:
                class_mapping = {i['ClassValue']: i['ClassName'] for i in emd['Classes']}

        color_mapping = {(i.get('Value', 0) or i.get('ClassValue', 0)): i['Color'] for i in emd.get('Classes', [])}

        if color_mapping.get(None):
            del color_mapping[None]

        if class_mapping.get(None):
            del class_mapping[None]

        # Multispectral support from EMD 
        # Not Implemented Yet
        if emd.get('bands', None) is not None: 
            _bands = emd.get['bands'] # Not Implemented
            
        if emd.get('imagery_type', None) is not None: 
            _imagery_type = emd.get['imagery_type'] # Not Implemented        

    elif dataset_type == 'PASCAL_VOC_rectangles' and not has_esri_files:
        if class_mapping is None:
            class_mapping = _get_class_mapping(path / 'labels')
            alter_class_mapping = True

    # Multispectral check
    imagery_type = 'RGB'
    if kwargs.get('imagery_type', None) is not None:
        imagery_type = kwargs.get('imagery_type')
    elif _imagery_type is not None:
        imagery_type = _imagery_type

    bands = None
    if kwargs.get('bands', None) is not None:
        bands = kwargs.get('bands')
        for i, b in enumerate(bands):
            if type(b) == str:
                bands[i] = b.lower()
    elif imagery_type_lib.get(imagery_type, None) is not None:
        bands = imagery_type_lib.get(imagery_type)['bands']
    elif _bands is not None:
        bands = _bands

    rgb_bands = None
    if kwargs.get('rgb_bands', None) is not None:
        rgb_bands = kwargs.get('rgb_bands')
    elif bands is not None:
        rgb_bands = [ bands.index(b) for b in ['r', 'g', 'b'] if b in bands ]
    
    if (bands is not None) or (rgb_bands is not None) or (not imagery_type == 'RGB'):
        if imagery_type == 'RGB':
            imagery_type = 'multispectral'
        _is_multispectral = True
    
    if kwargs.get('norm_pct', None) is not None:
        norm_pct= kwargs.get('norm_pct')
        norm_pct = min(max(0, norm_pct), 1)
    else:
        norm_pct = .1

    if dataset_type == 'RCNN_Masks':

        def get_labels(x, label_dirs, ext=right):
            label_path = []
            for lbl in label_dirs:
                if os.path.exists(Path(lbl) / (x.stem + '.{}'.format(ext))):
                    label_path.append(Path(lbl) / (x.stem + '.{}'.format(ext)))
            return label_path

        if class_mapping.get(0):
            del class_mapping[0]

        if color_mapping.get(0):
            del color_mapping[0]

      
        src = (ArcGISInstanceSegmentationItemList.from_folder(path/'images')
            .split_by_rand_pct(val_split_pct, seed=seed))

        label_dirs = os.listdir(path/'labels')
        label_dir = [os.path.join(path/'labels', lbl) for lbl in label_dirs if os.path.isdir(os.path.join(path/'labels', lbl))]
        get_y_func = partial(get_labels, label_dirs= label_dir)
        src = src.label_from_func(get_y_func, chip_size=chip_size, classes=['NoData'] + list(class_mapping.values()), class_mapping=class_mapping, color_mapping=color_mapping)
    
    elif dataset_type == 'Classified_Tiles':

        def get_y_func(x, ext=right):
            return x.parents[1] / 'labels' / (x.stem + '.{}'.format(ext))

        if class_mapping.get(0):
            del class_mapping[0]

        if color_mapping.get(0):
            del color_mapping[0]

        # TODO : Handle NoData case

        # Handle Multispectral
        if _is_multispectral:
            data = ArcGISSegmentationMSItemList.from_folder(path/'images')\
                .split_by_rand_pct(val_split_pct, seed=seed)\
                .label_from_func(
                    get_y_func, classes=(['NoData'] + list(class_mapping.values())),
                    class_mapping=class_mapping,
                    color_mapping=color_mapping
                )
            _show_batch_multispectral = _show_batch_unet_multispectral            

            def classified_tiles_collate_fn(samples): # The default fastai collate_fn was causing memory leak on tensors
                r = ( torch.stack([x[0].data for x in samples]), torch.stack([x[1].data for x in samples]) )
                return r
            databunch_kwargs['collate_fn'] = classified_tiles_collate_fn

        else:
            data = ArcGISSegmentationItemList.from_folder(path/'images')\
                .split_by_rand_pct(val_split_pct, seed=seed)\
                .label_from_func(
                    get_y_func, classes=(['NoData'] + list(class_mapping.values())),
                    class_mapping=class_mapping,
                    color_mapping=color_mapping
                )

        if transforms is None:
            transforms = get_transforms(
                flip_vert=True,
                max_rotate=90.,
                max_zoom=3.0,
                max_lighting=0.5
            )

        kwargs_transforms['tfm_y'] = True
        kwargs_transforms['size'] = chip_size
    elif dataset_type == 'PASCAL_VOC_rectangles':
        not_label_count = [0]
        get_y_func = partial(
            _get_bbox_lbls,
            class_mapping=class_mapping,
            not_label_count=not_label_count,
            height_width=height_width
        )

        data = SSDObjectItemList.from_folder(path/'images')\
            .split_by_rand_pct(val_split_pct, seed=seed)\
            .label_from_func(get_y_func)

        if not_label_count[0]:
            logger = logging.getLogger()
            logger.warning("Please check your dataset. " + str(not_label_count[0]) + " images dont have the corresponding label files.")

        if transforms is None:
            ranges = (0, 1)
            train_tfms = [
                crop(size=chip_size, p=1., row_pct=ranges, col_pct=ranges),
                dihedral_affine() if has_esri_files else flip_lr(),
                brightness(change=(0.4, 0.6)),
                contrast(scale=(0.75, 1.5)),
                rand_zoom(scale=(1.0, 1.5))
            ]
            val_tfms = [crop(size=chip_size, p=1., row_pct=0.5, col_pct=0.5)]
            transforms = (train_tfms, val_tfms)

        kwargs_transforms['tfm_y'] = True
        databunch_kwargs['collate_fn'] = collate_fn
    elif dataset_type in ['Labeled_Tiles', 'Imagenet']:
        if dataset_type == 'Labeled_Tiles':
            get_y_func = partial(_get_lbls, class_mapping=class_mapping)
        else:
            def get_y_func(x):
                return x.parent.stem

        data = ImageList.from_folder(path/'images')\
            .split_by_rand_pct(val_split_pct, seed=42)\
            .label_from_func(get_y_func)

        if dataset_type == 'Imagenet':
            class_mapping = {}
            index = 1
            for class_name in data.classes:
                class_mapping[index] = class_name
                index = index + 1

        if transforms is None:
            ranges = (0, 1)
            train_tfms = [
                rotate(degrees=30, p=0.5),
                crop(size=chip_size, p=1., row_pct=ranges, col_pct=ranges),
                dihedral_affine(),
                brightness(change=(0.4, 0.6)),
                contrast(scale=(0.75, 1.5))
            ]
            val_tfms = [crop(size=chip_size, p=1.0, row_pct=0.5, col_pct=0.5)]
            transforms = (train_tfms, val_tfms)
    elif dataset_type in ['ner_json','BIO','LBIOU']:
        return ner_prepare_data(dataset_type=dataset_type, path=path, class_mapping=class_mapping, val_split_pct=val_split_pct)
    else:
        raise NotImplementedError('Unknown dataset_type="{}".'.format(dataset_type))
    
    if dataset_type == 'RCNN_Masks':
        if transforms ==  None:
            data = (src.transform(size=chip_size, tfm_y=True)
                .databunch(**databunch_kwargs))
        else:
            data = (src.transform(transforms, size=chip_size, tfm_y=True) 
                    .databunch(**databunch_kwargs))
    elif _is_multispectral:
        data = data.databunch(**databunch_kwargs)

        # Statistics        
        dummy_stats = {
            "batch_stats_for_norm_pct_0" : {
                "band_min_values":None, 
                "band_max_values":None, 
                "band_mean_values":None, 
                "band_std_values":None, 
                "scaled_min_values":None, 
                "scaled_max_values":None, 
                "scaled_mean_values":None, 
                "scaled_std_values":None
            }
        }
        normstats_json_path = os.path.abspath(data.path / '..' / 'esri_normalization_stats.json')
        if not os.path.exists(normstats_json_path):
            normstats = dummy_stats
            with open(normstats_json_path, 'w', encoding='utf-8') as f:
                json.dump(normstats, f, ensure_ascii=False, indent=4)
        else:
            with open(normstats_json_path) as f:
                normstats = json.load(f)

        norm_pct_search = f"batch_stats_for_norm_pct_{round(norm_pct*100)}"
        if norm_pct_search in normstats:
            batch_stats = normstats[norm_pct_search]
            for s in batch_stats:
                if batch_stats[s] is not None:
                    batch_stats[s] = torch.tensor(batch_stats[s])
        else:
            batch_stats = _get_batch_stats(data.x, norm_pct)
            normstats[norm_pct_search] = dict(batch_stats)
            for s in normstats[norm_pct_search]:
                if normstats[norm_pct_search][s] is not None:
                    normstats[norm_pct_search][s] = normstats[norm_pct_search][s].tolist()
            with open(normstats_json_path, 'w', encoding='utf-8') as f:
                json.dump(normstats, f, ensure_ascii=False, indent=4)

        # batch_stats -> [band_min_values, band_max_values, band_mean_values, band_std_values, scaled_min_values, scaled_max_values, scaled_mean_values, scaled_std_values]
        data._band_min_values = batch_stats['band_min_values']
        data._band_max_values = batch_stats['band_max_values']
        data._band_mean_values = batch_stats['band_mean_values']
        data._band_std_values = batch_stats['band_std_values']
        data._scaled_min_values = batch_stats['scaled_min_values']
        data._scaled_max_values = batch_stats['scaled_max_values']
        data._scaled_mean_values = batch_stats['scaled_mean_values']
        data._scaled_std_values = batch_stats['scaled_std_values']
        
        # Scaling
        if kwargs.get('do_scale', None) is not None:
            data._do_scale = kwargs.get('do_scale')
        else:
            data._do_scale = True
        data._min_max_scaler = partial(_tensor_scaler, min_values=data._band_min_values, max_values=data._band_max_values, mode='minmax')
        if data._do_scale:
            data._min_max_scaler_tfm = partial(_tensor_scaler_tfm, min_values=data._band_min_values, max_values=data._band_max_values, mode='minmax')
            data.add_tfm(data._min_max_scaler_tfm)
        
        # Normalize
        if kwargs.get('do_normalize', None) is not None:
            data._do_normalize = kwargs.get('do_normalize')
        else:
            data._do_normalize = True
        if data._do_normalize:
            data = data.normalize(stats=(data._scaled_mean_values, data._scaled_std_values), do_x=True, do_y=False)
    else:
        # 
        data = (data.transform(transforms, **kwargs_transforms)
            .databunch(**databunch_kwargs)
            .normalize(imagenet_stats))


    data.chip_size = data.x[0].shape[-1] if transforms is False else chip_size

    if alter_class_mapping:
        new_mapping = {}
        for i, class_name in enumerate(class_mapping.keys()):
            new_mapping[i+1] = class_name
        class_mapping = new_mapping

    data.class_mapping = class_mapping
    data.color_mapping = color_mapping
    data.show_batch = partial(data.show_batch, rows=min(int(math.sqrt(batch_size)), 5))
    data.orig_path = path
    data.resize_to = kwargs_transforms.get('size', None)
    data.height_width = height_width
    
    data._is_multispectral = _is_multispectral
    if data._is_multispectral:
        data._imagery_type = imagery_type
        data._bands = bands
        data._norm_pct = norm_pct
        data._rgb_bands = rgb_bands
        data._symbology_rgb_bands = rgb_bands

        # Handle invalid color mapping
        data._multispectral_color_mapping = color_mapping
        if any( -1 in x for x in data._multispectral_color_mapping.values() ):
            random_color_list = np.random.randint(low=0, high=255, size=(len(data._multispectral_color_mapping), 3)).tolist()
            for i, c in enumerate(data._multispectral_color_mapping):
                if -1 in data._multispectral_color_mapping[c]:
                    data._multispectral_color_mapping[c] = random_color_list[i]

        # Prepare unknown bands list if bands data is missing
        if data._bands is None:
            n_bands = data.x[0].data.shape[0]
            if n_bands == 1:# Handle Pancromatic case
                data._bands = data._symbology_rgb_bands = data._rgb_bands = ['p']
            else:
                data._bands = ['u' for i in range(n_bands)]
        
        # 
        if data._rgb_bands is None:
            data._rgb_bands = []

        # 
        if data._symbology_rgb_bands is None:
            data._symbology_rgb_bands = [0, 1, 2][:min(n_bands, 3)]

        # Complete symbology rgb bands
        if len(data._bands) > 2 and len(data._symbology_rgb_bands) < 3:
            data._symbology_rgb_bands += [ min(max(data._symbology_rgb_bands)+1, len(data._bands)-1)  for i in range(3 - len(data._symbology_rgb_bands)) ]
        
        # Overwrite band values at r g b indexes with 'r' 'g' 'b'
        for i, band_idx in enumerate(data._rgb_bands):
            if band_idx is not None:
                if data._bands[band_idx] == 'u':
                    data._bands[band_idx] = ['r', 'g', 'b'][i]

        # Attach custom show batch
        if _show_batch_multispectral is not None:
            data.show_batch = types.MethodType( _show_batch_multispectral, data )

        # Apply filter band transformation if user has specified extract_bands otherwise add a generic extract_bands
        """
        extract_bands : List containing band indices of the bands from imagery on which the model would be trained. 
                        Useful for benchmarking and applied training, for reference see examples below.
                        
                        4 band naip ['r, 'g', 'b', 'nir'] + extract_bands=[0, 1, 2] -> 3 band naip with bands ['r', 'g', 'b'] 

        """
        data._extract_bands = kwargs.get('extract_bands', None) 
        if data._extract_bands is None:
            data._extract_bands = list(range(len(data._bands)))
        else:
            data._extract_bands_tfm = partial(_extract_bands_tfm, band_indices=data._extract_bands)
            data.add_tfm(data._extract_bands_tfm)   

        # Tail Training Override
        _train_tail = True
        if [data._bands[i] for i in data._extract_bands] == ['r', 'g', 'b']:
            _train_tail = False
        data._train_tail = kwargs.get('train_tail', _train_tail)

    return data
