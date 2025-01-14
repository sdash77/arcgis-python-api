import torch
import matplotlib.pyplot as plt
import math
import numpy as np
from .common import get_nbatches, image_batch_stretcher
from .._utils.env import is_arcgispronotebook


def show_batch_labeled_tiles(self, rows=3, **kwargs):  # parameters adjusted in kwargs
    """
    This function randomly picks a few training chips and visualizes them.

    =====================   ===========================================
    **Parameter**            **Description**
    ---------------------   -------------------------------------------
    rows                    Optional Integer.
                            Number of rows to display.
                            Default: 3.
    ---------------------   -------------------------------------------
    alpha                   Optional Float.
                            Opacity of the lables for the corresponding
                            images. Values range between 0 and 1, where
                            1 means opaque.
    -------------------------------------------------------------------

    """
    from .._utils.common import denorm_x

    nrows = rows
    ncols = kwargs.get("ncols", nrows)
    # start_index = kwargs.get('start_index', 0) # Does not work with dataloader

    # Modify nrows and ncols according to the dataset
    n_items = kwargs.get("n_items", nrows * ncols)
    n_items = min(n_items, len(self.x))
    nrows = math.ceil(n_items / ncols)
    nbatches = math.ceil(n_items / self.batch_size)

    type_data_loader = kwargs.get(
        "data_loader", "training"
    )  # options : traininig, validation, testing
    if type_data_loader == "training":
        data_loader = self.train_dl
    elif type_data_loader == "validation":
        data_loader = self.valid_dl
    elif type_data_loader == "testing":
        data_loader = self.test_dl
    else:
        e = Exception(
            f"could not find {type_data_loader} in data. Please ensure that the data loader type is traininig, validation or testing "
        )
        raise (e)

    rgb_bands = kwargs.get("rgb_bands", self._symbology_rgb_bands)
    nodata = kwargs.get("nodata", 0)
    imsize = kwargs.get("imsize", 5)
    statistics_type = kwargs.get(
        "statistics_type", "dataset"
    )  # Accepted Values `dataset`, `DRA`
    stretch_type = kwargs.get(
        "stretch_type", "minmax"
    )  # Accepted Values `minmax`, `percentclip`

    e = Exception(
        "`rgb_bands` should be a valid band_order, list or tuple of length 3 or 1."
    )
    symbology_bands = []
    if not (len(rgb_bands) == 3 or len(rgb_bands) == 1):
        raise (e)
    for b in rgb_bands:
        if type(b) == str:
            b_index = self._bands.index(b)
        elif type(b) == int:
            self._bands[
                b
            ]  # To check if the band index specified by the user really exists.
            b_index = b
        else:
            raise (e)
        b_index = self._extract_bands.index(b_index)
        symbology_bands.append(b_index)

    # Get Batch
    x_batch, y_batch = get_nbatches(data_loader, nbatches)
    x_batch = torch.cat(x_batch)
    y_batch = torch.cat(y_batch)

    # Denormalize X
    x_batch = denorm_x(x_batch, self)

    # Extract RGB Bands
    symbology_x_batch = x_batch[:, symbology_bands]
    if stretch_type is not None:
        symbology_x_batch = image_batch_stretcher(
            symbology_x_batch, stretch_type, statistics_type
        )

    # Channel first to channel last and clamp float values to range 0 - 1 for plotting
    symbology_x_batch = symbology_x_batch.permute(0, 2, 3, 1)
    # Clamp float values to range 0 - 1
    if symbology_x_batch.mean() < 1:
        symbology_x_batch = symbology_x_batch.clamp(0, 1)

    # Squeeze channels if single channel (1, 224, 224) -> (224, 224)
    if symbology_x_batch.shape[-1] == 1:
        symbology_x_batch = symbology_x_batch.squeeze()

    # Get color Array
    color_array = self._multispectral_color_array

    # Size for plotting
    fig, axs = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=(ncols * imsize, nrows * imsize)
    )
    idx = 0
    for r in range(nrows):
        for c in range(ncols):
            if idx < symbology_x_batch.shape[0]:
                axi = axs
                if nrows == 1:
                    axi = axi
                else:
                    axi = axi[r]
                if ncols == 1:
                    axi = axi
                else:
                    axi = axi[c]
                axi.imshow(symbology_x_batch[idx].cpu().numpy())

                if self.dataset_type == "MultiLabeled_Tiles":
                    one_hot_labels = y_batch[idx].tolist()
                    from itertools import compress

                    labels = compress(self.classes, one_hot_labels)
                    title = ";".join(labels)
                else:
                    title = f"{self.classes[y_batch[idx].item()]}"

                axi.set_title(title)
                axi.axis("off")
            else:
                axs[r][c].axis("off")
            idx += 1
    if is_arcgispronotebook():
        plt.show()


# Function to plot hard examples for multilabel classification
# This function has been taken from fastai and modified to work with multispectral and rgb (ArcGISMSImage).
def plot_multi_top_losses_modified(
    self, samples=3, figsize=(8, 8), save_misclassified=False
):
    "Show images in `top_losses` along with their prediction, actual, loss, and probability of predicted class in a multilabeled dataset."
    if samples > 20:
        print("Max 20 samples")
        return
    predclass, truthlabels, losses = self.learn.get_preds(with_loss=True)
    # convert it to one hot labels
    predclass_label = (predclass > 0.5).float()
    num_classes = len(self.data.classes)
    num_valid_img = len(self.data.valid_ds)
    idx_img = [x for x in range(num_valid_img) for _ in range(num_classes)]
    converted_predclass_labels = []
    converted_truthclass_labels = []
    for row in predclass_label:
        converted_predclass_labels.append(
            [i if value == 1 else None for i, value in enumerate(row)]
        )
    for row in truthlabels:
        converted_truthclass_labels.append(
            [i if value == 1 else None for i, value in enumerate(row)]
        )
    from itertools import chain

    # Flatten the lists
    flattened_predclass_labels = list(chain.from_iterable(converted_predclass_labels))
    flattened_truthclass_labels = list(chain.from_iterable(converted_truthclass_labels))
    # combined_list will have at position 0 validation image id , 1 truth labels , 2 prediction  , 3 losses & 4 probability
    combined_list = []
    for num1 in range(len(losses)):
        if flattened_predclass_labels[num1] is not None:
            # checking the mismatch
            if flattened_truthclass_labels[num1] != flattened_predclass_labels[num1]:
                combined_list.append(
                    (
                        idx_img[num1],
                        flattened_truthclass_labels[num1],
                        flattened_predclass_labels[num1],
                        losses[num1],
                        predclass.view(-1)[num1],
                    )
                )

    mismatches = sorted(combined_list, key=lambda x: x[3].item(), reverse=True)
    print(
        f"{str(len(mismatches))} misclassified samples over {str(len(self.data.valid_ds))} samples in the validation set."
    )
    samples = min(samples, len(mismatches))
    from arcgis.learn._utils.common import ArcGISMSImage
    from itertools import compress

    for sampleN in range(samples):
        predictedclasses = ""
        predictedclasses = f"{predictedclasses} -- {str(r''.join(self.data.classes[mismatches[sampleN][2]]))}"
        imag = (self.data.valid_ds[mismatches[sampleN][0]])[0]
        imag = ArcGISMSImage.show(imag, return_ax=True)
        imag.set_title(
            f"""Incorrectly predicted as class: {predictedclasses} \nLoss: {mismatches[sampleN][3].numpy()}\nProbability: {mismatches[sampleN][4]}""",
            loc="left",
        )
        plt.show()
        if save_misclassified:
            return mismatches
