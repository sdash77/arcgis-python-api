import os
import sys
from pathlib import Path
import numpy as np
from torch.utils import data
from arcgis.learn._utils.common import ArcGISMSImage
from fastai.data_block import DataBunch
import random
import math
import types
from collections import defaultdict
from torch.utils.data import DataLoader
import torch
import json
import os
import multiprocessing
from .._utils.cyclegan import image_extensions
from .pix2pix_data import get_files, get_device
from fastprogress.fastprogress import progress_bar
from fastai.vision import random
from .._data import _prepare_working_dir
from .._utils.env import is_arcgispronotebook
from .._utils.common import get_top_padding


def max_min_normalization(data, max_num, min_num):
    nl_data = (data - min_num) / (max_num - min_num)
    return nl_data


def padding(data, window_size):
    [m, n, c] = data.shape
    start_id = int(np.floor(window_size / 2))
    out_shape = [m + window_size - 1, n + window_size - 1, c]
    if isinstance(data, np.ndarray):
        pad_data = np.zeros(out_shape, dtype=data.dtype)
    elif isinstance(data, torch.Tensor):
        pad_data = torch.zeros(out_shape, dtype=data.dtype, device=data.device)
    pad_data[start_id : start_id + m, start_id : start_id + n] = data
    return pad_data


def get_auto_workers():
    try:
        # Total logical CPUs
        cpu_count = os.cpu_count() or multiprocessing.cpu_count()
        # Leave some cores free for OS (e.g., 25%)
        workers = max(1, cpu_count - max(1, cpu_count // 4))
        return workers
    except:
        return 4


def samples_extraction(
    path, window_size, max_num, min_num, training_class_map, workers=None
):
    if workers is None:
        workers = get_auto_workers()  # auto decide

    save_dir = os.path.join(path, "DATA")
    os.makedirs(save_dir, exist_ok=True)
    images, labels = os.path.join(path, "images"), os.path.join(path, "labels")

    all_chips = [i for i in os.listdir(images) if i.endswith(".tif")]
    training_class_map = {v: k for k, v in training_class_map.items()}

    for k in progress_bar(all_chips, comment="Processing chips and Extracting samples"):
        HSI_data = ArcGISMSImage.open(os.path.join(images, k)).data.numpy()
        HSI_gt = ArcGISMSImage.open(os.path.join(labels, k)).data.numpy()[0]

        remapped = np.copy(HSI_gt)
        for old_val, new_val in training_class_map.items():
            remapped[HSI_gt == old_val] = new_val
        HSI_gt = remapped

        HSI_data = np.transpose(HSI_data, (1, 2, 0))
        HSI_data = max_min_normalization(HSI_data, max_num, min_num)
        s = window_size
        HSI_data = padding(HSI_data, s)

        coords = np.argwhere(HSI_gt > 0)
        labels_vec = HSI_gt[HSI_gt > 0]

        save_tasks, lines = [], []
        for (i, j), label in zip(coords, labels_vec):
            patch = HSI_data[i : i + s, j : j + s, :].transpose(2, 0, 1)[np.newaxis]
            save_name = os.path.join(save_dir, f"samples_{k[:-4]}_{i+1}_{j+1}.npy")
            save_tasks.append((save_name, patch))
            lines.append(f"{save_name} {int(label)}\n")

        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(lambda x: np.save(*x), save_tasks)
        data_list_path = os.path.join(save_dir, "data_list.txt")
        with open(data_list_path, "a") as f:
            f.writelines(lines)


def samples_division_cv(list_dir, val_split_pct):
    with open(list_dir) as f:
        samples_txt = f.readlines()
    label_dict = defaultdict(list)
    for line in samples_txt:
        path, label = line.strip().rsplit(" ", 1)
        label_dict[label].append(f"{path} {label}\n")
    test_entries = []
    test_set = set()
    sorted_labels = sorted(label_dict.keys(), key=lambda x: int(x))
    for label in sorted_labels:
        items = label_dict[label]
        sample_size = max(1, math.ceil(len(items) * val_split_pct))
        selected = random.sample(items, sample_size)
        test_entries.extend(selected)
        test_set.update(selected)
    train_entries = [line for line in samples_txt if line not in test_set]
    train_entries.sort(key=lambda x: int(x.strip().rsplit(" ", 1)[1]))
    test_entries.sort(key=lambda x: int(x.strip().rsplit(" ", 1)[1]))

    with open(os.path.join(os.path.dirname(list_dir), "data_list_test.txt"), "w") as f:
        f.writelines(test_entries)
    with open(os.path.join(os.path.dirname(list_dir), "data_list_train.txt"), "w") as f:
        f.writelines(train_entries)


class HyperspectralDataset(data.Dataset):
    def __init__(self, list_dir, path, augmentation=False):
        f = open(list_dir)
        self.list_txt = f.readlines()
        self.length = len(self.list_txt)
        self.au = augmentation
        self.path = path

    def __getitem__(self, index):
        sample_path = self.list_txt[index].split(" ")
        data_path = os.path.join(self.path, "DATA", sample_path[0].split("\\")[-1])
        label = sample_path[1][:-1]
        if not self.au:
            data = np.load(data_path)
        else:
            data = self.random_flip_lr(np.load(data_path))
            data = self.random_flip_tb(data)
            data = self.random_rot(data)
        label = int(label) - 1
        return torch.from_numpy(data).float(), label

    def __len__(self):
        return self.length

    def __repr__(self):
        item = self.__getitem__(0)
        return f"{self.__class__.__name__}, Tensor:{(item[0][0].shape)}, items:{self.length}"

    def random_flip_lr(self, data):
        if np.random.randint(0, 2):
            c, d, h, w = data.shape
            index = np.arange(w, 0, -1) - 1
            return data[:, :, :, index]
        else:
            return data

    def random_flip_tb(self, data):
        if np.random.randint(0, 2):
            c, d, h, w = data.shape
            index = np.arange(h, 0, -1) - 1
            return data[:, :, index, :]
        else:
            return data

    def random_rot(self, data):
        rot_k = np.random.randint(0, 4)
        return np.rot90(data, rot_k, (2, 3)).copy()


class ChipsDataset(data.Dataset):
    def __init__(self, path, imagelist_a, imagelist_b):
        self.path = path
        self.imagelist_a = imagelist_a
        self.imagelist_b = imagelist_b

    def __len__(self):
        return len(self.imagelist_b)

    def __getitem__(self, idx):

        image_A = ArcGISMSImage.open(self.imagelist_a[idx], imagery_type="MS")
        image_B = ArcGISMSImage.open(self.imagelist_b[idx], imagery_type="MS")

        return image_A.px, image_B.px


def create_train_val_sets(path, val_split_pct, **kwargs):
    path = Path(path)
    images_path = path / "images"
    labels_path = path / "labels"
    save_dir = path / "DATA"

    emd_stats = kwargs["emd_stats"]["AllTilesStats"]
    window_size = kwargs.get("window_size", 27)
    min_num = min(stat["Min"] for stat in emd_stats)
    max_num = max(stat["Max"] for stat in emd_stats)

    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
        samples_extraction(
            path, window_size, max_num, min_num, kwargs["training_class_map"]
        )
        samples_division_cv(save_dir / "data_list.txt", val_split_pct)

    data_list_train = save_dir / "data_list_train.txt"
    data_list_test = save_dir / "data_list_test.txt"

    train_dataset = HyperspectralDataset(data_list_train, path, True)
    test_dataset = HyperspectralDataset(data_list_test, path, False)

    images_A = get_files(images_path, extensions=image_extensions, recurse=True)
    images_B = get_files(labels_path, extensions=image_extensions, recurse=True)

    assert len(images_A) == len(images_B), "Mismatch between images and labels"

    zipped = list(zip(images_A, images_B))
    random.shuffle(zipped)

    split_index = round(len(zipped) * 0.1)
    val_pairs = zipped[:split_index]
    train_pairs = zipped[split_index:]

    trainChips_dataset = ChipsDataset(path, *zip(*train_pairs))
    testChips_dataset = ChipsDataset(path, *zip(*val_pairs))

    return (
        (train_dataset, test_dataset),
        (trainChips_dataset, testChips_dataset),
        max_num,
        min_num,
    )


def create_dataloaders(datasets, batch_size, dataloader_kwargs):
    dl_list = []
    for c, d in enumerate(datasets):
        dataloader_kwargs["shuffle"] = True
        dl = DataLoader(d, batch_size, **dataloader_kwargs)
        dl_list.append(dl)
    return dl_list


def show_batch(self, rows=4, rgb_bands=[0, 1, 2], alpha=0.5, **kwargs):
    """
    Show a batch of hyperspectral image chips with overlaid labels.

    Parameters:
    -----------
    rows : int
        Number of rows in the display grid (each with ncols columns).
    rgb_bands : list
        List of band indices to use as RGB for display.
    alpha : float
        Transparency level for the label overlay (0 to 1).
    """
    import matplotlib.pyplot as plt
    from .._utils.common import (
        denorm_x,
        dynamic_range_adjustment,
        get_symbology_bands,
        image_tensor_checks_plotting,
    )

    ncols = kwargs.get("ncols", 3)
    n_images = rows * ncols

    # Collect image-label pairs
    xs, ys = [], []
    for n, imgs in enumerate(self.Showbatchdata.train_ds):
        if n >= n_images:
            break
        xs.append(imgs[0])
        ys.append(imgs[1])

    if not xs:
        print("No images found in dataset.")
        return

    x_batch = torch.stack([x.data for x in xs])
    y_batch = torch.stack([y.data for y in ys])

    symbology_bands = rgb_bands
    symbology_x_batch = x_batch[:, symbology_bands]

    if kwargs.get("statistics_type", "dataset") == "DRA":
        symbology_x_batch = dynamic_range_adjustment(symbology_x_batch)

    symbology_x_batch = image_tensor_checks_plotting(symbology_x_batch)

    color_array = self._multispectral_color_array.clone()
    color_array[1:, 3] = alpha  # Apply transparency to labels

    # Plotting
    fig, axs = plt.subplots(nrows=rows, ncols=ncols, figsize=(ncols * 5, rows * 5))
    axs = axs.flatten() if n_images > 1 else [axs]
    inv_class_dict = {v: k for k, v in self.classes.items()}

    for i in range(len(axs)):
        ax = axs[i]
        ax.axis("off")

        if i < len(symbology_x_batch):
            img_np = symbology_x_batch[i].cpu().numpy()
            img_np = (img_np - img_np.min()) / (img_np.max() - img_np.min() + 1e-6)
            ax.imshow(img_np)

            label_mask = y_batch[i][0].long().to(color_array.device)

            lut = np.zeros(max(inv_class_dict.keys()) + 1, dtype=np.int32)
            for old_val, new_val in inv_class_dict.items():
                lut[old_val] = new_val
            label_mask = lut[label_mask]

            label_rgb = color_array[label_mask].cpu().numpy()
            ax.imshow(label_rgb, alpha=alpha)
        else:
            ax.set_visible(False)

    if is_arcgispronotebook():
        plt.show()


@torch.no_grad()
def predict_on_validation(net, window_size, max_min, r, t, batch_size=64):
    if isinstance(r, ArcGISMSImage):
        r = np.transpose(r.data, (1, 2, 0))  # [H, W, Bands]
    else:
        r = r.permute(1, 2, 0).cpu().numpy()  # convert from [C, H, W] to [H, W, C]

    if isinstance(t, ArcGISMSImage):
        t = t.data
    elif isinstance(t, torch.Tensor):
        t = t.cpu().numpy()

    net.eval()
    s = window_size
    hst_img, hst_label = r, t
    hst_img = max_min_normalization(hst_img, max_min[0], max_min[1])
    hst_img = padding(hst_img, s)
    m, n = hst_label.shape

    valid_positions = np.argwhere(hst_label > 0)
    total_samples = len(valid_positions)

    if total_samples == 0:
        return np.array([]), np.array([])

    y_pred_test = []
    y_test = []

    for idx in range(0, total_samples, batch_size):
        batch = valid_positions[idx : idx + batch_size]

        batch_data = []
        batch_label = []

        for i, j in batch:
            patch = hst_img[i : i + s, j : j + s, :]  # [H, W, Bands]
            patch = patch.transpose(2, 0, 1)  # [Bands, H, W]
            patch = patch[np.newaxis, ...]  # [1, Bands, H, W] → 1 channel
            batch_data.append(patch)
            batch_label.append(hst_label[i, j])

        hst_data = torch.tensor(
            batch_data, dtype=torch.float32
        ).cuda()  # [B, 1, D, H, W]
        outputs = net(hst_data)
        preds = torch.argmax(outputs, dim=1).cpu().numpy()  # [B]

        y_pred_test.append(preds)
        y_test.append(np.array(batch_label))

    y_pred_test = np.concatenate(y_pred_test)
    y_test = np.concatenate(y_test)
    return y_pred_test, y_test


def get_classification_map(y_pred, y):
    height = y.shape[0]
    width = y.shape[1]
    k = 0
    cls_labels = np.zeros((height, width))
    for i in range(height):
        for j in range(width):
            target = int(y[i, j])
            if target == 0:
                continue
            else:
                cls_labels[i][j] = y_pred[k] + 1
                k += 1

    return cls_labels


def show_results(self, rows=4, rgb_bands=[0, 1, 2], alpha=0.5, **kwargs):
    """
    Show prediction results with input, ground truth, and predicted label masks overlaid on input raster.

    Parameters:
    -----------
    rows : int
        Number of image-label pairs to show.
    rgb_bands : list
        List of band indices to use as RGB for display.
    alpha : float
        Transparency for overlay, if needed.
    """
    import matplotlib.pyplot as plt
    import torch
    import numpy as np

    top = kwargs.get("top", None)
    title_font_size = 16
    if top is None:
        top = get_top_padding(title_font_size=title_font_size, nrows=rows, imsize=5)

    kwargs["rgb_bands"] = rgb_bands
    xs, ys = [], []

    # Collect samples
    for n, imgs in enumerate(self._data.Showbatchdata.train_ds):
        if n >= rows:
            break
        xs.append(imgs[0])
        ys.append(imgs[1][0])

    if len(xs) == 0:
        print("No data found.")
        return

    ys_preds, ys_reals, xs_imgs = [], [], []

    training_class_map = {j: i for i, j in self._data._training_class_map.items()}

    for i, (x, y) in enumerate(zip(xs, ys)):
        y_pred, y_new = predict_on_validation(
            self.learn.model, self._data._window_size, self._data._max_min, x, y
        )
        y_real = y.data
        cls_labels = get_classification_map(y_pred, y)
        ys_preds.append(torch.tensor(cls_labels)[None])
        ys_reals.append(y_real[None])
        xs_imgs.append(x)

    color_array = self._data._multispectral_color_array.clone()
    color_array[1:, 3] = alpha  # apply alpha to all but background

    # Plotting: 2 columns (GT and Prediction) per row, both overlaid on input image
    fig, axs = plt.subplots(nrows=rows, ncols=2, figsize=(12, rows * 5))
    if rows == 1:
        axs = [axs]

    plt.subplots_adjust(top=top)
    fig.suptitle("Ground Truth / Predictions", fontsize=title_font_size)

    for k in range(rows):
        input_image = xs_imgs[k].data[rgb_bands].permute(1, 2, 0).cpu().numpy()
        input_image = (input_image - input_image.min()) / (
            input_image.max() - input_image.min()
        )

        for col, (label_tensor, title) in enumerate(
            [
                (ys_reals[k][0].long(), "Ground Truth"),
                (ys_preds[k][0].long(), "Prediction"),
            ]
        ):
            if col == 0:
                label_tensor = np.vectorize(training_class_map.get)(label_tensor)

            ax = axs[k][col] if rows > 1 else axs[col]

            overlay = color_array[label_tensor].cpu().numpy()

            ax.imshow(input_image)  # Show input RGB image
            ax.imshow(overlay, alpha=alpha)  # Overlay label map
            ax.axis("off")

    if is_arcgispronotebook():
        plt.show()


def prepare_hyperspec_data(
    path,
    batch_size,
    val_split_pct,
    working_dir,
    class_mapping,
    **kwargs,
):
    emd_path = os.path.join(path, "esri_model_definition.emd")
    with open(emd_path) as f:
        emd_stats = json.load(f)
    kwargs["emd_stats"] = emd_stats

    training_class_map = {n + 1: i["Value"] for n, i in enumerate(emd_stats["Classes"])}
    kwargs["training_class_map"] = training_class_map

    train_val_dataset, train_val_chips_dataset, max_num, min_num = (
        create_train_val_sets(path, val_split_pct, **kwargs)
    )

    num_workers = kwargs.get("num_workers", 0)
    is_windows = sys.platform == "win32"
    num_workers_final = num_workers if is_windows else max(os.cpu_count() - 4, 1)

    databunch_kwargs = {
        "drop_last": True,
        "num_workers": num_workers_final,
    }

    if is_windows and num_workers > 0:
        databunch_kwargs["persistent_workers"] = True

    train_dl, valid_dl = create_dataloaders(
        train_val_dataset, batch_size, databunch_kwargs
    )
    trainChips_dl, validChips_dl = create_dataloaders(
        train_val_chips_dataset, 1, databunch_kwargs
    )

    device = get_device()
    data = DataBunch(train_dl, valid_dl, device=device)
    data.Showbatchdata = DataBunch(trainChips_dl, validChips_dl, device=device)

    final_path = Path(os.path.abspath(working_dir)) if working_dir else Path(path)
    data.path = final_path
    data._temp_folder = _prepare_working_dir(final_path)

    original_classes = {n: i["Value"] for n, i in enumerate(emd_stats["Classes"])}
    if class_mapping:
        for k in original_classes:
            class_mapping.setdefault(int(k), str(k))
        data.classes = class_mapping
    else:
        data.classes = original_classes

    data.classes = dict(sorted(data.classes.items()))
    data._training_class_map = training_class_map
    data._num_classes = len([i for i in data.classes.values() if i != 0])
    data._dataset_type = "3DRCNet"
    data._n_channels = data.train_ds[0][0][0].shape[0]
    data._max_min = (max_num, min_num)
    data.show_batch = types.MethodType(show_batch, data)
    data._window_size = kwargs.get("window_size", 27)
    data.color_mapping = {
        (i.get("Value", 0) or i.get("ClassValue", 0)): i["Color"]
        for i in emd_stats.get("Classes", [])
    }

    data._multispectral_color_mapping = data.color_mapping
    if data._multispectral_color_mapping is None and data.class_mapping is not None:
        data._multispectral_color_mapping = {
            c: [-1, -1, -1] for c in data.class_mapping
        }
    if data._multispectral_color_mapping is not None and any(
        -1 in x for x in data._multispectral_color_mapping.values()
    ):
        random_color_list = np.random.randint(
            low=0, high=255, size=(len(data._multispectral_color_mapping), 3)
        ).tolist()
        for i, (c, v) in enumerate(data._multispectral_color_mapping.items()):
            if -1 in v:
                data._multispectral_color_mapping[c] = random_color_list[i]

    # prepare color array
    if data._multispectral_color_mapping is not None:
        alpha = kwargs.get("alpha", 0.7)
        color_array = (
            torch.tensor(list(data._multispectral_color_mapping.values())).float() / 255
        )
        alpha_tensor = torch.tensor([alpha] * len(color_array)).view(-1, 1).float()
        color_array = torch.cat([color_array, alpha_tensor], dim=-1)
        background_color = torch.tensor([[0, 0, 0, 0]]).float()
        data._multispectral_color_array = torch.cat([background_color, color_array])

    return data
