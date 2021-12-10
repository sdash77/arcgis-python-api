import os
import re
import xml.etree.ElementTree as ET


def _get_bbox_classes(label_file, class_mapping, height_width=[], **kwargs):
    dataset_type = kwargs.get("dataset_type", None)

    if dataset_type == "KITTI_rectangles":
        classes = []
        truncated = []
        occluded = []
        obs_angle = []
        bboxes = []
        hwl = []
        d_xyz = []
        occluded = []
        rot_yaxis = []
        start_space = re.compile("^\s+")  # pattern to capture leading spaces
        spaces_to_be_replaced = re.compile(
            "(?<=\d)(\s+)(?=\d)"
        )  # pattern to capture spaces between numeric values

        with open(label_file) as f:  # reading the bbox and class labels
            lines = f.readlines()

        for line in lines:
            line = re.sub(start_space, "", line)
            lst = re.sub(spaces_to_be_replaced, ",", line).split(
                ","
            )  # reading kitti labels from string to a list
            xmin, ymin, xmax, ymax = [
                float(n) for n in lst[4:8]
            ]  # reading bbox coordinates
            hieght, width, length = [float(n) for n in lst[8:11]]
            x, y, z = [float(n) for n in lst[11:14]]

            data_class_text = str(lst[0])
            if (
                not data_class_text.isnumeric()
                and not class_mapping.get(data_class_text)
            ) or (
                data_class_text.isnumeric()
                and not (
                    class_mapping.get(data_class_text)
                    or class_mapping.get(int(data_class_text))
                )
            ):
                continue
            if data_class_text.isnumeric():
                data_class_mapping = (
                    class_mapping[data_class_text]
                    if class_mapping.get(data_class_text)
                    else class_mapping[int(data_class_text)]
                )
            else:
                data_class_mapping = class_mapping[data_class_text]

            classes.append(data_class_mapping)  # object class
            truncated.append(float(lst[1]))  # if the object is truncated
            obs_angle.append(float(lst[2]))  # onservation angle
            occluded.append(float(lst[3]))  # if the object is occluded
            bboxes.append([ymin, xmin, ymax, xmax])
            height_width.append(((xmax - xmin) * 1.25, (ymax - ymin) * 1.25))
            hwl.append([hieght, width, length])
            d_xyz.append([x, y, z])
            rot_yaxis.append(float(lst[14]))  # angle of rotation along y axis
    else:
        tree = ET.parse(label_file)
        xmlroot = tree.getroot()
        bboxes = []
        classes = []
        for tag_obj in xmlroot.findall("object"):
            bnd_box = tag_obj.find("bndbox")
            xmin, ymin, xmax, ymax = (
                float(bnd_box.find("xmin").text),
                float(bnd_box.find("ymin").text),
                float(bnd_box.find("xmax").text),
                float(bnd_box.find("ymax").text),
            )
            data_class_text = tag_obj.find("name").text

            if (
                not data_class_text.isnumeric()
                and not class_mapping.get(data_class_text)
            ) or (
                data_class_text.isnumeric()
                and not (
                    class_mapping.get(data_class_text)
                    or class_mapping.get(int(data_class_text))
                )
            ):
                continue

            if data_class_text.isnumeric():
                data_class_mapping = (
                    class_mapping[data_class_text]
                    if class_mapping.get(data_class_text)
                    else class_mapping[int(data_class_text)]
                )
            else:
                data_class_mapping = class_mapping[data_class_text]

            classes.append(data_class_mapping)
            bboxes.append([ymin, xmin, ymax, xmax])
            height_width.append(((xmax - xmin) * 1.25, (ymax - ymin) * 1.25))

    if len(bboxes) == 0:
        return [[[0.0, 0.0, 0.0, 0.0]], [list(class_mapping.values())[0]]]
    return [bboxes, classes]


def _get_bbox_lbls(imagefile, class_mapping, height_width, **kwargs):
    dataset_type = kwargs.get("dataset_type", None)
    if dataset_type == "KITTI_rectangles":
        label_suffix = ".txt"
    else:
        label_suffix = ".xml"
    label_file = (
        imagefile.parents[1]
        / "labels"
        / imagefile.name.replace("{ims}".format(ims=imagefile.suffix), label_suffix)
    )
    return _get_bbox_classes(
        label_file, class_mapping, height_width, dataset_type=dataset_type
    )

def _get_bbox_lbls_helper(args):
    return _get_bbox_lbls(**args)

def _get_lbls(imagefile, class_mapping):
    xmlfile = (
        imagefile.parents[1]
        / "labels"
        / imagefile.name.replace("{ims}".format(ims=imagefile.suffix), ".xml")
    )
    return _get_bbox_classes(xmlfile, class_mapping)[1][0]


def _get_multi_lbls(imagefile):
    """
    Function that returns class labels for an image for multilabel classification.
    input: imagefile (Path)
    returns: labels (List[str])
    """
    xmlfile = (
        imagefile.parents[1]
        / "labels"
        / imagefile.name.replace("{ims}".format(ims=imagefile.suffix), ".xml")
    )
    labels = ET.parse(xmlfile).getroot().find("object").find("name").text
    labels = labels.split(",")
    return labels


def _check_esri_files(path):
    if (
        os.path.exists(path / "esri_model_definition.emd")
        and os.path.exists(path / "map.txt")
        and os.path.exists(path / "esri_accumulated_stats.json")
    ):
        return True

    return False


def _get_class_mapping(path, **kwargs):
    """getting class mapping from labels, incase esri definition files and class mapping is not provided"""
    dataset_type = kwargs.get("dataset_type", None)
    class_mapping = {}
    if dataset_type == "KITTI_rectangles":
        start_space = re.compile("^\s+")  # pattern to capture leading spaces
        spaces_to_be_replaced = re.compile(
            "(?<=\d)(\s+)(?=\d)"
        )  # pattern to capture spaces between numeric values

        for txtfile in os.listdir(path):
            if not txtfile.endswith(".txt"):
                continue
            with open(os.path.join(path, txtfile)) as f:
                lines = f.readlines()
            for line in lines:
                line = re.sub(start_space, "", line)
                lst = re.sub(spaces_to_be_replaced, ",", line).split(",")
                class_mapping[str(lst[0])] = str(lst[0])
    else:
        for xmlfile in os.listdir(path):
            if not xmlfile.endswith(".xml"):
                continue
            tree = ET.parse(os.path.join(path, xmlfile))
            xmlroot = tree.getroot()
            for tag_obj in xmlroot.findall("object"):
                class_mapping[tag_obj.find("name").text] = tag_obj.find("name").text

    return class_mapping

