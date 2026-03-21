"""NTSC-RS Simple Node - Preset-based VHS/CRT effect.

This node provides quick access to common VHS/CRT looks using presets.
For full control over all parameters, use NtscRsNode instead.
"""

import torch
import numpy as np
from typing import Tuple

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io

from .ntsc_presets import PRESETS, get_preset, get_preset_names, apply_intensity_to_preset


class NtscRsSimpleNode(io.ComfyNode):
    """Simple NTSC-RS node with preset-based VHS/CRT effects."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Simple",
            display_name="NTSC-RS Simple",
            category="NTSC",
            description="VHS/CRT effect with preset configurations. For full parameter control, use the Advanced node.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to apply NTSC effect to"),
                io.Combo.Input("preset", display_name="Preset",
                    options=get_preset_names(),
                    default="vhs_classic",
                    tooltip="Preset configuration",
                ),
                io.Float.Input("intensity", display_name="Intensity",
                    default=1.0,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    tooltip="Effect intensity multiplier",
                ),
                io.Float.Input("saturation", display_name="Saturation",
                    default=0.25,
                    min=-1.0,
                    max=2.0,
                    step=0.01,
                    tooltip="Color saturation adjustment",
                ),
                io.Int.Input("random_seed", display_name="Seed",
                    default=0,
                    min=-2147483648,
                    max=2147483647,
                    step=1,
                    tooltip="Random seed for noise generation",
                ),
            ],
            outputs=[
                io.Image.Output(display_name="Image", tooltip="Processed image"),
            ],
            is_output_node=False,
            is_experimental=False,
            is_deprecated=False,
            is_dev_only=False,
            is_api_node=False,
            is_input_list=False,
            not_idempotent=False,
            accept_all_inputs=False,
            enable_expand=True,
            search_aliases=["ntsc", "vhs", "crt", "retro"],
        )

    @classmethod
    def process(cls, image, preset, intensity, saturation, random_seed):
        """Process the image through the NTSC effect."""
        try:
            import comfyui_ntsc_rs
            HAS_RUST = True
        except ImportError:
            HAS_RUST = False

        if not HAS_RUST:
            raise ImportError(
                "comfyui_ntsc_rs native module not found. "
                "Run 'python build_node.py' to build the Rust binding."
            )

        batch_size, height, width, channels = image.shape
        results = []

        preset_config = get_preset(preset)
        preset_config["random_seed"] = random_seed
        preset_config["composite_sharpening"] = preset_config.get("composite_sharpening", 1.0) * (1.0 + saturation)

        for i in range(batch_size):
            img = image[i]

            if intensity < 1.0:
                current_preset = apply_intensity_to_preset(preset_config, intensity)
            else:
                current_preset = preset_config.copy()

            img_np = (img.cpu().numpy() * 255.0).astype(np.uint8)

            result = comfyui_ntsc_rs.apply_ntsc_filter(img_np, current_preset)

            result_float = torch.from_numpy(result).float() / 255.0
            result_float = torch.clamp(result_float, 0.0, 1.0)

            results.append(result_float)

        output = torch.stack(results, dim=0)
        return io.NodeOutput(output)

    @classmethod
    async def execute(cls, image, preset, intensity, saturation, random_seed):
        return cls.process(image, preset, intensity, saturation, random_seed)