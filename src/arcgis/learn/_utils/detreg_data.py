try:
    import torch
    from torch.utils.data import DataLoader
    from PIL import Image
    from pathlib import Path
    import os
    import json
    import xml.etree.ElementTree as ET
    from typing import Dict, List
    from tqdm import tqdm
    import re
    from os import listdir
    from os.path import isfile, join
    from fastai.vision.data import ImageDataBunch
    from .coco_detection_utils import build as build_dataset
    from .coco_detection_utils import collate_fn
    from shutil import copyfile
except:
    pass


def get_image_info(annotation_root, extract_num_from_imgid=True):
    path = annotation_root.findtext("path")
    if path is None:
        filename = annotation_root.findtext("filename")
    else:
        filename = os.path.basename(path)
    img_name = os.path.basename(filename)
    img_id = os.path.splitext(img_name)[0]
    if extract_num_from_imgid and isinstance(img_id, str):
        img_id = int(re.findall(r"\d+", img_id)[0])

    size = annotation_root.find("size")
    width = int(size.findtext("width"))
    height = int(size.findtext("height"))

    image_info = {"file_name": filename, "height": height, "width": width, "id": img_id}
    return image_info


def get_coco_annotation_from_obj(obj, label2id):
    label = int(obj.findtext("name"))
    assert label in label2id, f"Error: {label} is not in label2id !"
    category_id = label2id[label]
    bndbox = obj.find("bndbox")
    xmin = float(bndbox.findtext("xmin"))
    ymin = float(bndbox.findtext("ymin"))
    xmax = float(bndbox.findtext("xmax"))
    ymax = float(bndbox.findtext("ymax"))
    assert (
        xmax > xmin and ymax > ymin
    ), f"Box size error !: (xmin, ymin, xmax, ymax): {xmin, ymin, xmax, ymax}"
    o_width = xmax - xmin
    o_height = ymax - ymin
    ann = {
        "area": o_width * o_height,
        "iscrowd": 0,
        "bbox": [xmin, ymin, o_width, o_height],
        "category_id": label,
        "ignore": 0,
        "segmentation": [],  # This script is not for segmentation
    }
    return ann


def convert_xmls_to_cocojson(
    annotation_paths: List[str],
    label2id: Dict[str, int],
    output_jsonpath: str,
    extract_num_from_imgid: bool = True,
):
    output_json_dict = {
        "images": [],
        "type": "instances",
        "annotations": [],
        "categories": [],
    }
    bnd_id = 1  # START_BOUNDING_BOX_ID, TODO input as args ?
    # print('Start converting !')
    for a_path in tqdm(annotation_paths):
        # Read annotation xml
        ann_tree = ET.parse(a_path)
        ann_root = ann_tree.getroot()

        img_info = get_image_info(
            annotation_root=ann_root, extract_num_from_imgid=extract_num_from_imgid
        )
        img_id = img_info["id"]
        output_json_dict["images"].append(img_info)

        for obj in ann_root.findall("object"):
            ann = get_coco_annotation_from_obj(obj=obj, label2id=label2id)
            ann.update({"image_id": img_id, "id": bnd_id})
            output_json_dict["annotations"].append(ann)
            bnd_id = bnd_id + 1

    for label, label_id in label2id.items():
        category_info = {"supercategory": "none", "id": label_id, "name": label}
        output_json_dict["categories"].append(category_info)

    with open(output_jsonpath, "w") as f:
        output_json = json.dumps(output_json_dict)
        f.write(output_json)


def get_coco_data(data, coco_data_path):
    orig_coco_path = coco_data_path
    coco_folder_path = os.path.join(data.path, "coco_data")
    annotation_path = os.path.join(coco_folder_path, "annotations")
    coco_train_path = os.path.join(coco_folder_path, "train2017")
    coco_val_path = os.path.join(coco_folder_path, "val2017")
    voc_label_path = os.path.join(data.path, "labels")
    voc_val_label_path = os.path.join(voc_label_path, "val")
    voc_train_label_path = os.path.join(voc_label_path, "train")
    if not os.path.isdir(coco_folder_path):
        os.makedirs(coco_folder_path)
    if not os.path.isdir(annotation_path):
        os.makedirs(annotation_path)
    if not os.path.isdir(coco_train_path):
        os.makedirs(coco_train_path)
    if not os.path.isdir(coco_val_path):
        os.makedirs(coco_val_path)
    if not os.path.isdir(voc_val_label_path):
        os.makedirs(voc_val_label_path)
    if not os.path.isdir(voc_train_label_path):
        os.makedirs(voc_train_label_path)
    ann_dir_list = [
        [
            os.path.join(voc_label_path, "train"),
            os.path.join(annotation_path, "instances_train2017.json"),
        ],
        [
            os.path.join(voc_label_path, "val"),
            os.path.join(annotation_path, "instances_val2017.json"),
        ],
    ]

    path = os.path.join(data.path, "images")
    outpath = os.path.join(data.path, "coco_data")
    voc_label_path = os.path.join(data.path, "labels")

    for infile in os.listdir(path):
        outpath = os.path.join(data.path, "coco_data")
        # print ("file : " + infile)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        if infile[-3:] == "tif" or infile[-3:] == "bmp":
            # print "is tif or bmp"
            file_path = path + "\\" + infile
            out_label = infile[:-3] + "xml"
            # print("filename : " + file_path)
            file_path_1 = Path(file_path)
            if file_path_1 in data.valid_ds.items:
                outpath = os.path.join(outpath, "val2017")
                label_path = os.path.join(voc_label_path, "val")
            else:
                outpath = os.path.join(outpath, "train2017")
                label_path = os.path.join(voc_label_path, "train")
            dest = os.path.join(label_path, out_label)
            outfile = infile[:-3] + "jpg"
            out_label = infile[:-3] + "xml"
            im = Image.open(file_path)
            # print("new filename : " + outfile)
            out = im.convert("RGB")
            if not os.path.exists(dest):
                copyfile(os.path.join(voc_label_path, out_label), dest)
            outfile = outpath + "\\" + outfile
            out.save(outfile, "JPEG", quality=100)
        elif infile[-3:] == "jpg" or infile[-3:] == "jpeg":
            file_path = path + "\\" + infile
            # print("filename : " + file_path)
            out_label = infile[:-3] + "xml"
            file_path_1 = Path(file_path)
            if file_path_1 in data.valid_ds.items:
                outpath = os.path.join(outpath, "val2017")
                label_path = os.path.join(voc_label_path, "val")
                dest = os.path.join(label_path, out_label)
            else:
                outpath = os.path.join(outpath, "train2017")
                label_path = os.path.join(voc_label_path, "train")
                dest = os.path.join(label_path, out_label)
            outfile = infile[:-3] + "jpg"
            im = Image.open(file_path)
            # print("new filename : " + outfile)
            out = im.convert("RGB")
            copyfile(os.path.join(voc_label_path, out_label), dest)
            outfile = outpath + "\\" + outfile
            out.save(outfile, "JPEG", quality=100)

    for ann in ann_dir_list:
        output = ann[1]
        annpath = ann[0]
        annpaths_lis = [
            os.path.join(annpath, f)
            for f in listdir(annpath)
            if isfile(join(annpath, f))
        ]
        convert_xmls_to_cocojson(
            annotation_paths=annpaths_lis,
            label2id=dict((k, v) for k, v in data.class_mapping.items()),
            output_jsonpath=output,
            extract_num_from_imgid=True,
        )
        with open(output) as infile:
            json_data = json.load(infile)
        for elem in json_data["images"]:
            elem["file_name"] = elem["file_name"].replace("tif", "jpg")
        with open(output, "w") as outfile:
            json.dump(json_data, outfile)

    dataset_train = build_dataset("train", coco_train_path, annotation_path)
    dataset_val = build_dataset("val", coco_val_path, annotation_path)
    device = torch.device("cuda")
    sampler_train = torch.utils.data.RandomSampler(dataset_train)
    sampler_val = torch.utils.data.SequentialSampler(dataset_val)
    batch_sampler_train = torch.utils.data.BatchSampler(
        sampler_train, 4, drop_last=True
    )
    data_loader_train = DataLoader(
        dataset_train,
        batch_sampler=batch_sampler_train,
        collate_fn=collate_fn,
        num_workers=2,
        pin_memory=True,
    )
    data_loader_val = DataLoader(
        dataset_val,
        4,
        sampler=sampler_val,
        drop_last=False,
        collate_fn=collate_fn,
        num_workers=2,
        pin_memory=True,
    )

    data_fastai = ImageDataBunch(data_loader_train, data_loader_val, device=device)
    data_fastai.train_dl.dl.collate_fn = collate_fn
    data_fastai.valid_dl.dl.collate_fn = collate_fn
    data_fastai.dataset_type = data._dataset_type
    data_fastai.classes = data.classes
    data_fastai.class_mapping = data.class_mapping
    data_fastai.c = data.c
    data_fastai.path = data.path
    data_fastai.chip_size = data.chip_size
    data_fastai._imagery_type = data._imagery_type
    data_fastai._is_multispectral = data._is_multispectral
    data_fastai._image_space_used = data._image_space_used
    data_fastai._val_split_pct = data._val_split_pct

    return data_fastai
