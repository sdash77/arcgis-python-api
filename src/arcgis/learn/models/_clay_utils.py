import math
import os
import random
import torchvision

torchvision.disable_beta_transforms_warning()
from collections import OrderedDict
import timm
import torch
import torch.nn.functional as F
from einops import rearrange, reduce, repeat
from torch import nn
from torchvision.transforms import v2
from torch import Tensor
from typing import Any, List, Tuple, Dict

import logging
import warnings


torch.set_float32_matmul_precision("medium")
os.environ["TORCH_CUDNN_V8_API_DISABLED"] = "1"


############################## utils ##############################
"""
Code from https://github.com/lucidrains/vit-pytorch/blob/main/vit_pytorch/simple_vit.py

"""

import torch


def posemb_sincos_2d(h, w, dim, temperature: int = 10000, dtype=torch.float32):
    y, x = torch.meshgrid(torch.arange(h), torch.arange(w), indexing="ij")
    assert (dim % 4) == 0, "feature dimension must be multiple of 4 for sincos emb"
    omega = torch.arange(dim // 4) / (dim // 4 - 1)
    omega = 1.0 / (temperature**omega)

    y = y.flatten()[:, None] * omega[None, :]
    x = x.flatten()[:, None] * omega[None, :]
    pe = torch.cat((x.sin(), x.cos(), y.sin(), y.cos()), dim=1)
    return pe.type(dtype)


def posemb_sincos_2d_with_gsd(
    h, w, dim, gsd=1.0, temperature: int = 10000, dtype=torch.float32
):
    y, x = torch.meshgrid(torch.arange(h), torch.arange(w), indexing="ij")
    assert (dim % 4) == 0, "feature dimension must be multiple of 4 for sincos emb"

    gsd = gsd.to(x.device)
    omega = torch.arange(dim // 4) / (dim // 4 - 1)
    omega = 1.0 / (temperature ** (2 * omega / dim)) * (gsd / 1.0)  # Adjusted for g

    y = y.flatten()[:, None] * omega[None, :]
    x = x.flatten()[:, None] * omega[None, :]
    pe = torch.cat((x.sin(), x.cos(), y.sin(), y.cos()), dim=1)
    return pe.type(dtype)


def posemb_sincos_1d(waves, dim, temperature: int = 10000, dtype=torch.float32):
    assert (
        dim % 2 == 0
    ), "Feature dimension must be a multiple of 2 for sincos embedding"
    waves = torch.arange(waves) if isinstance(waves, int) else waves

    omega = torch.arange(dim // 2, device=waves.device) / (dim // 2 - 1)
    omega = 1.0 / (temperature**omega)

    scaled_waves = waves[:, None] * omega[None, :]
    pe = torch.cat((scaled_waves.sin(), scaled_waves.cos()), dim=1)

    return pe.type(dtype)


############################## factory ############################

"""Dynamic Embedding from DOFA paper.
Reference:
- https://arxiv.org/abs/2403.15356
- https://github.com/zhu-xlab/DOFA
"""

import torch
import torch.nn.functional as F
from einops import rearrange
from torch import nn


class FCBlock(nn.Module):
    def __init__(self, size):
        super().__init__()
        self.l1 = nn.Linear(size, size)
        self.l2 = nn.Linear(size, size)

    def forward(self, x):
        y = F.gelu(self.l1(x))
        y = F.gelu(self.l2(y))
        return x + y


class WavesTransformer(nn.Module):
    def __init__(  # noqa: PLR0913
        self,
        wave_dim,
        output_dim,
        num_latent_tokens,
        embed_dim,
        is_decoder,
        num_heads=4,
        num_layers=1,
    ):
        super().__init__()
        self.num_latent_tokens = num_latent_tokens
        self.is_decoder = is_decoder
        layer = nn.TransformerEncoderLayer(
            d_model=wave_dim,
            nhead=num_heads,
            activation="gelu",
            dropout=0,
            norm_first=False,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers)

        self.fc_weight = nn.Linear(wave_dim, output_dim)
        self.fc_bias = None if self.is_decoder else nn.Linear(wave_dim, embed_dim)

        self.weight_tokens = nn.Parameter(
            torch.randn(self.num_latent_tokens, wave_dim) * 0.02
        )
        self.bias_token = nn.Parameter(torch.randn(1, wave_dim) * 0.02)

    def forward(self, x):
        x = torch.cat([self.weight_tokens, x, self.bias_token], dim=0)
        out = self.encoder(x)
        weights = self.fc_weight(
            out[self.num_latent_tokens : -1] + x[self.num_latent_tokens : -1]
        )
        bias = None if self.is_decoder else self.fc_bias(out[-1])
        return weights, bias


class DynamicEmbedding(nn.Module):
    def __init__(
        self,
        wave_dim,
        num_latent_tokens,
        patch_size,
        embed_dim,
        is_decoder=False,
    ):
        super().__init__()
        self.wave_dim = wave_dim
        self.num_latent_tokens = num_latent_tokens
        self.patch_size = patch_size
        self.embed_dim = embed_dim
        self.is_decoder = is_decoder
        self.output_dim = (patch_size**2) * embed_dim

        self.weight_generator = WavesTransformer(
            wave_dim,
            self.output_dim,
            self.num_latent_tokens,
            self.embed_dim,
            is_decoder,
        )
        self.fclayer = FCBlock(self.wave_dim)

        self.initialize_weights()

    def forward(self, batch, waves):
        waves = posemb_sincos_1d(waves, self.wave_dim)
        waves = waves.to(batch.device)
        waves = self.fclayer(waves)
        weight, bias = self.weight_generator(waves)

        if self.is_decoder:
            dynamic_weight = rearrange(
                weight,
                "cin (k1 k2 cout) -> (cin k1 k2) cout",
                k1=self.patch_size,
                k2=self.patch_size,
                cout=self.embed_dim,
            )
            if bias is not None:
                bias = rearrange(bias, "b -> (b)")
            dynamic_out = F.linear(batch, dynamic_weight * 0.02, bias=bias)
            x = dynamic_out
        else:
            dynamic_weight = rearrange(
                weight,
                "cin (cout k1 k2) -> cout cin k1 k2",
                k1=self.patch_size,
                k2=self.patch_size,
            )
            if bias is not None:
                bias = rearrange(bias, "b -> (b)")
            dynamic_out = F.conv2d(
                batch, dynamic_weight * 0.02, bias=bias, stride=self.patch_size
            )
            x = rearrange(dynamic_out, "b c h w -> b (h w) c")

        return x, waves

    def initialize_weights(self):
        # Initialize weights using Xavier initialization
        for m in self.modules():
            if isinstance(m, (nn.Linear, nn.Conv2d)):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)


############################## backbone ###########################

"""Code for Transformer from Phil Wangs vit-pytorch library.
Repository: https://github.com/lucidrains/vit-pytorch
"""

import torch
import torch.nn.functional as F
from einops import rearrange
from torch import nn


class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, dim),
        )

    def forward(self, x):
        return self.net(x)


class Attention(nn.Module):
    def __init__(self, dim, heads=8, dim_head=64, fused_attn=True):
        super().__init__()
        inner_dim = dim_head * heads
        self.heads = heads
        self.scale = dim_head**-0.5
        self.norm = nn.LayerNorm(dim)
        self.fused_attn = fused_attn

        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias=False)
        self.to_out = nn.Linear(inner_dim, dim, bias=False)

    def forward(self, x):
        x = self.norm(x)

        qkv = self.to_qkv(x).chunk(3, dim=-1)
        q, k, v = map(lambda t: rearrange(t, "b n (h d) -> b h n d", h=self.heads), qkv)

        if self.fused_attn:
            x = F.scaled_dot_product_attention(q, k, v, dropout_p=0.0)
        else:
            attn = torch.matmul(q, k.transpose(-1, -2)) * self.scale
            attn = attn.softmax(dim=-1)
            x = torch.matmul(attn, v)

        x = rearrange(x, "b h n d -> b n (h d)")
        return self.to_out(x)


class Transformer(nn.Module):
    def __init__(  # noqa: PLR0913
        self,
        dim,
        depth,
        heads,
        dim_head,
        mlp_dim,
        fused_attn,
    ):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(
                nn.ModuleList(
                    [
                        Attention(
                            dim, heads=heads, dim_head=dim_head, fused_attn=fused_attn
                        ),
                        FeedForward(dim, mlp_dim),
                    ]
                )
            )

    def forward(self, x):
        for attn, ff in self.layers:
            x = attn(x) + x
            x = ff(x) + x
        return self.norm(x)


#################################################################################################


class Encoder(nn.Module):
    def __init__(  # noqa: PLR0913
        self,
        mask_ratio,
        patch_size,
        shuffle,
        dim,
        depth,
        heads,
        dim_head,
        mlp_ratio,
    ):
        super().__init__()
        self.mask_ratio = mask_ratio
        self.patch_size = patch_size
        self.shuffle = shuffle
        self.dim = dim

        self.patch_embedding = DynamicEmbedding(
            wave_dim=128,
            num_latent_tokens=128,
            patch_size=patch_size,
            embed_dim=dim,
            is_decoder=False,
        )

        self.transformer = Transformer(
            dim=dim,
            depth=depth,
            heads=heads,
            dim_head=dim_head,
            mlp_dim=int(dim * mlp_ratio),
            fused_attn=True,
        )

    def to_patch_embed(self, cube, waves):
        """Split the input cube into patches & create embeddings per patch"""
        patches, waves_encoded = self.patch_embedding(cube, waves)  # [B L D]
        return patches, waves_encoded  # ([B L D], [N D])

    def add_encodings(self, patches):
        """Add position encoding to the patches"""
        B, L, D = patches.shape

        grid_size = int(math.sqrt(L))
        self.num_patches = grid_size**2

        pos_encoding = (
            posemb_sincos_2d(
                h=grid_size,
                w=grid_size,
                dim=self.dim,
            )
            .to(patches.device)
            .detach()
        )

        pos_encoding = repeat(pos_encoding, "L D -> B L D", B=B)  # [B L D]

        patches = patches + pos_encoding  # [B L D] + [B L D] -> [B L D]

        return patches  # [B L D]

    def mask_out(self, patches):
        """
        Mask out patches randomly by shuffling the patches & masking out the
        first N patches

        Parameters
        ----------
        patches : torch.Tensor A tensor of shape (B, L, D)

        Returns
        -------
        unmasked_patches : torch.Tensor
            A tensor of shape (B, L:(1 - mask_ratio), D) containing the
            embeddings of the unmasked patches.
        unmasked_indices : torch.Tensor
            A tensor of shape (B, (1 - mask_ratio)) containing the indices of
            the unmasked patches.
        masked_indices : torch.Tensor
            A tensor of shape (B, mask_ratio) containing the indices of the
            masked patches.
        masked_matrix : torch.Tensor
            A tensor of shape (B, L) containing the mask matrix, 1 indicates a masked
            patch & 0 indicates an unmasked patch.
        """
        B, L, D = patches.shape

        if self.shuffle:  # Shuffle the patches
            noise = torch.randn((B, L), device=patches.device)  # [B L]
        else:  # Don't shuffle, useful for interpolation & inspection of embeddings
            noise = rearrange(
                torch.arange(B * L, device=patches.device), "(B L) -> B L", B=B, L=L
            )

        random_indices = torch.argsort(noise, dim=-1)  # [B L]
        reverse_indices = torch.argsort(random_indices, dim=-1)  # [B L]

        num_masked_patches = int(
            self.mask_ratio * self.num_patches
        )  # Number of patches to be masked out
        masked_indices, unmasked_indices = (
            random_indices[:, :num_masked_patches],  # [B mask_ratio * L]
            random_indices[:, num_masked_patches:],  # [B (1 - mask_ratio) * L]
        )

        # create a mask of shape B L, where 1 indicates a masked patch
        # and 0 indicates an unmasked patch
        masked_matrix = torch.zeros((B, L), device=patches.device)  # [B L] = 0
        masked_matrix[:, :num_masked_patches] = 1  # [B mask_ratio * L] = 1
        masked_matrix = torch.gather(
            masked_matrix, dim=1, index=reverse_indices
        )  # [B L] -> [B L] - reorder the patches

        # mask out the patches
        batch_indices = rearrange(
            torch.arange(B, device=patches.device), "B -> B 1"
        )  # [B 1]
        unmasked_patches = patches[
            batch_indices, unmasked_indices, :
        ]  # [B L:(1 - mask_ratio) D]
        _ = patches[batch_indices, masked_indices, :]  # [B L:mask_ratio D]

        return (
            unmasked_patches,
            unmasked_indices,
            masked_indices,
            masked_matrix,
        )  # [B L:(1 - mask_ratio) D], [(1-mask_ratio)], [mask_ratio], [B L]

    def forward(self, cube: Tensor, waves: Tensor) -> Tensor:

        B, C, H, W = cube.shape

        patches, waves_encoded = self.to_patch_embed(
            cube, waves
        )  # [B L D] - patchify & create embeddings per patch

        patches = self.add_encodings(
            patches,
        )  # [B L D] - add position encoding to the embeddings

        # mask out patches
        (
            unmasked_patches,
            unmasked_indices,
            masked_indices,
            masked_matrix,
        ) = self.mask_out(
            patches
        )  # [B L:(1 - mask_ratio) D], [(1-mask_ratio)], [mask_ratio], [B L]

        # pass the unmasked patches through the transformer
        encoded_unmasked_patches = self.transformer(
            unmasked_patches
        )  # [B L:(1 - mask_ratio)) D]

        return encoded_unmasked_patches


class ClayMAE(nn.Module):
    def __init__(  # noqa: PLR0913
        self,
        mask_ratio,
        patch_size,
        shuffle,
        wavelengths,
        is_clf,
        num_classes,
        img_size,
        # ENCODER
        dim,
        depth,
        heads,
        dim_head,
        mlp_ratio,
        # WEIGHTS
        pretrained_path,
        **kwargs,
    ):
        super().__init__()
        self.mask_ratio = mask_ratio
        self.patch_size = patch_size
        self.shuffle = shuffle
        self.wavelengths = wavelengths
        self.img_size = img_size

        self.output_shape = dict(channels=dim, stride=patch_size)
        self.out_channels = dim
        self._is_dofa = True
        self.is_clf = is_clf
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

        self.encoder = Encoder(
            mask_ratio=mask_ratio,
            patch_size=patch_size,
            shuffle=shuffle,
            dim=dim,
            depth=depth,
            heads=heads,
            dim_head=dim_head,
            mlp_ratio=mlp_ratio,
        )

        if self.is_clf:
            num_patches = (img_size // patch_size) ** 2
            self.head = (
                nn.Linear(num_patches * dim, num_classes)
                if num_classes > 0
                else nn.Identity()
            )
        else:
            self.upsample = nn.Sequential(
                nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
                nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
                nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
            )

        self._init_weights_from_ckpt(pretrained_path)

    def _init_weights_from_ckpt(self, pretrained_path):
        raw_stdict = torch.hub.load_state_dict_from_url(
            pretrained_path, map_location=torch.device("cpu")
        )
        if "state_dict" in raw_stdict.keys():
            raw_stdict = raw_stdict["state_dict"]

        new_stdict = OrderedDict()
        for k, v in raw_stdict.items():
            if (
                # any(substring in k for substring in ["model.encoder", "model.decoder"])
                "model.encoder" in k
                and "cls_token" not in k
            ):
                if "model." in k:
                    k = k.replace("model.", "")
                new_stdict[k] = v

        logging.disable(logging.WARNING)
        self.load_state_dict(new_stdict, strict=False)
        logging.disable(0)

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass of the model.

        Args:
            x: Input mini-batch.

        Returns:
            Output mini-batch.
        """

        if self.qa_idx is not None:
            x = torch.cat([x[:, : self.qa_idx], x[:, self.qa_idx + 1 :]], dim=1)

        waves = torch.tensor(self.wavelengths)

        _pixels = x.clone()

        batch_size, channels, _, _ = _pixels.size()

        # ENCODER

        pixels = self.encoder(_pixels, waves)

        if self.is_clf:
            batch, num_patches, dim = pixels.shape
            pixels_flattened = pixels.view(batch, -1)
            pixels = self.head(pixels_flattened)
        else:
            batch, num_patches, dim = pixels.shape
            patch_size = int(num_patches**0.5)
            pixels = pixels.permute(0, 2, 1).reshape(batch, dim, patch_size, patch_size)

            pixels = self.upsample(pixels)

        return pixels
