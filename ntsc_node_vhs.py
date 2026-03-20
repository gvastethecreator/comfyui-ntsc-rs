"""NTSC VHS Node.

Applies VHS-specific effects: tape speed, chroma loss, sharpen, edge wave.
Part of the chainable NTSC-RS node system.
"""

import torch
import numpy as np

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io


VHS_TAPE_SPEED_OPTIONS = ["NONE", "SP", "LP", "EP"]


class NtscRsVHSNode(io.ComfyNode):
    """NTSC VHS node - tape speed, chroma loss, sharpen, edge wave effects."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_VHS",
            display_name="NTSC VHS",
            category="image/effects/ntsc/category",
            description="VHS-specific effects: tape speed, chroma loss, sharpening, edge wave. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", tooltip="Image to process"),

                io.Combo.Input(
                    "vhs_tape_speed",
                    options=VHS_TAPE_SPEED_OPTIONS,
                    default="SP",
                    tooltip="VHS tape speed (affects high-frequency cutoff)",
                ),
                io.Float.Input("vhs_chroma_loss", default=0.000025, min=0.0, max=1.0, step=0.000001,
                    tooltip="Chroma loss probability per scanline"),

                io.Boolean.Input("vhs_sharpen_enabled", default=True,
                    tooltip="Enable VHS sharpening"),
                io.Float.Input("vhs_sharpen_intensity", default=0.25, min=0.0, max=5.0, step=0.01,
                    tooltip="VHS sharpen intensity"),
                io.Float.Input("vhs_sharpen_frequency", default=1.0, min=0.5, max=4.0, step=0.01,
                    tooltip="VHS sharpen frequency"),

                io.Boolean.Input("vhs_edge_wave_enabled", default=True,
                    tooltip="Enable edge wave effect"),
                io.Float.Input("vhs_edge_wave_intensity", default=0.5, min=0.0, max=20.0, step=0.01,
                    tooltip="Edge wave intensity (pixels)"),
                io.Float.Input("vhs_edge_wave_speed", default=4.0, min=0.0, max=10.0, step=0.1,
                    tooltip="Edge wave speed"),
                io.Float.Input("vhs_edge_wave_frequency", default=0.05, min=0.0, max=0.5, step=0.001,
                    tooltip="Edge wave frequency"),
                io.Int.Input("vhs_edge_wave_detail", default=2, min=1, max=5, step=1,
                    tooltip="Edge wave detail (octaves)"),

                io.Int.Input("random_seed", default=0, min=-2147483648, max=2147483647, step=1,
                    tooltip="Random seed for noise generation"),
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
            search_aliases=["ntsc", "vhs", "tape", "chroma", "sharpen", "edge", "wave"],
        )

    @classmethod
    def process(cls, image, vhs_tape_speed, vhs_chroma_loss, vhs_sharpen_enabled,
               vhs_sharpen_intensity, vhs_sharpen_frequency, vhs_edge_wave_enabled,
               vhs_edge_wave_intensity, vhs_edge_wave_speed, vhs_edge_wave_frequency, vhs_edge_wave_detail,
               random_seed):
        """Process the image through NTSC VHS effects."""
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
            "use_field": "InterleavedUpper",
            "video_scanline_phase_shift": "Degrees180",
            "video_scanline_phase_shift_offset": 0,
            "head_switching_enabled": False,
            "tracking_noise_enabled": False,
            "composite_noise_enabled": False,
            "luma_noise_enabled": False,
            "chroma_noise_enabled": False,
            "ringing_enabled": False,
            # Enable VHS
            "vhs_enabled": True,
            "vhs_tape_speed": vhs_tape_speed,
            "vhs_chroma_loss": vhs_chroma_loss,
            "vhs_sharpen_enabled": vhs_sharpen_enabled,
            "vhs_sharpen_intensity": vhs_sharpen_intensity,
            "vhs_sharpen_frequency": vhs_sharpen_frequency,
            "vhs_edge_wave_enabled": vhs_edge_wave_enabled,
            "vhs_edge_wave_intensity": vhs_edge_wave_intensity,
            "vhs_edge_wave_speed": vhs_edge_wave_speed,
            "vhs_edge_wave_frequency": vhs_edge_wave_frequency,
            "vhs_edge_wave_detail": vhs_edge_wave_detail,
            # Disable other effects
            "snow_intensity": 0.0,
            "chroma_phase_noise_intensity": 0.0,
            "chroma_phase_error": 0.0,
            "chroma_delay_horizontal": 0.0,
            "chroma_delay_vertical": 0,
            "scale_enabled": True,
            "horizontal_scale": 1.0,
            "vertical_scale": 1.0,
            "scale_with_video_size": False,
            "random_seed": random_seed,
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
    async def execute(cls, image, vhs_tape_speed, vhs_chroma_loss, vhs_sharpen_enabled,
                     vhs_sharpen_intensity, vhs_sharpen_frequency, vhs_edge_wave_enabled,
                     vhs_edge_wave_intensity, vhs_edge_wave_speed, vhs_edge_wave_frequency, vhs_edge_wave_detail,
                     random_seed):
        return cls.process(image, vhs_tape_speed, vhs_chroma_loss, vhs_sharpen_enabled,
                          vhs_sharpen_intensity, vhs_sharpen_frequency, vhs_edge_wave_enabled,
                          vhs_edge_wave_intensity, vhs_edge_wave_speed, vhs_edge_wave_frequency, vhs_edge_wave_detail,
                          random_seed)
