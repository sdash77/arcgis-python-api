try:
    from fastai.vision.data import ObjectItemList, imagenet_stats
    from fastai.vision.transform import crop, dihedral_affine
    import torch
    from pathlib import Path
    from functools import partial
    import xml.etree.ElementTree as ET
    HAS_FASTAI = True
except:
    HAS_FASTAI = False

def _raise_fastai_import_error():
    raise Exception('This class requires fastai, PyTorch and torchvision as its dependencies. Install it using "conda install -c pytorch -c fastai fastai pytorch torchvision"')

def _bb_pad_collate(samples, pad_idx=0):
    "Function that collect `samples` of labelled bboxes and adds padding with `pad_idx`."
    arr = []
    for s in samples:
        try:
            arr.append(len(s[1].data[1]))
        except Exception as e:
            # set_trace()
            # print(s[1].data[1],s[1].data[1],e)
            arr.append(0)
    max_len = max(arr)
#    max_len = max([len(s[1].data[1]) for s in samples])
    bboxes = torch.zeros(len(samples), max_len, 4)
    labels = torch.zeros(len(samples), max_len).long() + pad_idx
    imgs = []
    for i,s in enumerate(samples):
        imgs.append(s[0].data[None])
        bbs, lbls = s[1].data
        # print(bbs, lbls)
        try:
            bboxes[i,-len(lbls):] = bbs
            labels[i,-len(lbls):] = lbls
        except Exception as e:
            pass
    return torch.cat(imgs,0), (bboxes,labels)


def _get_bbox_lbls(imagefile, class_mapping):
    xmlfile = imagefile.parents[1] / 'labels' / imagefile.name.replace(f'{imagefile.suffix}', '.xml')
    tree = ET.parse(xmlfile)
    xmlroot = tree.getroot()
    bboxes  = []
    classes = []
    for child in xmlroot:
        if child.tag == 'object':
            xmin, ymin, xmax, ymax = float(child[1][0].text),\
            float(child[1][1].text),\
            float(child[1][2].text),\
            float(child[1][3].text)
            bboxes.append([ymin, xmin, ymax, xmax])
            classes.append(class_mapping[int(child[0].text)])

    return [bboxes, classes]

def prepare_data(path, class_mapping, chip_size=224, val_split_pct=0.1, bs=64, tfms=None, collate_fn=_bb_pad_collate, seed=42):
    """
    Prepares a Fast.ai DataBunch from the exported Pascal VOC image chips exported by Export Training Data tool in ArcGIS PRo or Image Server.
    
    This DataBunch consists of training and validation DataLoaders with the specified transformations, chip size, batch size, split percentage (for train-test split).
    """

    if not HAS_FASTAI:
        _raise_fastai_import_error()
    
    if type(path) is str:
        path = Path(path)
        
    images = 'images'
    
    get_y_func = partial(_get_bbox_lbls, class_mapping=class_mapping)

    src = (ObjectItemList.from_folder(path/images)
       .random_split_by_pct(val_split_pct, seed=seed)
       .label_from_func(get_y_func))
    
    if tfms is None:
        ranges = (0,1)
        train_tfms = [crop(size=chip_size, p=1., row_pct=ranges, col_pct=ranges), dihedral_affine()]
        val_tfms = [crop(size=chip_size, p=1., row_pct=0.5, col_pct=0.5)]
        tfms = (train_tfms, val_tfms)        
        
    data = (src
        .transform(tfms, tfm_y=True)
        .databunch(bs=bs, collate_fn=collate_fn)
        .normalize(imagenet_stats)
       )
    
    data.chip_size = chip_size
    
    return data