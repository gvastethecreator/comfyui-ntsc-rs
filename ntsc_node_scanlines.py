"""NTSC Scanlines Node.

Applies field/scanline processing: field mode, scanline phase shift.
Part of the chainable NTSC-RS node system.
"""

import torch
import numpy as np

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io


USE_FIELD_OPTIONS = ["Alternating", "Upper", "Lower", "Both", "InterleavedUpper", "InterleavedLower"]
PHASE_SHIFT_OPTIONS = ["Degrees0", "Degrees90", "Degrees180", "Degrees270"]


class NtscRsScanlinesNode(io.ComfyNode):
    """NTSC Scanlines node - field mode and scanline phase processing."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Scanlines",
            display_name="NTSC Scanlines",
            category="image/effects/ntsc/category",
            description="Field and scanline processing: field mode and scanline phase shift. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", tooltip="Image to process"),

                io.Combo.Input(
                    "use_field",
                    options=USE_FIELD_OPTIONS,
                    default="InterleavedUpper",
                    tooltip="Field usage mode",
                ),
                io.Combo.Input(
                    "video_scanline_phase_shift",
                    options=PHASE_SHIFT_OPTIONS,
                    default="Degrees180",
                    tooltip="Video scanline phase shift",
                ),
                io.Int.Input("video_scanline_phase_shift_offset", default=0, min=0, max=3, step=1,
                    tooltip="Phase shift offset"),
            ],
            outputs=[
                io.Image.Output(tooltip="Processed image"),
            ],
            is_output_node=False,
            is_experimental=False,
            is_deprecated=False,
            is_dev_only=False,
            is_api_node=False,
            is_input_list=False,
            not_idempotent=False,
            accept_all_inputs=False,
            enable_expand=False,
            search_aliases=["ntsc", "scanlines", "field", "interlace"],
        )

    @classmethod
    def process(cls, image, use_field, video_scanline_phase_shift, video_scanline_phase_shift_offset):
        """Process the image through NTSC scanline effects."""
        try:
            import comfyui_ntsc_rs
            HAS_RUST = True
        except ImportError:
            HAS_RUST = False

        if not HAS_RUST:
            raise ImportError("comfyui_ntsc_rs native module not found.")

        params = {
            # Disable signal processing
            "filter_type": "Butterworth",
            "input_luma_filter": "Notch",
            "chroma_lowpass_in": "Full",
            "chroma_demodulation": "Notch",
            "chroma_lowpass_out": "Full",
            "luma_smear": 0.5,
            "composite_sharpening": 1.0,
            "chroma_vert_blend": True,
            # Enable scanlines
            "use_field": use_field,
            "video_scanline_phase_shift": video_scanline_phase_shift,
            "video_scanline_phase_shift_offset": video_scanline_phase_shift_offset,
            # Disable all other effects
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
            "scale_enabled": True,
            "horizontal_scale": 1.0,
            "vertical_scale": 1.0,
            "scale_with_video_size": False,
            "random_seed": 0,
        }

        batch_size, height, width, channels = image.shape
        results = []

        for i in range(batch_size):
            img = image[i]
            img_np = (img.cpu().numpy() * 255.0).astype(np.uint8)
            result = comfyui_ntsc_rs.apply_ntsc_filter(img_np, params)
            result_float = torch.from_numpy(result).float() / 255.0
            result_float = torch.clamp(result_float, 0.0, 1.0)
            results.append(result_float)

        output = torch.stack(results, dim=0)
        return io.NodeOutput(output)

    @classmethod
    async def execute(cls, image, use_field, video_scanline_phase_shift, video_scanline_phase_shift_offset):
        return cls.process(image, use_field, video_scanline_phase_shift, video_scanline_phase_shift_offset)
