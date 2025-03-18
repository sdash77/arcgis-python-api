# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Dynamic One-For-All (DOFA) models."""

from functools import partial
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init
from timm.models.vision_transformer import Block
from torch import Tensor
import logging
import warnings
from ._mmlab_utils import load_mmlab_checkpoint
import math


def get_abs_pos(abs_pos, has_cls_token, hw):
    """
    Calculate absolute positional embeddings. If needed, resize embeddings and remove cls_token
        dimension for the original embeddings.
    Args:
        abs_pos (Tensor): absolute positional embeddings with (1, num_position, C).
        has_cls_token (bool): If true, has 1 embedding in abs_pos for cls token.
        hw (Tuple): size of input image tokens.

    Returns:
        Absolute positional embeddings after processing with shape (1, H, W, C)
    """
    imgsize = int(math.sqrt(hw))
    assert imgsize * imgsize == hw
    if has_cls_token:
        abs_pos = abs_pos[:, 1:, :]
    xy_num = abs_pos.shape[1]
    size = int(math.sqrt(xy_num))
    assert size * size == xy_num

    if size != imgsize:
        new_abs_pos = F.interpolate(
            abs_pos.reshape(1, size, size, -1).permute(0, 3, 1, 2),
            size=(imgsize, imgsize),
            mode="bicubic",
            align_corners=False,
        )

        return new_abs_pos.permute(0, 2, 3, 1).reshape(1, imgsize * imgsize, -1)

    else:
        return abs_pos


def position_embedding(embed_dim: int, pos: Tensor) -> Tensor:
    """Compute the 1D sine/cosine position embedding.

    Args:
        embed_dim: Output dimension D for each position. Must be even.
        pos: A list of positions to be encoded, of size (M,).

    Returns:
        Position embeddings of size (M, D).

    Raises:
        AssertionError: If *embed_dim* is not even.
    """
    assert embed_dim % 2 == 0
    omega = torch.arange(embed_dim // 2, dtype=torch.float32, device=pos.device)
    omega /= embed_dim / 2.0
    omega = 1.0 / 10000**omega  # (D/2,)

    pos = pos.reshape(-1)  # (M,)

    out = torch.einsum("m,d->md", pos, omega)  # (M, D/2), outer product

    emb_sin = torch.sin(out)  # (M, D/2)
    emb_cos = torch.cos(out)  # (M, D/2)

    emb = torch.cat([emb_sin, emb_cos], dim=1)  # (M, D)
    return emb


class TransformerWeightGenerator(nn.Module):
    """Dynamic weight generator for DOFA."""

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        embed_dim: int,
        num_heads: int = 4,
        num_layers: int = 1,
    ) -> None:
        """Initialize a new TransformerWeightGenerator instance.

        Args:
            input_dim: Input dimensions.
            output_dim: Output dimensions.
            embed_dim: Embedding dimensions.
            num_heads: Number of heads.
            num_layers: Number of layers.
        """
        super().__init__()

        self.input_dim = input_dim
        self.output_dim = output_dim
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.num_layers = num_layers

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=input_dim,
            nhead=num_heads,
            activation="gelu",
            norm_first=False,
            batch_first=False,
            dropout=False,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers, enable_nested_tensor=False
        )

        # Linear layer to map transformer output to desired weight shape
        self.fc_weight = nn.Linear(input_dim, output_dim)
        self.fc_bias = nn.Linear(input_dim, embed_dim)
        self.wt_num = 128
        self.weight_tokens = nn.Parameter(torch.empty([self.wt_num, input_dim]))
        self.bias_token = nn.Parameter(torch.empty([1, input_dim]))

        # timm's trunc_normal_(std=.02) is effectively normal_(std=0.02) as cutoff is
        # too big (2.)
        torch.nn.init.normal_(self.weight_tokens, std=0.02)
        torch.nn.init.normal_(self.bias_token, std=0.02)

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """Forward pass of the model.

        Args:
            x: Input mini-batch of size (seq_len, batch, input_dim).

        Returns:
            Weight and bias.
        """
        pos_wave = x
        x = torch.cat([self.weight_tokens, pos_wave], dim=0)
        x = torch.cat([x, self.bias_token], dim=0)
        transformer_output = self.transformer_encoder(x)
        weights = self.fc_weight(transformer_output[self.wt_num : -1] + pos_wave)
        # Using the last output to generate bias
        bias = self.fc_bias(transformer_output[-1])
        return weights, bias


class FCResLayer(nn.Module):
    """Fully-connected residual layer."""

    def __init__(self, linear_size: int = 128) -> None:
        """Initialize a new FCResLayer instance.

        Args:
            linear_size: Size of linear layer.
        """
        super().__init__()
        self.l_size = linear_size
        self.nonlin1 = nn.ReLU(inplace=True)
        self.nonlin2 = nn.ReLU(inplace=True)
        self.w1 = nn.Linear(self.l_size, self.l_size)
        self.w2 = nn.Linear(self.l_size, self.l_size)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass of the model.

        Args:
            x: Input mini-batch.

        Returns:
            Output of the model.
        """
        y = self.w1(x)
        y = self.nonlin1(y)
        y = self.w2(y)
        y = self.nonlin2(y)
        out: Tensor = x + y
        return out


class DOFAEmbedding(nn.Module):
    """Dynamic One-For-All (DOFA) embedding."""

    def __init__(
        self,
        dynamic_embed_dim,
        kernel_size=3,
        embed_dim=1024,
        wavelengths=3,
        flatten=True,
    ):
        """Initialize a new DOFAEmbedding instance.

        Args:
            dynamic_embed_dim: Dimensions of dynamic weight generator.
            kernel_size: Kernel size of the depth-wise convolution.
            embed_dim: Embedding dimensions.
        """
        super().__init__()
        self.dynamic_embed_dim = dynamic_embed_dim
        self.kernel_size = kernel_size
        self.embed_dim = embed_dim
        self._num_kernel = self.kernel_size * self.kernel_size * self.embed_dim
        self.patch_size = (kernel_size, kernel_size)
        self.num_patches = -1
        self.wavelengths = torch.tensor(wavelengths).float()
        self.flatten = flatten

        self.weight_generator = TransformerWeightGenerator(
            dynamic_embed_dim, self._num_kernel, embed_dim
        )
        self.scaler = 0.01

        self.fclayer = FCResLayer(dynamic_embed_dim)

        self._init_weights()

    def _init_weight(self, m: object) -> None:
        """Initialize weights of a single layer.

        Args:
            m: A single layer.
        """
        if isinstance(m, nn.Linear):
            init.xavier_uniform_(m.weight)
            m.bias.data.fill_(0.01)

    def _init_weights(self):
        """Initialize weights of all layers."""
        self.weight_generator.apply(self._init_weight)
        self.fclayer.apply(self._init_weight)

    def forward(self, x):
        """Forward pass of the model.

        Args:
            x: Input mini-batch.

        Return:
            Output mini-batch and wavelengths.
        """
        self.wavelengths = self.wavelengths.to(x.device)

        # wv_feats: 9,128 -> 9, 3x3x3
        waves = position_embedding(self.dynamic_embed_dim, self.wavelengths * 1000)
        waves = self.fclayer(waves)
        weight, bias = self.weight_generator(waves)  # 3x3x3
        dynamic_weight = weight.view(
            self.wavelengths.size(0), self.kernel_size, self.kernel_size, self.embed_dim
        )

        dynamic_weight = dynamic_weight.permute([3, 0, 1, 2])

        if bias is not None:
            bias = bias.view([self.embed_dim]) * self.scaler

        weights = dynamic_weight * self.scaler

        x = F.conv2d(
            x, weights, bias=bias, stride=self.kernel_size, padding=1, dilation=1
        )

        if self.flatten:
            x = x.flatten(2).transpose(1, 2)  # BCHW -> BNC
        else:
            x = x.permute(0, 2, 3, 1)  # BCHW -> BHWC
        return x


class DOFA(nn.Module):
    """Dynamic One-For-All (DOFA) model.

    Reference implementation:

    * https://github.com/zhu-xlab/DOFA

    If you use this model in your research, please cite the following paper:

    * https://arxiv.org/abs/2403.15356

    .. versionadded:: 0.6
    """

    def __init__(
        self,
        img_size: int = 224,
        patch_size: int = 16,
        # drop_rate: float = 0.0,
        embed_dim: int = 1024,
        depth: int = 24,
        num_heads: int = 16,
        dynamic_embed_dim: int = 128,
        num_classes: int | None = None,
        # global_pool: bool = False,
        mlp_ratio: float = 4.0,
        norm_layer: type[nn.Module] = partial(nn.LayerNorm, eps=1e-6),  # type: ignore[assignment]
        wavelengths: list[float] | None = None,
        is_clf: bool = False,
        pretrained: bool = True,
        pretrained_path: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize a new DOFA instance.

        Args:
            img_size: Input image size.
            patch_size: Patch size.
            drop_rate: Head dropout rate.
            embed_dim: Transformer embedding dimension.
            depth: Depth of transformer.
            num_heads: Number of attention heads.
            dynamic_embed_dim: Dimensions of dynamic weight generator.
            num_classes: Number of classes for classification head.
            global_pool: Whether or not to perform global pooling.
            mlp_ratio: Ratio of MLP hidden dim to embedding dim.
            norm_layer: Normalization layer.
            wavelengths: List of floats, wavelengths of dataset. Should not be None
        """
        super().__init__()

        self.img_size = img_size
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.depth = depth
        self.num_heads = num_heads
        self.dynamic_embed_dim = dynamic_embed_dim
        self.mlp_ratio = mlp_ratio
        self.wavelengths = wavelengths
        self._is_dofa = True
        self.out_channels = embed_dim
        # self.norm = norm_layer(embed_dim)
        self.is_clf = is_clf
        self.num_classes = num_classes

        self._band_names = kwargs.get("band_names", None)

        self.qa_idx = None

        if self._band_names is not None:
            cleaned_bandnames = [
                band_name.lower().replace("_", "").replace(" ", "")
                for band_name in self._band_names
            ]
            if "qa" in cleaned_bandnames:
                self.qa_idx = cleaned_bandnames.index("qa")
                self.wavelengths = (
                    wavelengths[: self.qa_idx] + wavelengths[self.qa_idx + 1 :]
                )

        self.output_shape = dict(channels=embed_dim, stride=patch_size)
        ####################################################

        in_chans = self.output_shape["channels"]
        self.scale_factors = 4.0
        out_stride = self.output_shape["stride"] // self.scale_factors

        # --------------------------------------------------------------------------
        # MAE encoder specifics
        self.patch_embed = DOFAEmbedding(
            dynamic_embed_dim=128,
            kernel_size=16,
            embed_dim=embed_dim,
            wavelengths=self.wavelengths,
        )
        self.num_patches = (img_size // patch_size) ** 2
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        # ---------------------------------------------------------------------------
        self.pos_embed = nn.Parameter(
            torch.zeros(1, self.num_patches + 1, embed_dim), requires_grad=False
        )  # fixed sin-cos embedding

        self.blocks = nn.ModuleList(
            [
                Block(
                    embed_dim,
                    num_heads,
                    mlp_ratio,
                    qkv_bias=True,
                    norm_layer=norm_layer,
                )
                for i in range(depth)
            ]
        )

        self.norm = norm_layer(embed_dim)

        if self.is_clf:
            self.head = (
                nn.Linear(embed_dim, num_classes) if num_classes > 0 else nn.Identity()
            )
        else:
            self.upsample = nn.Sequential(
                nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
                nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
                # nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
                # nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
            )

        if pretrained:
            logging.disable(logging.WARNING)
            load_mmlab_checkpoint(self, pretrained_path)
            logging.disable(0)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass of the model.

        Args:
            x: Input mini-batch.
            wavelengths: Wavelengths of each spectral band (μm).

        Returns:
            Output mini-batch.
        """

        if self.qa_idx is not None:
            x = torch.cat([x[:, : self.qa_idx], x[:, self.qa_idx + 1 :]], dim=1)

        # embed patches
        wavelist = torch.tensor(self.wavelengths, device=x.device).float()

        x = self.patch_embed(x)  # , wavelist)

        abs_pos_embed = get_abs_pos(self.pos_embed, True, x.shape[1])

        x = x + abs_pos_embed

        if self.is_clf:
            cls_token = self.cls_token + self.pos_embed[:, :1, :]
            cls_tokens = cls_token.expand(x.shape[0], -1, -1)
            x = torch.cat((cls_tokens, x), dim=1)

        # apply Transformer blocks
        for block in self.blocks:
            x = block(x)

        x = self.norm(x)
        outcome = x

        if self.is_clf:
            outcome = self.head(outcome[:, 0])
        else:
            batch_size, num_patches, hidden_dim = outcome.shape
            patch_size = int(num_patches**0.5)
            outcome = outcome.permute(0, 2, 1).reshape(
                batch_size, hidden_dim, patch_size, patch_size
            )

            outcome = self.upsample(outcome)

        return outcome


dofa_config = dict(
    dofa_base=dict(
        patch_size=16,
        embed_dim=768,
        depth=12,
        num_heads=12,
        pretrained_path="https://hf.co/torchgeo/dofa/resolve/b8db318b64a90b9e085ec04ba8851233c5893666/dofa_base_patch16_224-a0275954.pth",
    ),
    dofa_large=dict(
        patch_size=16,
        embed_dim=1024,
        depth=24,
        num_heads=16,
        pretrained_path="https://hf.co/torchgeo/dofa/resolve/b8db318b64a90b9e085ec04ba8851233c5893666/dofa_large_patch16_224-0ff904d3.pth",
    ),
)


dofa_backbones_downstream = list(dofa_config.keys())


class DofaBackboneFastai(nn.Module):
    def __init__(self, backbone):
        super().__init__()
        self.base_net = backbone
        in_chans = backbone.output_shape["channels"]
        self.scale_factors = 4.0
        out_stride = backbone.output_shape["stride"] // self.scale_factors
        self.output_shape = dict(channels=in_chans, stride=out_stride)

        self.dummy = nn.Sequential(
            nn.Conv2d(in_chans, in_chans, kernel_size=1, bias=False),
            nn.MaxPool2d(kernel_size=2),
        )

    def forward(self, x):
        out = self.base_net(x)
        return out


def dofa_backbone(
    backbone_name,
    pretrained=True,
    img_size=224,
    wavelengths=[0.48, 0.56, 0.64],
    is_clf=False,
    num_classes=None,
    **kwargs,
):

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logging.disable(logging.WARNING)
        if backbone_name in dofa_config.keys():
            backbone_cfg = dofa_config[backbone_name]
            backbone = DOFA(
                img_size,
                wavelengths=wavelengths,
                pretrained=pretrained,
                is_clf=is_clf,
                num_classes=num_classes,
                **backbone_cfg,
                **kwargs,
            )
            backbone_fpn = DofaBackboneFastai(backbone=backbone)

            backbone_fpn.__name__ = backbone_name
        logging.disable(0)

    return backbone_fpn
