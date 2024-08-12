import timm
from timm.models.resnet import (
    BasicBlock,
    Bottleneck,
    build_model_with_cfg,
    ResNet,
    # _create_resnet,
)
from timm.models.resnet import default_cfgs as resnet_default_cfgs
from timm.models.registry import register_model


# extended configs for timm resnet models
def _res_cfg(url="", **kwargs):
    return {
        "url": url,
        "num_classes": 1000,
        "input_size": (3, 224, 224),
        "pool_size": (7, 7),
        "crop_pct": 0.875,
        "interpolation": "bilinear",
        "mean": timm.data.IMAGENET_DEFAULT_MEAN,
        "std": timm.data.IMAGENET_DEFAULT_STD,
        # "first_conv": "conv1",
        "classifier": "fc",
        **kwargs,
    }


hf_resnet_cfgs = {
    # ResNet18 and ResNet50 variants
    "resnet18_landsat_tm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_tm_toa_moco-1c691b4f.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_tm_toa_moco-1c691b4f.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_landsat_tm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_tm_toa_simclr-d2d38ace.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_tm_toa_simclr-d2d38ace.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_landsat_etm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_toa_moco-bb88689c.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_toa_moco-bb88689c.pth",
        input_size=(9, 224, 224),
    ),
    "resnet18_landsat_etm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_toa_simclr-4d813f79.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_toa_simclr-4d813f79.pth",
        input_size=(9, 224, 224),
    ),
    "resnet18_landsat_etm_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_sr_moco-4f078acd.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_sr_moco-4f078acd.pth",
        input_size=(6, 224, 224),
    ),
    "resnet18_landsat_etm_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_etm_sr_simclr-8e8543b4.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_etm_sr_simclr-8e8543b4.pth",
        input_size=(6, 224, 224),
    ),
    "resnet18_landsat_oli_tirs_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_tirs_toa_moco-a3002f51.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_tirs_toa_moco-a3002f51.pth",
        input_size=(11, 224, 224),
    ),
    "resnet18_landsat_oli_tirs_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_tirs_toa_simclr-b0635cc6.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_tirs_toa_simclr-b0635cc6.pth",
        input_size=(11, 224, 224),
    ),
    "resnet18_landsat_oli_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_sr_moco-660e82ed.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_sr_moco-660e82ed.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_landsat_oli_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet18_landsat_oli_sr_simclr-7bced5be.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet18_landsat_oli_sr_simclr-7bced5be.pth",
        input_size=(7, 224, 224),
    ),
    "resnet18_sentinel2_all_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet18_sentinel2_all_moco/resolve/5b8cddc9a14f3844350b7f40b85bcd32aed75918/resnet18_sentinel2_all_moco-59bfdff9.pth",
        hf_hub="torchgeo/resnet18_sentinel2_all_moco",
        filename="resnet18_sentinel2_all_moco-59bfdff9.pth",
        input_size=(13, 224, 224),
    ),
    "resnet18_sentinel2_rgb_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet18_sentinel2_rgb_moco/resolve/e1c032e7785fd0625224cdb6699aa138bb304eec/resnet18_sentinel2_rgb_moco-e3a335e3.pth",
        hf_hub="torchgeo/resnet18_sentinel2_rgb_moco",
        filename="resnet18_sentinel2_rgb_moco-e3a335e3.pth",
        input_size=(3, 224, 224),
    ),
    "resnet18_sentinel2_rgb_seco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet18_sentinel2_rgb_seco/resolve/f8dcee692cf7142163b55a5c197d981fe0e717a0/resnet18_sentinel2_rgb_seco-cefca942.pth",
        hf_hub="torchgeo/resnet18_sentinel2_rgb_seco",
        filename="resnet18_sentinel2_rgb_seco-cefca942.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_landsat_tm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_tm_toa_moco-ba1ce753.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_tm_toa_moco-ba1ce753.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_landsat_tm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_tm_toa_simclr-a1c93432.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_tm_toa_simclr-a1c93432.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_landsat_etm_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_toa_moco-e9a84d5a.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_toa_moco-e9a84d5a.pth",
        input_size=(9, 224, 224),
    ),
    "resnet50_landsat_etm_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_toa_simclr-70b5575f.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_toa_simclr-70b5575f.pth",
        input_size=(9, 224, 224),
    ),
    "resnet50_landsat_etm_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_sr_moco-1266cde3.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_sr_moco-1266cde3.pth",
        input_size=(6, 224, 224),
    ),
    "resnet50_landsat_etm_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_etm_sr_simclr-e5d185d7.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_etm_sr_simclr-e5d185d7.pth",
        input_size=(6, 224, 224),
    ),
    "resnet50_landsat_oli_tirs_toa_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_tirs_toa_moco-de7f5e0f.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_tirs_toa_moco-de7f5e0f.pth",
        input_size=(11, 224, 224),
    ),
    "resnet50_landsat_oli_tirs_toa_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_tirs_toa_simclr-030cebfe.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_tirs_toa_simclr-030cebfe.pth",
        input_size=(11, 224, 224),
    ),
    "resnet50_landsat_oli_sr_moco": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_sr_moco-ff580dad.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_sr_moco-ff580dad.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_landsat_oli_sr_simclr": _res_cfg(
        # url="https://hf.co/torchgeo/ssl4eo_landsat/resolve/1c88bb51b6e17a21dde5230738fa38b74bd74f76/resnet50_landsat_oli_sr_simclr-94f78913.pth",
        hf_hub="torchgeo/ssl4eo_landsat",
        filename="resnet50_landsat_oli_sr_simclr-94f78913.pth",
        input_size=(7, 224, 224),
    ),
    "resnet50_sentinel2_all_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_all_moco/resolve/da4f3c9dbe09272eb902f3b37f46635fa4726879/resnet50_sentinel2_all_moco-df8b932e.pth",
        hf_hub="torchgeo/resnet50_sentinel2_all_moco",
        filename="resnet50_sentinel2_all_moco-df8b932e.pth",
        input_size=(13, 224, 224),
    ),
    "resnet50_sentinel2_rgb_moco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_rgb_moco/resolve/efd9723b59a88e9dc1420dc1e96afb25b0630a3c/resnet50_sentinel2_rgb_moco-2b57ba8b.pth",
        hf_hub="torchgeo/resnet50_sentinel2_rgb_moco",
        filename="resnet50_sentinel2_rgb_moco-2b57ba8b.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_sentinel2_rgb_seco": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_rgb_seco/resolve/fbd07b02a8edb8fc1035f7957160deed4321c145/resnet50_sentinel2_rgb_seco-018bf397.pth",
        hf_hub="torchgeo/resnet50_sentinel2_rgb_seco",
        filename="resnet50_sentinel2_rgb_seco-018bf397.pth",
        input_size=(3, 224, 224),
    ),
    "resnet50_sentinel2_all_dino": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_sentinel2_all_dino/resolve/d7f14bf5530d70ac69d763e58e77e44dbecfec7c/resnet50_sentinel2_all_dino-d6c330e9.pth",
        hf_hub="torchgeo/resnet50_sentinel2_all_dino",
        filename="resnet50_sentinel2_all_dino-d6c330e9.pth",
        input_size=(13, 224, 224),
    ),
    "resnet50_fmow_rgb_gassl": _res_cfg(
        # url="https://hf.co/torchgeo/resnet50_fmow_rgb_gassl/resolve/fe8a91026cf9104f1e884316b8e8772d7af9052c/resnet50_fmow_rgb_gassl-da43d987.pth",
        hf_hub="torchgeo/resnet50_fmow_rgb_gassl",
        filename="resnet50_fmow_rgb_gassl-da43d987.pth",
        input_size=(3, 224, 224),
    ),
}


# resnet_updated_cfgs = resnet_default_cfgs.update(tg_resnet_cfgs)
resnet_updated_cfgs = resnet_default_cfgs | hf_resnet_cfgs

timm.models.resnet.default_cfgs = resnet_updated_cfgs


def resnet_checkpoint_filter_fn(state_dict, model):
    """make downloaded state dict keys' names same as model state keys' names for resnet models"""
    out_dict = model.state_dict().copy()
    for ix, (kx, vx) in zip(model.state_dict(), state_dict.items()):
        out_dict[ix] = vx

    return out_dict


def _create_resnet(variant, pretrained=False, **kwargs):
    return build_model_with_cfg(
        ResNet,
        variant,
        pretrained,
        default_cfg=resnet_updated_cfgs[variant],
        pretrained_filter_fn=resnet_checkpoint_filter_fn,
        **kwargs
    )


@register_model
def resnet18_landsat_tm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_tm_toa_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_tm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_tm_toa_simclr", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_toa_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_toa_simclr", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_sr_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_etm_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_etm_sr_simclr", pretrained, **model_args)


@register_model
def resnet18_landsat_oli_tirs_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet(
        "resnet18_landsat_oli_tirs_toa_moco", pretrained, **model_args
    )


@register_model
def resnet18_landsat_oli_tirs_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet(
        "resnet18_landsat_oli_tirs_toa_simclr", pretrained, **model_args
    )


@register_model
def resnet18_landsat_oli_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_oli_sr_moco", pretrained, **model_args)


@register_model
def resnet18_landsat_oli_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_landsat_oli_sr_simclr", pretrained, **model_args)


@register_model
def resnet18_sentinel2_all_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_sentinel2_all_moco", pretrained, **model_args)


@register_model
def resnet18_sentinel2_rgb_moco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_sentinel2_rgb_moco", pretrained, **model_args)


@register_model
def resnet18_sentinel2_rgb_seco(pretrained=False, **kwargs):
    model_args = dict(block=BasicBlock, layers=[2, 2, 2, 2], **kwargs)
    return _create_resnet("resnet18_sentinel2_rgb_seco", pretrained, **model_args)


@register_model
def resnet50_landsat_tm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_tm_toa_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_tm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_tm_toa_simclr", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_toa_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_toa_simclr", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_sr_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_etm_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_etm_sr_simclr", pretrained, **model_args)


@register_model
def resnet50_landsat_oli_tirs_toa_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet(
        "resnet50_landsat_oli_tirs_toa_moco", pretrained, **model_args
    )


@register_model
def resnet50_landsat_oli_tirs_toa_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet(
        "resnet50_landsat_oli_tirs_toa_simclr", pretrained, **model_args
    )


@register_model
def resnet50_landsat_oli_sr_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_oli_sr_moco", pretrained, **model_args)


@register_model
def resnet50_landsat_oli_sr_simclr(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_landsat_oli_sr_simclr", pretrained, **model_args)


@register_model
def resnet50_sentinel2_all_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_all_moco", pretrained, **model_args)


@register_model
def resnet50_sentinel2_rgb_moco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_rgb_moco", pretrained, **model_args)


@register_model
def resnet50_sentinel2_rgb_seco(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_rgb_seco", pretrained, **model_args)


@register_model
def resnet50_sentinel2_all_dino(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_sentinel2_all_dino", pretrained, **model_args)


@register_model
def resnet50_fmow_rgb_gassl(pretrained=False, **kwargs):
    model_args = dict(block=Bottleneck, layers=[3, 4, 6, 3], **kwargs)
    return _create_resnet("resnet50_fmow_rgb_gassl", pretrained, **model_args)
