"""NTSC Scale Node.

Resizes images with PyTorch interpolation. Part of the chainable NTSC-RS node system.

Note: ntsc-rs scale parameters (horizontal_scale/vertical_scale) affect signal
processing (filter bandwidth), not image dimensions. This node only resizes.
"""

import torch
import torch.nn.functional as F
from comfy_api.latest import io

SCALE_PRESETS = {
    "Source (1x)": 1.0,
    "Half (0.5x)": 0.5,
    "Quarter (0.25x)": 0.25,
    "Double (2x)": 2.0,
    "Quad (4x)": 4.0,
    "Custom": None,
}


def get_scale_values(scale_preset: str, custom_h: float, custom_v: float) -> tuple[float, float]:
    """Return (horizontal, vertical) factors for a preset name; "Custom" uses the inputs."""
    factor = SCALE_PRESETS.get(scale_preset)
    return (custom_h, custom_v) if factor is None else (factor, factor)


def resize(image: torch.Tensor, h_scale: float, v_scale: float) -> torch.Tensor:
    """Bilinearly resize a ComfyUI IMAGE batch (B, H, W, C)."""
    if h_scale == 1.0 and v_scale == 1.0:
        return image
    _, height, width, _ = image.shape
    size = (max(1, int(height * v_scale)), max(1, int(width * h_scale)))
    resized = F.interpolate(
        image.permute(0, 3, 1, 2), size=size, mode="bilinear", align_corners=False
    )
    return resized.permute(0, 2, 3, 1).clamp(0.0, 1.0)


class NtscRsScaleNode(io.ComfyNode):
    """NTSC Scale node - horizontal/vertical resolution scaling."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Scale",
            display_name="NTSC-RS Scale",
            category="NTSC",
            description="Resolution scaling: horizontal and vertical scale factors. Performs actual image resizing using PyTorch. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to process"),
                io.Combo.Input(
                    "scale_preset",
                    display_name="Scale Preset",
                    options=list(SCALE_PRESETS),
                    default="Source (1x)",
                    tooltip="Output resolution preset",
                ),
                io.Float.Input(
                    "horizontal_scale",
                    display_name="H Scale",
                    default=1.0,
                    min=0.125,
                    max=8.0,
                    step=0.125,
                    tooltip="Horizontal scale factor (Custom preset)",
                ),
                io.Float.Input(
                    "vertical_scale",
                    display_name="V Scale",
                    default=1.0,
                    min=0.125,
                    max=8.0,
                    step=0.125,
                    tooltip="Vertical scale factor (Custom preset)",
                ),
            ],
            outputs=[
                io.Image.Output(display_name="Image", tooltip="Rescaled image"),
            ],
        )

    @classmethod
    def execute(cls, image, scale_preset, horizontal_scale, vertical_scale):
        h_scale, v_scale = get_scale_values(scale_preset, horizontal_scale, vertical_scale)
        return io.NodeOutput(resize(image, h_scale, v_scale))
