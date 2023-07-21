from pathlib import Path
import types
import os
import torch
import torch.nn.functional as F
import numpy as np
import mmcv
from mmdet3d.models import build_detector
import logging
from mmcv.runner import auto_fp16


def get_backbone_channel(model_cfg, data):
    temp_model = build_detector(model_cfg).to(data.device)

    # x_batch, _ = data.one_batch(detach=False)
    x_batch = torch.rand(
        (data.max_point, data.num_features), dtype=torch.float32, device=data.device
    )
    x_batch[:, :3] = (x_batch[:, :3] - 0.5) / 0.5
    x_batch[:, :3] *= data.scale_factor

    voxels, num_points, coors = temp_model.voxelize([x_batch])
    voxel_features = temp_model.voxel_encoder(voxels, num_points, coors)
    batch_size = coors[-1, 0].item() + 1
    backbone_feature = temp_model.middle_encoder(voxel_features, coors, batch_size)

    return backbone_feature.shape[1]


def set_voxel_info(voxel_parms, data):
    voxel_parms["voxel_size"] = voxel_parms.get("voxel_size", [0.05, 0.05, 0.1])
    data.range = np.array(data.range)
    grid_size = torch.tensor(
        (data.range[3:] - data.range[:3]) / voxel_parms["voxel_size"]
    )
    data.range = data.range.tolist()
    voxel_parms["sparse_shape"] = torch.round(grid_size).long().tolist()[::-1]

    if not voxel_parms.get("max_voxels", False):
        no_of_voxels = np.prod(voxel_parms["sparse_shape"], dtype=np.uint64).tolist()
        voxel_parms["max_voxels"] = (no_of_voxels // 3000, no_of_voxels // 2000)
        voxel_parms["voxel_points"] = int(
            data.max_point // (voxel_parms["max_voxels"][0] * 0.3)
        )


def model_config(model_cfg, data, **kwargs):
    voxel_parms = kwargs.get("voxel_parms", {})
    set_voxel_info(voxel_parms, data)

    model_cfg.voxel_layer.voxel_size = voxel_parms["voxel_size"]
    model_cfg.voxel_layer.max_voxels = voxel_parms["max_voxels"]
    model_cfg.voxel_layer.max_num_points = voxel_parms["voxel_points"]
    model_cfg.voxel_layer.point_cloud_range = data.range

    model_cfg.voxel_encoder.num_features = data.num_features
    model_cfg.middle_encoder.in_channels = data.num_features

    # set correctly otherwise RuntimeError: CUDA error: an illegal memory access was encountered
    model_cfg.middle_encoder.sparse_shape = voxel_parms["sparse_shape"]

    model_cfg.backbone.in_channels = get_backbone_channel(model_cfg, data)

    model_cfg.bbox_head.num_classes = data.c
    model_cfg.bbox_head.bbox_coder.code_size = 7
    model_cfg.bbox_head.anchor_generator.ranges = data.anchor_range
    model_cfg.bbox_head.anchor_generator.sizes = data.average_box_size
    model_cfg.bbox_head.anchor_generator.rotations = [0.0, 1.57]

    return model_cfg


@auto_fp16(apply_to=("points",))
def forward_modified(self, input):
    if not self.prediction:
        losses = self.forward_train(**input)
        loss, log_vars = self._parse_losses(losses)

        loss = dict(loss=loss, log_vars=log_vars)
        output = None
        if not self.training:
            output = self.simple_test(input["points"], input["img_metas"])
        return output, loss
    else:
        return self.simple_test(input["points"], input["img_metas"])


@auto_fp16()
def forward_neck(self, x):
    assert len(x) == len(self.in_channels)
    ups = [deblock(x[i]) for i, deblock in enumerate(self.deblocks)]
    size = ups[0].shape[-2:]
    ups = [F.interpolate(up, size, mode="bilinear", align_corners=False) for up in ups]
    if len(ups) > 1:
        out = torch.cat(ups, dim=1)
    else:
        out = ups[0]
    return [out]


def get_model(data, **kwargs):
    logging.disable(logging.WARNING)

    config = kwargs.get("model")
    checkpoint = kwargs.get("model_weight", False)

    if os.path.exists(Path(config)):
        cfg = mmcv.Config.fromfile(config)
    else:
        import arcgis

        cfg_abs_path = (
            Path(arcgis.__file__).parent
            / "learn"
            / "_mmdet3d_config"
            / (config + ".{}".format("py"))
        )
        cfg = mmcv.Config.fromfile(cfg_abs_path)
        checkpoint = cfg.get("checkpoint", False)

    cfg.model = model_config(cfg.model, data, **kwargs)

    model = build_detector(cfg.model)

    if checkpoint:
        mmcv.runner.load_checkpoint(
            model, checkpoint, "cpu", False, logging.getLogger()
        )

    model.forward = types.MethodType(forward_modified, model)
    if cfg.model.neck.type == "SECONDFPN":
        model.neck.forward = types.MethodType(forward_neck, model.neck)

    model.prediction = False

    logging.disable(0)

    return model, cfg
