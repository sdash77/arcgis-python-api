import types
from torch import nn
from ._arcgis_model import _get_backbone_meta
import logging
import os
import sys
import warnings

_logger = logging.getLogger(__name__)

try:
    from fastai.callbacks.hooks import hook_outputs, model_sizes
    from fastai.torch_core import one_param
    from fastai.vision import create_body, Image
    from fastai.layers import AdaptiveConcatPool2d
    from fastai.basic_data import DatasetType
    from fastai.callbacks import hook_output
    import torch.nn.functional as F
    from matplotlib import pyplot as plt
    import timm
    import fnmatch
    from timm.models.hub import (
        has_hf_hub,
        load_state_dict_from_hf,
        load_state_dict_from_url,
    )
    from timm.models.helpers import adapt_input_conv
    from torch.hub import get_dir
    import zipfile
    import torch

    HAS_FASTAI = True
except Exception as e:
    HAS_FASTAI = False


# same function with modification fastai.vision.learner._test_cnn
def test_cnn_trnsfrmr(m):
    if not isinstance(m, nn.Sequential) or not len(m) == 2:
        return False
    if hasattr(m[1], "_transformer"):
        return True
    return isinstance(m[1][0], (AdaptiveConcatPool2d, nn.AdaptiveAvgPool2d))


def reshape_tensor(x, h, w, embed_dim):
    return x[1:, :].reshape(h, w, embed_dim).permute(2, 0, 1)


# same function with modification fastai.vision.learner._cl_int_gradcam
def gradcam_trnsfrmr(
    self,
    idx,
    ds_type=None,
    heatmap_thresh=16,
    image=True,
):
    if ds_type == None:
        ds_type = DatasetType.Valid
    m = self.learn.model.eval()
    im, cl = self.learn.data.dl(ds_type).dataset[idx]
    cl = int(cl)
    xb, _ = self.data.one_item(
        im, detach=False, denorm=False
    )  # put into a minibatch of batch size = 1
    with hook_output(m[0]) as hook_a:
        with hook_output(m[0], grad=True) as hook_g:
            preds = m(xb)
            preds[0, int(cl)].backward()
    acts = hook_a.stored[0].cpu()  # activation maps
    grad = hook_g.stored[0][0].cpu()
    if hasattr(m[1], "_transformer"):
        h, w = m[0].patch_embed.grid_size
        embed_dim = m[0].embed_dim
        acts = reshape_tensor(acts, h, w, embed_dim)
        grad = reshape_tensor(grad, h, w, embed_dim)
    if (acts.shape[-1] * acts.shape[-2]) >= heatmap_thresh:
        grad_chan = grad.mean(1).mean(1)
        mult = F.relu(((acts * grad_chan[..., None, None])).sum(0))
        if image:
            xb_im = Image(xb[0])
            _, ax = plt.subplots()
            sz = list(xb_im.shape[-2:])
            xb_im.show(
                ax,
                title=f"pred. class: {self.pred_class[idx]}, actual class: {self.learn.data.classes[cl]}",
            )
            ax.imshow(
                mult,
                alpha=0.4,
                extent=(0, *sz[::-1], 0),
                interpolation="bilinear",
                cmap="magma",
            )
        return mult


hosted_weights = {
    "ecaresnet101d": "682eb6fca513415b9c5a6be61f1bc0f1",
    "ecaresnet101d_pruned": "d676dfa5ffa04732bc8ef58d2c85dd38",
    "ecaresnet269d": "df81aea21521475eba81658496dc6ace",
    "ecaresnet50d": "9f3235316a464885b4d3e5db2d5499b9",
    "ecaresnet50d_pruned": "eca1ccf9ea3145f3ae1cd257f290ef09",
    "ecaresnetlight": "680b9da80da54bbca20a6b7446b5a2df",
    "efficientnet_b1_pruned": "ed49c5e7bb804a05b877702e7ce12f40",
    "efficientnet_b2_pruned": "8eb218d51113449181f1f25efae9ab98",
    "efficientnet_b3_pruned": "b341d13252d244c591370c082bea9696",
    "hardcorenas_a": "af3227e5f48145c2a21c8cf76c3782e4",
    "hardcorenas_b": "9c14f1b482c5465ba5cc75772aeead60",
    "hardcorenas_c": "b758a9d94cb7402c942f2a51fdd99953",
    "hardcorenas_d": "8a927ea1f2c14b2dabaae423c21c193c",
    "hardcorenas_e": "1e7d664452cf4ce596bd5d1bfe776557",
    "hardcorenas_f": "f3a1f74efe244911b166d5456f2bba68",
    "legacy_senet154": "36266e6e22444ce299d76a57a6a817df",
    "legacy_seresnext101_32x4d": "884b2dd7093e49b4884fac2d23bc2386",
    "legacy_seresnext50_32x4d": "e54dc138f33f415984ccfbf6250e1e03",
    "nasnetalarge": "91404c5ecbd842948bb1507f1e313e4b",
    "regnetx_006": "e595c123a67c4a4f87f322b1af4b293c",
    "tf_efficientnet_b6_ns": "20d17115f5db4e11837b8d43e81d59da",
}


# same function with modification timm.models.helpers.load_pretrained
def load_timm_bckbn_pretrained(
    model,
    default_cfg=None,
    num_classes=1000,
    in_chans=3,
    filter_fn=None,
    strict=True,
    progress=True,
):
    default_cfg = default_cfg or getattr(model, "default_cfg", None) or {}
    pretrained_url = default_cfg.get("url", None)
    hf_hub_id = default_cfg.get("hf_hub", None)
    if not pretrained_url and not hf_hub_id:
        _logger.warning(
            "No pretrained weights exist for this model. Using random initialization."
        )
        return

    model_url = hosted_weights.get(default_cfg["architecture"], False)
    if model_url:
        model_dir = os.path.join(get_dir(), "checkpoints")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        cached_file = os.path.join(model_dir, pretrained_url.split("/")[-1])
        if not os.path.exists(cached_file):
            sys.stderr.write(
                'Downloading: "{}" pretrained weights to {}\n'.format(
                    default_cfg["architecture"], cached_file
                )
            )
            from arcgis.gis import GIS

            gis = GIS(set_active=False)
            item = gis.content.get(model_url)
            item.download(model_dir)
            zipped_file = os.path.join(
                model_dir, pretrained_url.split("/")[-1][:-3] + "zip"
            )
            with zipfile.ZipFile(zipped_file) as f:
                f.extractall(model_dir)
            os.remove(zipped_file)

        state_dict = torch.load(cached_file, map_location="cpu")

    elif hf_hub_id and has_hf_hub(necessary=not pretrained_url):
        _logger.info(f"Loading pretrained weights from Hugging Face hub ({hf_hub_id})")
        state_dict = load_state_dict_from_hf(hf_hub_id)
    else:
        _logger.info(f"Loading pretrained weights from url ({pretrained_url})")
        state_dict = load_state_dict_from_url(
            pretrained_url, progress=progress, map_location="cpu"
        )
    if filter_fn is not None:
        # for backwards compat with filter fn that take one arg, try one first, the two
        try:
            state_dict = filter_fn(state_dict)
        except TypeError:
            state_dict = filter_fn(state_dict, model)

    input_convs = default_cfg.get("first_conv", None)
    if input_convs is not None and in_chans != 3:
        if isinstance(input_convs, str):
            input_convs = (input_convs,)
        for input_conv_name in input_convs:
            weight_name = input_conv_name + ".weight"
            try:
                state_dict[weight_name] = adapt_input_conv(
                    in_chans, state_dict[weight_name]
                )
                _logger.info(
                    f"Converted input conv {input_conv_name} pretrained weights from 3 to {in_chans} channel(s)"
                )
            except NotImplementedError as e:
                del state_dict[weight_name]
                strict = False
                _logger.warning(
                    f"Unable to convert pretrained {input_conv_name} weights, using random init for this layer."
                )

    classifiers = default_cfg.get("classifier", None)
    label_offset = default_cfg.get("label_offset", 0)
    if classifiers is not None:
        if isinstance(classifiers, str):
            classifiers = (classifiers,)
        if num_classes != default_cfg["num_classes"]:
            for classifier_name in classifiers:
                # completely discard fully connected if model num_classes doesn't match pretrained weights
                del state_dict[classifier_name + ".weight"]
                del state_dict[classifier_name + ".bias"]
            strict = False
        elif label_offset > 0:
            for classifier_name in classifiers:
                # special case for pretrained weights with an extra background class in pretrained weights
                classifier_weight = state_dict[classifier_name + ".weight"]
                state_dict[classifier_name + ".weight"] = classifier_weight[
                    label_offset:
                ]
                classifier_bias = state_dict[classifier_name + ".bias"]
                state_dict[classifier_name + ".bias"] = classifier_bias[label_offset:]

    model.load_state_dict(state_dict, strict=strict)


def _default_split(m):
    return (m[1],)


def _tresnet_split(m):
    return (m[0].feature.body.layer4,)


def _squeezenet_split(m):
    return (m[0][0][5], m[0][0][8], m[1])


def _densenet_split(m):
    return (m[0][0][7], m[0][0][9])


def _vgg_split(m):
    return m[0][0][15]


def _rep_vgg(m):
    return m[0][1][2]


def _mobilenetv2_split(m):
    return m[1]


def _darknet_split(m):
    return m[0][1][4]


def _cspres_split(m):
    return m[0][1][3]


def _nfnet_split(m):
    return m[0][1][-1]


def _dpn_split(m):
    return m[0][0][-2]


def _esevovnet_split(m):
    return m[0][1][-1]


def _gernet_split(m):
    return m[0][1][-2]


def _modified_cut(m):
    def forward_modified(self, img):
        return self.forward_features(img)

    m.forward = types.MethodType(forward_modified, m)

    class TimmBackbone(nn.Module):
        def __init__(self, m):
            super(TimmBackbone, self).__init__()
            self.feature = m

        def forward(self, x):
            return self.feature.forward_features(x)

    return TimmBackbone(m)


timm_model_meta = {
    "default": {"cut": None, "split": _default_split},
    "squeezenet": {"cut": -1, "split": _squeezenet_split},
    "densenet": {"cut": None, "split": _densenet_split},
    "repvgg": {"cut": -2, "split": _rep_vgg},
    "vgg": {"cut": -2, "split": _vgg_split},
    "mobilenet": {"cut": None, "split": _mobilenetv2_split},
    "darknet": {"cut": None, "split": _darknet_split},
    "hrnet": {"cut": _modified_cut, "split": _default_split},
    "nasnet": {"cut": _modified_cut, "split": _default_split},
    "selecsls": {"cut": _modified_cut, "split": _default_split},
    "tresnet": {"cut": _modified_cut, "split": _tresnet_split},
    "cspres": {"cut": None, "split": _cspres_split},
    "nfnet": {"cut": None, "split": _nfnet_split},
    "dpn": {"cut": None, "split": _dpn_split},
    "ese_vovnet": {"cut": None, "split": _esevovnet_split},
    "gernet": {"cut": None, "split": _gernet_split},
}


def timm_config(arch):
    model_name = arch if type(arch) is str else arch.__name__
    model_key = [key for key in timm_model_meta if key in model_name] + ["default"]
    return timm_model_meta.get(model_key[0])


def filter_timm_models(flt=[]):
    models = timm.list_models(pretrained=True)
    # remove transformer models
    flt = [
        "*cait*",
        "*coat*",
        "*convit*",
        "*deit*",
        "*gmixer*",
        "*gmlp*",
        "*levit*",
        "*mixer*",
        "*pit*",
        "*resmlp*",
        "*swin*",
        "*tnt*",
        "*twins*",
        "*visformer*",
        "vit_*",
    ] + flt
    flt_models = []
    for f in flt:
        flt_models.extend(fnmatch.filter(models, f))
    return sorted(set(models) - set(flt_models))


def _get_feature_size(arch, cut, chip_size=(64, 64), channel_in=3):
    m = nn.Sequential(*create_body(arch, False, cut).children())
    if "tresnet" in arch.__module__:
        with hook_outputs(m) as hooks:
            dummy_batch = (
                one_param(m)
                .new(1, channel_in, *chip_size)
                .requires_grad_(False)
                .uniform_(-1.0, 1.0)
            )
            x = m.eval()(dummy_batch)
            return [o.stored.shape for o in hooks]
    else:
        return model_sizes(m, chip_size)


def get_backbone(backbone_fn, pretrained):
    if "timm" in backbone_fn.__module__:
        backbone_cut = timm_config(backbone_fn)["cut"]
    elif getattr(backbone_fn, "_is_multispectral", False):
        backbone_cut = _get_backbone_meta(backbone_fn.__name__)["cut"]
    else:
        backbone_cut = None

    return create_body(backbone_fn, pretrained, backbone_cut)


def forward_VisionTransformer(self, x):
    x = self.patch_embed(x)
    cls_token = self.cls_token.expand(x.shape[0], -1, -1)
    if self.dist_token is None:
        x = torch.cat((cls_token, x), dim=1)
    else:
        x = torch.cat((cls_token, self.dist_token.expand(x.shape[0], -1, -1), x), dim=1)
    x = self.pos_drop(x + self.pos_embed)

    x = self.blocks[:-1](x)

    return x


class VisionTransformerHead(nn.Module):
    def __init__(self, block, head, norm, dist_token, pre_logits, head_dist):
        super().__init__()
        self.block = block
        self.head = head
        self.norm = norm
        self.dist_token = dist_token
        self.pre_logits = pre_logits
        self.head_dist = head_dist
        self._transformer = True

    def forward(self, x):
        x = self.block(x)
        x = self.norm(x)
        if self.dist_token is None:
            x = self.pre_logits(x[:, 0])

        if self.head_dist is not None:
            x, x_dist = self.head(x[:, 0]), self.head_dist(x[:, 1])
            if self.training and not torch.jit.is_scripting():
                # during inference, return the average of both classifier predictions
                return x, x_dist
            else:
                return (x + x_dist) / 2
        else:
            x = self.head(x)
        return x


def create_trnsfrmr_model(bckbn_name, num_classes, img_size, pretrained):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logging.disable(logging.WARNING)
        trnsfrmr_bckbn = timm.create_model(
            bckbn_name,
            num_classes=num_classes,
            img_size=img_size,
            pretrained=pretrained,
        )
        logging.disable(logging.NOTSET)

    if trnsfrmr_bckbn.__class__.__name__ == "VisionTransformer":
        trnsfrmr_bckbn.forward = types.MethodType(
            forward_VisionTransformer, trnsfrmr_bckbn
        )

        trnsfrmr_head = VisionTransformerHead(
            trnsfrmr_bckbn.blocks[-1],
            trnsfrmr_bckbn.head,
            trnsfrmr_bckbn.norm,
            trnsfrmr_bckbn.dist_token,
            trnsfrmr_bckbn.pre_logits,
            trnsfrmr_bckbn.head_dist,
        )

    trnsfrmr_model = nn.Sequential(trnsfrmr_bckbn, trnsfrmr_head)
    return trnsfrmr_model
