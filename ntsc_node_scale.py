"""NTSC Scale Node.

Applies resolution scaling: horizontal and vertical scale factors.
Part of the chainable NTSC-RS node system.

Note: ntsc-rs scale parameters (horizontal_scale/vertical_scale) affect signal
processing (filter bandwidth), not image dimensions. This node performs actual
image resizing using PyTorch interpolation.
"""

import torch
import torch.nn.functional as F
import numpy as np

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io


SCALE_PRESET_OPTIONS = [
    "Source (1x)", 
    "Half (0.5x)", 
    "Quarter (0.25x)",
    "Double (2x)", 
    "Quad (4x)",
    "Custom"
]


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

                io.Combo.Input("scale_preset", display_name="Scale Preset",
                    options=SCALE_PRESET_OPTIONS,
                    default="Source (1x)",
                    tooltip="Output resolution preset",
                ),
                io.Float.Input("horizontal_scale", display_name="H Scale", default=1.0, min=0.125, max=8.0, step=0.125,
                    tooltip="Horizontal scale factor"),
                io.Float.Input("vertical_scale", display_name="V Scale", default=1.0, min=0.125, max=8.0, step=0.125,
                    tooltip="Vertical scale factor"),
                io.Boolean.Input("scale_with_video_size", display_name="Scale With Video Size", default=False,
                    tooltip="Multiply scale by video height"),
            ],
            outputs=[
                io.Image.Output(display_name="Image", tooltip="Rescaled image"),
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
            search_aliases=["ntsc", "scale", "resolution", "size", "resize"],
        )

    @classmethod
    def get_scale_values(cls, scale_preset: str, custom_h: float, custom_v: float):
        """Get horizontal and vertical scale values based on preset selection."""
        if scale_preset == "Source (1x)":
            return 1.0, 1.0
        elif scale_preset == "Half (0.5x)":
            return 0.5, 0.5
        elif scale_preset == "Quarter (0.25x)":
            return 0.25, 0.25
        elif scale_preset == "Double (2x)":
            return 2.0, 2.0
        elif scale_preset == "Quad (4x)":
            return 4.0, 4.0
        else:  # Custom
            return custom_h, custom_v

    @classmethod
    def process(cls, image, scale_preset, horizontal_scale, vertical_scale, scale_with_video_size):
        """Process the image through NTSC scaling (actual resize)."""
        try:
            import comfyui_ntsc_rs
            HAS_RUST = True
        except ImportError:
            HAS_RUST = False

        if not HAS_RUST:
            raise ImportError("comfyui_ntsc_rs native module not found.")

        h_scale, v_scale = cls.get_scale_values(scale_preset, horizontal_scale, vertical_scale)

        params = {
            "filter_type": "Butterworth",
            "input_luma_filter": "Notch",
            "chroma_lowpass_in": "Full",
            "chroma_demodulation": "Notch",
            "chroma_lowpass_out": "Full",
            "luma_smear": 0.5,
            "composite_sharpening": 1.0,
            "chroma_vert_blend": True,
            "use_field": "Both",
            "video_scanline_phase_shift": "Degrees180",
            "video_scanline_phase_shift_offset": 0,
            "head_switching_enabled": False,
            "tracking_noise_enabled": False,
            "composite_noise_enabled": False,
            "luma_noise_enabled": False,
            "chroma_noise_enabled": False,
            "ringing_enabled": False,
            "vhs_enabled": False,
            "snow_intensity": 0.0,
            "chroma_phase_noise_intensity": 0.0,
            "chroma_phase_error": 0.0,
            "chroma_delay_horizontal": 0.0,
            "chroma_delay_vertical": 0,
            "scale_enabled": False,
            "random_seed": 0,
        }

        batch_size, height, width, channels = image.shape
        results = []

        for i in range(batch_size):
            img = image[i]
            img_np = (img.cpu().numpy() * 255.0).astype(np.uint8)
            
            result = comfyui_ntsc_rs.apply_ntsc_filter(img_np, params)
            result_float = torch.from_numpy(result).float() / 255.0
            
            if h_scale != 1.0 or v_scale != 1.0:
                new_height = int(height * v_scale)
                new_width = int(width * h_scale)
                
                result_float = result_float.permute(2, 0, 1)
                result_float = result_float.unsqueeze(0)
                result_float = F.interpolate(
                    result_float,
                    size=(new_height, new_width),
                    mode='bilinear',
                    align_corners=False
                )
                result_float = result_float.squeeze(0).permute(1, 2, 0)
            
            result_float = torch.clamp(result_float, 0.0, 1.0)
            results.append(result_float)

        output = torch.stack(results, dim=0)
        return io.NodeOutput(output)

    @classmethod
    async def execute(cls, image, scale_preset, horizontal_scale, vertical_scale, scale_with_video_size):
        return cls.process(image, scale_preset, horizontal_scale, vertical_scale, scale_with_video_size)
