try:
    from arcgis.learn.models._model_extension import ModelExtension
    from .._utils.detreg_data import get_coco_data
    from .._utils.coco_detection_utils import (
        box_cxcywh_to_xyxy,
        box_xyxy_to_cxcywh,
        plot_prediction,
    )
    from .._utils.coco_detection_utils import (
        make_coco_transforms,
        nested_tensor_from_tensor_list,
        plot_results,
    )
    from .._utils.common import (
        _get_emd_path,
        get_nbatches,
    )
    import numpy as np
    from pathlib import Path
    import json
    from IPython.utils import io
    import argparse
    import torch.distributed as dist
    from PIL import Image
    import math
    import torch
    import os
    import pickle
    import contextlib
    import copy
    import cv2
    from fastprogress.fastprogress import progress_bar
    from pycocotools.cocoeval import COCOeval
    from pycocotools.coco import COCO
    import pycocotools.mask as mask_util
    from matplotlib import pyplot as plt
    from ._arcgis_model import ArcGISModel
except:
    pass


class CustomDetReg:
    import torch

    def __init__(self, **kwargs):
        self.args = kwargs.get("args", "")
        self.classes = kwargs.get("classes", 1)
        from ._detr_object_detection.deformable_detr import build as build_model

        self.model_1, self.criterion_1, self.postprocessors = build_model(
            self.args, self.classes
        )

    def get_model(self, data, backbone=None, **kwargs):
        self.data = data
        return self.model_1

    def loss(self, model_output, *model_target):
        loss_dict = self.criterion_1(model_output, model_target)
        weight_dict = self.criterion_1.weight_dict
        losses = sum(
            loss_dict[k] * weight_dict[k] for k in loss_dict.keys() if k in weight_dict
        )
        loss_dict_reduced = reduce_dict(loss_dict)
        loss_dict_reduced_unscaled = {
            f"{k}_unscaled": v for k, v in loss_dict_reduced.items()
        }
        loss_dict_reduced_scaled = {
            k: v * weight_dict[k]
            for k, v in loss_dict_reduced.items()
            if k in weight_dict
        }
        losses_reduced_scaled = sum(loss_dict_reduced_scaled.values())

        loss_value = losses_reduced_scaled.item()
        if not math.isfinite(loss_value):
            print("Loss is {}, stopping training".format(loss_value))
            print(loss_dict_reduced)
            pass
        return losses

    def transform_input_multispectral(self, xb):
        return xb

    def transform_input(self, xb):

        transforms = make_coco_transforms("val")
        batch_input = xb.cpu().detach().numpy()
        num_batches = batch_input.shape[0]

        list_tensor = []
        for i in range(num_batches):
            batch_input_i = batch_input[i].transpose(1, 2, 0)
            batch_input_i = Image.fromarray(batch_input_i.astype(np.uint8))
            batch_input_i, _ = transforms(batch_input_i, None)
            batch_input_i = batch_input_i.to("cuda")
            list_tensor.append(batch_input_i)
        tensors_list = torch.stack(list_tensor, dim=0)
        batch_input_nested_tensor = nested_tensor_from_tensor_list(tensors_list)
        return batch_input_nested_tensor

    def lr_find(self):
        """
        Runs the Learning Rate Finder. Helps in choosing the
        optimum learning rate for training the model.
        """
        print(
            "The learning rate that works best with this model is found to be 2e-5. This learning rate will be used by default during the model training."
        )

    def on_batch_begin(self, learn, model_input_batch, model_target_batch, **kwargs):
        return model_input_batch, model_target_batch

    def post_process(
        self, pred, nms_overlap, thres, chip_size, device=torch.device("cuda")
    ):
        post_processed_pred = []
        pred_logits = pred["pred_logits"]
        pred_boxes = pred["pred_boxes"]
        pred_boxes_ = box_cxcywh_to_xyxy(pred_boxes.cpu()) * torch.Tensor(
            [224, 224, 224, 224]
        )
        for batch, p in enumerate(pred_boxes_):
            scores_temp = torch.sigmoid(pred_logits[batch][..., 1])
            I = np.argwhere(scores_temp.cpu().detach().numpy() > thres)
            I_temp = [i[0] for i in I]
            scores_thres = scores_temp[scores_temp > thres]
            bbox = np.vstack(p.cpu().detach().numpy())
            bbox = bbox[I_temp, :]
            label = [np.full(len(I_temp), 1, dtype=np.int32) for i, box in enumerate(p)]
            label = np.concatenate(label)

            bbox, label, score = (
                torch.from_numpy(bbox),
                torch.from_numpy(label),
                scores_thres,
            )
            # convert bboxes in range -1 to 1.
            bbox = bbox / (chip_size / 2) - 1
            # convert bboxes in format [y1,x1,y2,x2]
            bbox = torch.index_select(
                bbox.data.to(device), 1, torch.tensor([1, 0, 3, 2]).to(device)
            )
            # Append the tuple in list for each image
            post_processed_pred.append(
                (bbox.data.to(device), label.to(device), score.to(device))
            )

        return post_processed_pred

    def average_precision_score_detreg(self):
        """
        Computes average precision on the validation set for each class.
        """
        eval_res = self.evaluate_metric(
            self.model_1,
            self.criterion_1,
            self.postprocessors,
            self.data.valid_dl.dl,
            torch.device("cuda"),
            self.data.valid_ds,
        )

    @torch.no_grad()
    def evaluate_metric(
        self, model, criterion, postprocessors, data_loader, device, valid_ds
    ):
        model.eval()
        criterion.eval()
        iou_types = tuple(k for k in ("segm", "bbox") if k in postprocessors.keys())
        base_ds = get_coco_api_from_dataset(valid_ds)
        coco_evaluator = CocoEvaluator(base_ds, iou_types)
        iter = 0
        for samples, targets in progress_bar(data_loader, display=False):
            iter += 1
            if iter > 1:
                break
            samples = samples.to(device)
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            outputs = model(samples)
            loss_dict = criterion(outputs, targets)
            weight_dict = criterion.weight_dict

            # reduce losses over all GPUs for logging purposes
            loss_dict_reduced = reduce_dict(loss_dict)
            loss_dict_reduced_scaled = {
                k: v * weight_dict[k]
                for k, v in loss_dict_reduced.items()
                if k in weight_dict
            }
            loss_dict_reduced_unscaled = {
                f"{k}_unscaled": v for k, v in loss_dict_reduced.items()
            }
            orig_target_sizes = torch.stack([t["orig_size"] for t in targets], dim=0)
            results = postprocessors["bbox"](outputs, orig_target_sizes)
            res = {
                target["image_id"].item(): output
                for target, output in zip(targets, results)
            }
            if coco_evaluator is not None:
                coco_evaluator.update(res)
                coco_evaluator.synchronize_between_processes()
            if coco_evaluator is not None:
                coco_evaluator.accumulate()
                coco_evaluator.summarize()
        return coco_evaluator

    def _show_results(self, rows=5, **kwargs):
        """
        Displays the results of a trained model on a part of the validation set.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        rows                    Optional int. Number of rows of results
                                to be displayed.
        =====================   ===========================================

        """
        self.model_1.eval()
        self.criterion_1.eval()
        proc = 0
        samples, targets = get_nbatches(self.data.valid_dl.dl, 2)
        num_val_samples = len(self.data.valid_ds)
        rows = rows if rows < num_val_samples else num_val_samples
        fig, ax = plt.subplots(rows, 2, figsize=(10, rows * 5))
        fig.suptitle("Ground Truth / Predictions", fontsize=16)
        top = 1 - (math.sqrt(16) / math.sqrt(100 * rows * 5))
        plt.subplots_adjust(top=top)
        for i in range(2):
            sample_batch = samples[i].to(torch.device("cuda"))
            target_batch = [
                {k: v.to(torch.device("cuda")) for k, v in t.items()}
                for t in targets[i]
            ]
            outputs = self.model_1(sample_batch)

            # for samples, targets in self.data.valid_dl.dl:
            #    samples = samples.to(torch.device("cuda"))
            #    targets = [
            #        {k: v.to(torch.device("cuda")) for k, v in t.items()} for t in targets
            #    ]
            num_samples = len(target_batch)
            # outputs = self.model_1(samples)
            for sample in range(num_samples):
                if proc >= rows:
                    return
                top_k = len(target_batch[sample]["boxes"])
                indices = (
                    outputs["pred_logits"][sample]
                    .softmax(-1)[..., 1]
                    .sort(descending=True)[1][:top_k]
                )
                predictied_boxes = torch.stack(
                    [outputs["pred_boxes"][sample][i] for i in indices]
                ).unsqueeze(0)
                logits = torch.stack(
                    [outputs["pred_logits"][sample][i] for i in indices]
                ).unsqueeze(0)
                img = sample_batch.tensors[sample].cpu().permute(1, 2, 0).numpy()
                img = img * np.array([0.229, 0.224, 0.225]) + np.array(
                    [0.485, 0.456, 0.406]
                )
                img = img * 255
                img = img.astype("uint8")
                h, w = img.shape[:-1]
                boxes_ss = get_ss_res(img, h, w, top_k)
                # plot_prediction(samples.tensors[0:1], boxes_ss, torch.zeros(1, boxes_ss.shape[1], 4).to(logits), ax[0],
                # plot_prob=False)
                # ax[0].set_title('Selective Search')
                plot_prediction(
                    sample_batch.tensors[sample : sample + 1],
                    predictied_boxes,
                    logits,
                    ax[proc, 1] if num_val_samples > 1 else ax[1],
                    plot_prob=False,
                )
                # ax[proc, 1].set_title("Prediction") if num_val_samples > 1 else ax[1].set_title("Prediction")
                # ax[proc, 1].set_anchor('W')
                plot_prediction(
                    sample_batch.tensors[sample : sample + 1],
                    target_batch[sample]["boxes"].unsqueeze(0),
                    torch.zeros(1, target_batch[sample]["boxes"].shape[0], 4).to(
                        logits
                    ),
                    ax[proc, 0] if num_val_samples > 1 else ax[0],
                    plot_prob=False,
                )
                # ax[proc, 0].set_title("Ground Truth") if num_val_samples else ax[0].set_title("Ground Truth")
                # ax[proc, 0].set_anchor('W')
                proc = proc + 1
            for i in range(2):
                for j in range(proc + 1):
                    ax[j, i].set_aspect("equal") if num_val_samples else ax[
                        i
                    ].set_aspect("equal")
                    ax[j, i].set_axis_off() if num_val_samples else ax[i].set_axis_off()

    def predict(self, path, threshold=0.5):
        """
        Runs prediction on an Image. This method is only supported for RGB images.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        image_path              Required. Path to the image file to make the
                                predictions on.
        ---------------------   -------------------------------------------
        threshold               Optional float. The probability above which
                                a detection will be considered valid.
                                Default value - 0.5
        =====================   ===========================================
        """
        transforms = make_coco_transforms("val")
        im = Image.open(path)
        im_t, _ = transforms(im, None)
        im_t = im_t.to("cuda")
        img_1 = nested_tensor_from_tensor_list([im_t])
        res = self.model_1(img_1)
        scores_temp = torch.sigmoid(res["pred_logits"][..., 1])
        pred_boxes = res["pred_boxes"]
        pred_boxes_cpu = pred_boxes.cpu()
        img_w, img_h = im.size
        pred_boxes_ = box_cxcywh_to_xyxy(pred_boxes_cpu) * torch.Tensor(
            [img_w, img_h, img_w, img_h]
        )
        # I = scores.argsort(descending=True)  # sort by model confidence
        scores_temp_np = scores_temp.cpu().detach().numpy()
        I = np.argwhere(scores_temp_np > threshold)[:, 1]
        # pred_boxes_ = pred_boxes_[0, I[0, :3]]  # pick top 3 proposals
        pred_boxes_ = pred_boxes_[0, I]
        scores_ = scores_temp_np[0, I]

        plt.figure()
        plot_results(np.array(im), scores_, pred_boxes_, plt.gca(), norm=False)
        plt.axis("off")
        plt.show()


class DETReg(ModelExtension):
    """
    =============================   =============================================
    **Argument**                    **Description**
    -----------------------------   ---------------------------------------------
    data                            Required fastai Databunch. Returned data object from
                                    ``prepare_data`` function. This model supports only
                                    RGB imagery exported in PASCAL_VOC format.
    -----------------------------   ---------------------------------------------
    pretrained_path                 Optional string. Path where pre-trained model is
                                    saved.
    =============================   =============================================

    :return: ``DETReg`` Object
    """

    def __init__(self, data, pretrained_path=None):
        parser = argparse.ArgumentParser(
            "Deformable DETR training and evaluation script",
            parents=[self.get_args_parser()],
        )
        args = parser.parse_args(args=[])
        args.coco_path = os.path.join(args.data_root, "MSCoco")
        args.orig_data = data
        self.coco_data = data
        if not hasattr(data, "_is_empty"):
            with io.capture_output() as captured:
                self.coco_data = get_coco_data(data, args.coco_path)
        model = super().__init__(
            self.coco_data,
            CustomDetReg,
            args=args,
            pretrained_path=pretrained_path,
            classes=data.c,
        )
        # if pretrained_path:
        #    model.load(pretrained_path)
        return model

    @staticmethod
    def supported_datasets():
        return ["PASCAL_VOC_rectangles"]

    def fit(
        self,
        epochs=10,
        lr=2e-5,
        one_cycle=True,
        early_stopping=False,
        checkpoint=True,  # "all", "best", True, False ("best" and True are same.)
        tensorboard=False,
        monitor="valid_loss",  # whatever is passed here, earlystopping and checkpointing will use that.
        **kwargs,
    ):
        """
        Train the model for the specified number of epochs and using the
        specified learning rates

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        epochs                  Required integer. Number of cycles of training
                                on the data. Increase it if underfitting.
        ---------------------   -------------------------------------------
        lr                      Optional float or slice of floats. Learning rate
                                to be used for training the model. If ``lr=None``,
                                an optimal learning rate is automatically deduced
                                for training the model.
        ---------------------   -------------------------------------------
        one_cycle               Optional boolean. Parameter to select 1cycle
                                learning rate schedule. If set to `False` no
                                learning rate schedule is used.
        ---------------------   -------------------------------------------
        early_stopping          Optional boolean. Parameter to add early stopping.
                                If set to 'True' training will stop if parameter
                                `monitor` value stops improving for 5 epochs.
                                A minimum difference of 0.001 is required for
                                it to be considered an improvement.
        ---------------------   -------------------------------------------
        checkpoint              Optional boolean or string.
                                Parameter to save checkpoint during training.
                                If set to `True` the best model
                                based on `monitor` will be saved during
                                training. If set to 'all', all checkpoints
                                are saved. If set to False, checkpointing will
                                be off. Setting this parameter loads the best
                                model at the end of training.
        ---------------------   -------------------------------------------
        tensorboard             Optional boolean. Parameter to write the training log.
                                If set to 'True' the log will be saved at
                                <dataset-path>/training_log which can be visualized in
                                tensorboard. Required tensorboardx version=2.1

                                The default value is 'False'.
                                **Note - Not applicable for Text Models
        ---------------------   -------------------------------------------
        monitor                 Optional string. Parameter specifies
                                which metric to monitor while checkpointing
                                and early stopping. Defaults to 'valid_loss'. Value
                                should be one of the metric that is displayed in
                                the training table. Use `{model_name}.available_metrics`
                                to list the available metrics to set here. Currently
                                supports only valid_loss.
        =====================   ===========================================
        """
        return ArcGISModel.fit(
            self,
            epochs=epochs,
            lr=lr,
            one_cycle=True,
            early_stopping=early_stopping,
            checkpoint=checkpoint,
            tensorboard=tensorboard,
            monitor="valid_loss",
            **kwargs,
        )

    def save(
        self,
        name_or_path,
        publish=False,
        gis=None,
        compute_metrics=True,
        save_optimizer=False,
        save_inference_file=True,
        **kwargs,
    ):
        """
        Saves the model weights, creates an Esri Model Definition and Deep
        Learning Package zip for deployment to Image Server or ArcGIS Pro.
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        name_or_path            Required string. Name of the model to save. It
                                stores it at the pre-defined location. If path
                                is passed then it stores at the specified path
                                with model name as directory name and creates
                                all the intermediate directories.
        ---------------------   -------------------------------------------
        publish                 Optional boolean. Publishes the DLPK as an item.
        ---------------------   -------------------------------------------
        gis                     Optional GIS Object. Used for publishing the item.
                                If not specified then active gis user is taken.
        ---------------------   -------------------------------------------
        compute_metrics         Optional boolean. Used for computing model
                                metrics.
        ---------------------   -------------------------------------------
        save_optimizer          Optional boolean. Used for saving the model-optimizer
                                state along with the model. Default is set to False
        ---------------------   -------------------------------------------
        save_inference_file     Optional boolean. Used for saving the inference file
                                along with the model.
                                If False, the model will not work with ArcGIS Pro 2.6
                                or earlier. Default is set to True.
        =====================   ===========================================
        """
        return ArcGISModel._save(
            self,
            name_or_path,
            framework="PyTorch",
            publish=publish,
            gis=gis,
            compute_metrics=False,
            save_optimizer=save_optimizer,
            save_inference_file=save_inference_file,
            **kwargs,
        )

    # def ap_score(self):
    #    self._model_conf.average_precision_score_detreg()

    def get_args_parser(self):
        parser = argparse.ArgumentParser("Deformable DETR Detector", add_help=False)
        parser.add_argument("--lr", default=2e-4, type=float)
        parser.add_argument("--max_prop", default=30, type=int)
        parser.add_argument(
            "--lr_backbone_names", default=["backbone.0"], type=str, nargs="+"
        )
        parser.add_argument("--lr_backbone", default=2e-5, type=float)
        parser.add_argument(
            "--lr_linear_proj_names",
            default=["reference_points", "sampling_offsets"],
            type=str,
            nargs="+",
        )
        parser.add_argument("--lr_linear_proj_mult", default=0.1, type=float)
        parser.add_argument("--batch_size", default=4, type=int)
        parser.add_argument("--weight_decay", default=1e-4, type=float)
        parser.add_argument("--epochs", default=50, type=int)
        parser.add_argument("--lr_drop", default=40, type=int)
        parser.add_argument("--lr_drop_epochs", default=None, type=int, nargs="+")
        parser.add_argument(
            "--clip_max_norm",
            default=0.1,
            type=float,
            help="gradient clipping max norm",
        )
        parser.add_argument("--sgd", action="store_true")
        parser.add_argument("--filter_pct", type=float, default=-1)

        # Variants of Deformable DETR
        parser.add_argument("--with_box_refine", default=False, action="store_true")
        parser.add_argument("--two_stage", default=False, action="store_true")
        parser.add_argument(
            "--strategy",
            default="topk",
            type=str,
            choices=["topk", "mc_1", "mc_2", "mc_3", "mc_4", "random_sample", "random"],
        )
        parser.add_argument(
            "--obj_embedding_head",
            default="intermediate",
            type=str,
            choices=["intermediate", "head"],
        )

        # Model parameters
        parser.add_argument(
            "--frozen_weights",
            type=str,
            default=None,
            help="Path to the pretrained model. If set, only the mask head will be trained",
        )

        # * Backbone
        parser.add_argument(
            "--backbone",
            default="resnet50",
            type=str,
            help="Name of the convolutional backbone to use",
        )
        parser.add_argument(
            "--dilation",
            action="store_true",
            help="If true, we replace stride with dilation in the last convolutional block (DC5)",
        )
        parser.add_argument(
            "--position_embedding",
            default="sine",
            type=str,
            choices=("sine", "learned"),
            help="Type of positional embedding to use on top of the image features",
        )
        parser.add_argument(
            "--position_embedding_scale",
            default=2 * np.pi,
            type=float,
            help="position / size * scale",
        )
        parser.add_argument(
            "--num_feature_levels", default=4, type=int, help="number of feature levels"
        )

        # * Transformer
        parser.add_argument(
            "--enc_layers",
            default=6,
            type=int,
            help="Number of encoding layers in the transformer",
        )
        parser.add_argument(
            "--dec_layers",
            default=6,
            type=int,
            help="Number of decoding layers in the transformer",
        )
        parser.add_argument(
            "--dim_feedforward",
            default=1024,
            type=int,
            help="Intermediate size of the feedforward layers in the transformer blocks",
        )
        parser.add_argument(
            "--hidden_dim",
            default=256,
            type=int,
            help="Size of the embeddings (dimension of the transformer)",
        )
        parser.add_argument(
            "--dropout",
            default=0.1,
            type=float,
            help="Dropout applied in the transformer",
        )
        parser.add_argument(
            "--nheads",
            default=8,
            type=int,
            help="Number of attention heads inside the transformer's attentions",
        )
        parser.add_argument(
            "--num_queries", default=100, type=int, help="Number of query slots"
        )
        parser.add_argument("--dec_n_points", default=4, type=int)
        parser.add_argument("--enc_n_points", default=4, type=int)
        parser.add_argument(
            "--pretrain", default="", help="initialized from the pre-training model"
        )
        parser.add_argument("--load_backbone", default="swav", type=str)

        # * Segmentation
        parser.add_argument(
            "--masks",
            action="store_true",
            help="Train segmentation head if the flag is provided",
        )

        # Loss
        parser.add_argument(
            "--no_aux_loss",
            dest="aux_loss",
            action="store_false",
            help="Disables auxiliary decoding losses (loss at each layer)",
        )

        # * Matcher
        parser.add_argument(
            "--set_cost_class",
            default=2,
            type=float,
            help="Class coefficient in the matching cost",
        )
        parser.add_argument(
            "--set_cost_bbox",
            default=5,
            type=float,
            help="L1 box coefficient in the matching cost",
        )
        parser.add_argument(
            "--set_cost_giou",
            default=2,
            type=float,
            help="giou box coefficient in the matching cost",
        )
        parser.add_argument(
            "--object_embedding_loss_coeff",
            default=1,
            type=float,
            help="object_embedding_loss_coef box coefficient in the matching cost",
        )
        # * Loss coefficients
        parser.add_argument("--mask_loss_coef", default=1, type=float)
        parser.add_argument("--dice_loss_coef", default=1, type=float)
        parser.add_argument("--cls_loss_coef", default=2, type=float)
        parser.add_argument("--bbox_loss_coef", default=5, type=float)
        parser.add_argument("--giou_loss_coef", default=2, type=float)
        parser.add_argument("--focal_alpha", default=0.25, type=float)

        # dataset parameters
        parser.add_argument("--dataset_file", default="coco")
        parser.add_argument("--dataset", default="imagenet")
        parser.add_argument("--data_root", default="data")
        parser.add_argument("--coco_panoptic_path", type=str)
        parser.add_argument("--remove_difficult", action="store_true")

        parser.add_argument(
            "--output_dir", default="", help="path where to save, empty for no saving"
        )
        parser.add_argument(
            "--cache_path",
            default="cache/ilsvrc/ss_box_cache",
            help="where to store the cache",
        )
        parser.add_argument(
            "--device", default="cuda", help="device to use for training / testing"
        )
        parser.add_argument("--seed", default=42, type=int)
        parser.add_argument("--resume", default="", help="resume from checkpoint")
        parser.add_argument("--eval_every", default=1, type=int)
        parser.add_argument(
            "--start_epoch", default=0, type=int, metavar="N", help="start epoch"
        )
        parser.add_argument("--eval", action="store_true")
        parser.add_argument("--viz", action="store_true")
        parser.add_argument("--num_workers", default=2, type=int)
        parser.add_argument(
            "--cache_mode",
            default=False,
            action="store_true",
            help="whether to cache images on memory",
        )
        parser.add_argument(
            "--object_embedding_loss",
            default=False,
            action="store_true",
            help="whether to use this loss",
        )
        return parser

    @classmethod
    def from_model(cls, data, emd_path):

        """
        Creates a Single Shot Detector from an Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        data                    Required fastai Databunch or None. Returned data
                                object from `prepare_data` function or None for
                                inferencing.
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Esri Model Definition
                                file.
        =====================   ===========================================

        :return: `DETReg` Object
        """
        # if not HAS_FASTAI:
        #    _raise_fastai_import_error(import_exception=import_exception)
        emd_path = _get_emd_path(emd_path)
        emd = json.load(open(emd_path))
        model_file = Path(emd["ModelFile"])
        backbone = emd.get("backbone", "resnet34")
        chip_size = emd["ImageWidth"]

        if not model_file.is_absolute():
            model_file = emd_path.parent / model_file

        class_mapping = {i["Value"]: i["Name"] for i in emd["Classes"]}

        resize_to = emd.get("resize_to")
        if isinstance(resize_to, list):
            resize_to = (resize_to[0], resize_to[1])

        # Tensorflow support
        backend = emd.get("ModelParameters", {}).get("backend", "pytorch")
        if backend == "tensorflow":
            backbone = emd["ModelParameters"].get("backbone", "ResNet50")

        data_passed = True
        # Create an image Staunch for when loading the model using emd (without training data)
        if data is None:
            data_passed = False
            train_tfms = []
            val_tfms = []
            ds_tfms = (train_tfms, val_tfms)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)

                sd = ImageList([], path=emd_path.parent.parent.parent).split_by_idx([])
                data = (
                    sd.label_const(
                        0,
                        label_cls=ObjectDetectionCategoryList,
                        classes=list(class_mapping.values()),
                    )
                    .transform(ds_tfms)
                    .databunch(device=_get_device())
                    .normalize(imagenet_stats)
                )

            data.chip_size = chip_size
            data.class_mapping = class_mapping
            data.classes = ["background"] + list(class_mapping.values())
            data._is_empty = True
            # Add 1 for background class
            data.c += 1
            data.emd_path = emd_path
            data.emd = emd
            # data = get_multispectral_data_params_from_emd(data, emd)

        data.resize_to = resize_to

        detreg = cls(data, pretrained_path=str(model_file))

        if not data_passed:
            detreg.learn.data.single_ds.classes = detreg._data.classes
            detreg.learn.data.single_ds.y.classes = detreg._data.classes

        return detreg


def is_dist_avail_and_initialized():
    if not dist.is_available():
        return False
    if not dist.is_initialized():
        return False
    return True


def get_world_size():
    if not is_dist_avail_and_initialized():
        return 1
    return dist.get_world_size()


def all_gather(data):
    """
    Run all_gather on arbitrary picklable data (not necessarily tensors)
    Args:
        data: any picklable object
    Returns:
        list[data]: list of data gathered from each rank
    """
    world_size = get_world_size()
    if world_size == 1:
        return [data]

    # serialized to a Tensor
    buffer = pickle.dumps(data)
    storage = torch.ByteStorage.from_buffer(buffer)
    tensor = torch.ByteTensor(storage).to("cuda")

    # obtain Tensor size of each rank
    local_size = torch.tensor([tensor.numel()], device="cuda")
    size_list = [torch.tensor([0], device="cuda") for _ in range(world_size)]
    dist.all_gather(size_list, local_size)
    size_list = [int(size.item()) for size in size_list]
    max_size = max(size_list)

    # receiving Tensor from all ranks
    # we pad the tensor because torch all_gather does not support
    # gathering tensors of different shapes
    tensor_list = []
    for _ in size_list:
        tensor_list.append(torch.empty((max_size,), dtype=torch.uint8, device="cuda"))
    if local_size != max_size:
        padding = torch.empty(
            size=(max_size - local_size,), dtype=torch.uint8, device="cuda"
        )
        tensor = torch.cat((tensor, padding), dim=0)
    dist.all_gather(tensor_list, tensor)

    data_list = []
    for size, tensor in zip(size_list, tensor_list):
        buffer = tensor.cpu().numpy().tobytes()[:size]
        data_list.append(pickle.loads(buffer))

    return data_list


def reduce_dict(input_dict, average=True):
    """
    Args:
        input_dict (dict): all the values will be reduced
        average (bool): whether to do average or sum
    Reduce the values in the dictionary from all processes so that all processes
    have the averaged results. Returns a dict with the same fields as
    input_dict, after reduction.
    """
    world_size = get_world_size()
    if world_size < 2:
        return input_dict
    with torch.no_grad():
        names = []
        values = []
        # sort the keys so that they are consistent across processes
        for k in sorted(input_dict.keys()):
            names.append(k)
            values.append(input_dict[k])
        values = torch.stack(values, dim=0)
        dist.all_reduce(values)
        if average:
            values /= world_size
        reduced_dict = {k: v for k, v in zip(names, values)}
    return reduced_dict


class CocoEvaluator(object):
    def __init__(self, coco_gt, iou_types):
        assert isinstance(iou_types, (list, tuple))
        coco_gt = copy.deepcopy(coco_gt)
        self.coco_gt = coco_gt

        self.iou_types = iou_types
        self.coco_eval = {}
        for iou_type in iou_types:
            self.coco_eval[iou_type] = COCOeval(coco_gt, iouType=iou_type)

        self.img_ids = []
        self.eval_imgs = {k: [] for k in iou_types}

    def update(self, predictions):
        img_ids = list(np.unique(list(predictions.keys())))
        self.img_ids.extend(img_ids)

        for iou_type in self.iou_types:
            results = self.prepare(predictions, iou_type)

            # suppress pycocotools prints
            with open(os.devnull, "w") as devnull:
                with contextlib.redirect_stdout(devnull):
                    coco_dt = COCO.loadRes(self.coco_gt, results) if results else COCO()
            coco_eval = self.coco_eval[iou_type]

            coco_eval.cocoDt = coco_dt
            coco_eval.params.imgIds = list(img_ids)
            img_ids, eval_imgs = evaluate(coco_eval)

            self.eval_imgs[iou_type].append(eval_imgs)

    def synchronize_between_processes(self):
        for iou_type in self.iou_types:
            self.eval_imgs[iou_type] = np.concatenate(self.eval_imgs[iou_type], 2)
            create_common_coco_eval(
                self.coco_eval[iou_type], self.img_ids, self.eval_imgs[iou_type]
            )

    def accumulate(self):
        for coco_eval in self.coco_eval.values():
            coco_eval.accumulate()

    def summarize(self):
        for iou_type, coco_eval in self.coco_eval.items():
            print("IoU metric: {}".format(iou_type))
            coco_eval.summarize()

    def prepare(self, predictions, iou_type):
        if iou_type == "bbox":
            return self.prepare_for_coco_detection(predictions)
        elif iou_type == "segm":
            return self.prepare_for_coco_segmentation(predictions)
        elif iou_type == "keypoints":
            return self.prepare_for_coco_keypoint(predictions)
        else:
            raise ValueError("Unknown iou type {}".format(iou_type))

    def prepare_for_coco_detection(self, predictions):
        coco_results = []
        for original_id, prediction in predictions.items():
            if len(prediction) == 0:
                continue

            boxes = prediction["boxes"]
            boxes = convert_to_xywh(boxes).tolist()
            scores = prediction["scores"].tolist()
            labels = prediction["labels"].tolist()

            coco_results.extend(
                [
                    {
                        "image_id": original_id,
                        "category_id": labels[k],
                        "bbox": box,
                        "score": scores[k],
                    }
                    for k, box in enumerate(boxes)
                ]
            )
        return coco_results

    def prepare_for_coco_segmentation(self, predictions):
        coco_results = []
        for original_id, prediction in predictions.items():
            if len(prediction) == 0:
                continue

            scores = prediction["scores"]
            labels = prediction["labels"]
            masks = prediction["masks"]

            masks = masks > 0.5

            scores = prediction["scores"].tolist()
            labels = prediction["labels"].tolist()

            rles = [
                mask_util.encode(
                    np.array(mask[0, :, :, np.newaxis], dtype=np.uint8, order="F")
                )[0]
                for mask in masks
            ]
            for rle in rles:
                rle["counts"] = rle["counts"].decode("utf-8")

            coco_results.extend(
                [
                    {
                        "image_id": original_id,
                        "category_id": labels[k],
                        "segmentation": rle,
                        "score": scores[k],
                    }
                    for k, rle in enumerate(rles)
                ]
            )
        return coco_results

    def prepare_for_coco_keypoint(self, predictions):
        coco_results = []
        for original_id, prediction in predictions.items():
            if len(prediction) == 0:
                continue

            boxes = prediction["boxes"]
            boxes = convert_to_xywh(boxes).tolist()
            scores = prediction["scores"].tolist()
            labels = prediction["labels"].tolist()
            keypoints = prediction["keypoints"]
            keypoints = keypoints.flatten(start_dim=1).tolist()

            coco_results.extend(
                [
                    {
                        "image_id": original_id,
                        "category_id": labels[k],
                        "keypoints": keypoint,
                        "score": scores[k],
                    }
                    for k, keypoint in enumerate(keypoints)
                ]
            )
        return coco_results


def convert_to_xywh(boxes):
    xmin, ymin, xmax, ymax = boxes.unbind(1)
    return torch.stack((xmin, ymin, xmax - xmin, ymax - ymin), dim=1)


def merge(img_ids, eval_imgs):
    all_img_ids = all_gather(img_ids)
    all_eval_imgs = all_gather(eval_imgs)

    merged_img_ids = []
    for p in all_img_ids:
        merged_img_ids.extend(p)

    merged_eval_imgs = []
    for p in all_eval_imgs:
        merged_eval_imgs.append(p)

    merged_img_ids = np.array(merged_img_ids)
    merged_eval_imgs = np.concatenate(merged_eval_imgs, 2)

    # keep only unique (and in sorted order) images
    merged_img_ids, idx = np.unique(merged_img_ids, return_index=True)
    merged_eval_imgs = merged_eval_imgs[..., idx]

    return merged_img_ids, merged_eval_imgs


def create_common_coco_eval(coco_eval, img_ids, eval_imgs):
    img_ids, eval_imgs = merge(img_ids, eval_imgs)
    img_ids = list(img_ids)
    eval_imgs = list(eval_imgs.flatten())

    coco_eval.evalImgs = eval_imgs
    coco_eval.params.imgIds = img_ids
    coco_eval._paramsEval = copy.deepcopy(coco_eval.params)


#################################################################
# From pycocotools, just removed the prints and fixed
# a Python3 bug about unicode not defined
#################################################################


def evaluate(self):
    """
    Run per image evaluation on given images and store results (a list of dict) in self.evalImgs
    :return: None
    """
    # tic = time.time()
    # print('Running per image evaluation...')
    p = self.params
    # add backward compatibility if useSegm is specified in params
    if p.useSegm is not None:
        p.iouType = "segm" if p.useSegm == 1 else "bbox"
        print(
            "useSegm (deprecated) is not None. Running {} evaluation".format(p.iouType)
        )
    # print('Evaluate annotation type *{}*'.format(p.iouType))
    p.imgIds = list(np.unique(p.imgIds))
    if p.useCats:
        p.catIds = list(np.unique(p.catIds))
    p.maxDets = sorted(p.maxDets)
    self.params = p

    self._prepare()
    # loop through images, area range, max detection number
    catIds = p.catIds if p.useCats else [-1]

    if p.iouType == "segm" or p.iouType == "bbox":
        computeIoU = self.computeIoU
    elif p.iouType == "keypoints":
        computeIoU = self.computeOks
    self.ious = {
        (imgId, catId): computeIoU(imgId, catId)
        for imgId in p.imgIds
        for catId in catIds
    }

    evaluateImg = self.evaluateImg
    maxDet = p.maxDets[-1]
    evalImgs = [
        evaluateImg(imgId, catId, areaRng, maxDet)
        for catId in catIds
        for areaRng in p.areaRng
        for imgId in p.imgIds
    ]
    # this is NOT in the pycocotools code, but could be done outside
    evalImgs = np.asarray(evalImgs).reshape(len(catIds), len(p.areaRng), len(p.imgIds))
    self._paramsEval = copy.deepcopy(self.params)
    # toc = time.time()
    # print('DONE (t={:0.2f}s).'.format(toc-tic))
    return p.imgIds, evalImgs


def get_coco_api_from_dataset(dataset):
    return dataset.coco


def selective_search(img, h, w, res_size=128):
    img_det = np.array(img)
    ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()

    if res_size is not None:
        img_det = cv2.resize(img_det, (res_size, res_size))

    ss.setBaseImage(img_det)
    ss.switchToSelectiveSearchFast()
    boxes = ss.process().astype("float32")

    if res_size is not None:
        boxes /= res_size
        boxes *= np.array([w, h, w, h])

    boxes[..., 2] = boxes[..., 0] + boxes[..., 2]
    boxes[..., 3] = boxes[..., 1] + boxes[..., 3]
    return boxes


def get_ss_res(img, h, w, top_k):
    boxes = selective_search(img, h, w)[:top_k]
    boxes = torch.tensor(boxes).unsqueeze(0)
    boxes = box_xyxy_to_cxcywh(boxes) / torch.tensor([w, h, w, h])
    return boxes
