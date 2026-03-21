"""NTSC-RS Intermediate Node - Preset with scaling controls.

This node provides preset-based VHS/CRT looks with additional
control over resolution scaling and output size.
"""

import torch
import numpy as np
from typing import Tuple

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io

from .ntsc_presets import PRESETS, get_preset, get_preset_names, apply_intensity_to_preset


SCALE_PRESET_OPTIONS = [
    "Source (1x)", 
    "Half (0.5x)", 
    "Quarter (0.25x)",
    "Double (2x)", 
    "Custom"
]

FIELD_MODE_OPTIONS = ["InterleavedUpper", "InterleavedLower", "Both", "Alternating"]


def get_scale_values(preset: str, scale_preset: str, custom_h: float, custom_v: float) -> Tuple[float, float, bool]:
    """Get horizontal and vertical scale values based on preset selection."""
    if scale_preset == "Source (1x)":
        return 1.0, 1.0, False
    elif scale_preset == "Half (0.5x)":
        return 0.5, 0.5, False
    elif scale_preset == "Quarter (0.25x)":
        return 0.25, 0.25, False
    elif scale_preset == "Double (2x)":
        return 2.0, 2.0, False
    else:  # Custom
        return custom_h, custom_v, True


class NtscRsIntermediateNode(io.ComfyNode):
    """Intermediate NTSC-RS node with presets and scaling controls."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Intermediate",
            display_name="NTSC-RS Intermediate",
            category="NTSC",
            description="VHS/CRT effect with preset configurations and scaling controls. Balance between simplicity and full parameter control.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to apply NTSC effect to"),
                
                # Preset Selection
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

                # Scaling Section
                io.Combo.Input("scale_preset", display_name="Scale Preset",
                    options=SCALE_PRESET_OPTIONS,
                    default="Source (1x)",
                    tooltip="Output resolution preset",
                ),
                io.Float.Input("horizontal_scale", display_name="H Scale",
                    default=1.0,
                    min=0.125,
                    max=8.0,
                    step=0.125,
                    tooltip="Horizontal scale factor (for Custom preset)",
                ),
                io.Float.Input("vertical_scale", display_name="V Scale", 
                    default=1.0,
                    min=0.125,
                    max=8.0,
                    step=0.125,
                    tooltip="Vertical scale factor (for Custom preset)",
                ),

                # Additional Controls
                io.Combo.Input("field_mode", display_name="Field Mode",
                    options=FIELD_MODE_OPTIONS,
                    default="InterleavedUpper",
                    tooltip="Field processing mode",
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
            search_aliases=["ntsc", "vhs", "crt", "retro", "scaled", "intermediate"],
        )

    @classmethod
    def process(cls, image, preset, intensity, scale_preset, horizontal_scale, vertical_scale, field_mode, random_seed):
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
        preset_config["use_field"] = field_mode

        # Apply intensity to noise parameters
        if intensity < 1.0:
            current_preset = apply_intensity_to_preset(preset_config, intensity)
        else:
            current_preset = preset_config.copy()

        # Override scale settings
        if scale_preset != "Custom":
            h_scale, v_scale, use_custom = get_scale_values(preset, scale_preset, horizontal_scale, vertical_scale)
            current_preset["horizontal_scale"] = h_scale
            current_preset["vertical_scale"] = v_scale
            current_preset["scale_with_video_size"] = False
        else:
            current_preset["horizontal_scale"] = horizontal_scale
            current_preset["vertical_scale"] = vertical_scale
            current_preset["scale_with_video_size"] = False
            current_preset["scale_enabled"] = True

        for i in range(batch_size):
            img = image[i]
            img_np = (img.cpu().numpy() * 255.0).astype(np.uint8)

            result = comfyui_ntsc_rs.apply_ntsc_filter(img_np, current_preset)

            result_float = torch.from_numpy(result).float() / 255.0
            result_float = torch.clamp(result_float, 0.0, 1.0)

            results.append(result_float)

        output = torch.stack(results, dim=0)
        return io.NodeOutput(output)

    @classmethod
    async def execute(cls, image, preset, intensity, scale_preset, horizontal_scale, vertical_scale, field_mode, random_seed):
        return cls.process(image, preset, intensity, scale_preset, horizontal_scale, vertical_scale, field_mode, random_seed)
