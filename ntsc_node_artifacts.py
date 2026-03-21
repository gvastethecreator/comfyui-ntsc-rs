"""NTSC Artifacts Node.

Applies VHS artifacts: head switching and tracking noise.
Part of the chainable NTSC-RS node system.
"""

import torch
import numpy as np

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io


class NtscRsArtifactsNode(io.ComfyNode):
    """NTSC Artifacts node - head switching and tracking noise effects."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Artifacts",
            display_name="NTSC-RS Artifacts",
            category="NTSC",
            description="VHS artifacts: head switching and tracking noise emulation. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to process"),

                io.Boolean.Input("head_switching_enabled", display_name="Head Switching", default=True,
                    tooltip="Enable head switching effect"),
                io.Int.Input("head_switching_height", display_name="Head Switching Height", default=8, min=0, max=24, step=1,
                    tooltip="Height of head switching artifact"),
                io.Int.Input("head_switching_offset", display_name="Head Switching Offset", default=3, min=0, max=24, step=1,
                    tooltip="Head switching offset"),
                io.Float.Input("head_switching_horizontal_shift", display_name="Head Switching H Shift", default=72.0, min=-100.0, max=100.0, step=0.5,
                    tooltip="Horizontal shift amount"),
                io.Boolean.Input("head_switching_mid_line_enabled", display_name="Mid Line Enabled", default=True,
                    tooltip="Enable mid-line head switching"),
                io.Float.Input("head_switching_mid_line_position", display_name="Mid Line Position", default=0.95, min=0.0, max=1.0, step=0.01,
                    tooltip="Mid-line position"),
                io.Float.Input("head_switching_mid_line_jitter", display_name="Mid Line Jitter", default=0.03, min=0.0, max=1.0, step=0.001,
                    tooltip="Mid-line jitter amount"),

                io.Boolean.Input("tracking_noise_enabled", display_name="Tracking Noise", default=True,
                    tooltip="Enable tracking noise"),
                io.Int.Input("tracking_noise_height", display_name="Tracking Noise Height", default=12, min=0, max=120, step=1,
                    tooltip="Tracking noise height"),
                io.Float.Input("tracking_noise_wave_intensity", display_name="Tracking Wave Intensity", default=15.0, min=-50.0, max=50.0, step=0.5,
                    tooltip="Wave intensity"),
                io.Float.Input("tracking_noise_snow_intensity", display_name="Tracking Snow Intensity", default=0.025, min=0.0, max=1.0, step=0.001,
                    tooltip="Snow speckle intensity"),
                io.Float.Input("tracking_noise_snow_anisotropy", display_name="Tracking Snow Anisotropy", default=0.25, min=0.0, max=1.0, step=0.01,
                    tooltip="Snow anisotropy"),
                io.Float.Input("tracking_noise_noise_intensity", display_name="Tracking Noise Intensity", default=0.25, min=0.0, max=1.0, step=0.01,
                    tooltip="Non-speckle noise intensity"),

                io.Int.Input("random_seed", display_name="Seed", default=0, min=-2147483648, max=2147483647, step=1,
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
            enable_expand=True,
            search_aliases=["ntsc", "artifacts", "head", "switching", "tracking", "vhs"],
        )

    @classmethod
    def process(cls, image, head_switching_enabled, head_switching_height, head_switching_offset,
               head_switching_horizontal_shift, head_switching_mid_line_enabled,
               head_switching_mid_line_position, head_switching_mid_line_jitter,
               tracking_noise_enabled, tracking_noise_height, tracking_noise_wave_intensity,
               tracking_noise_snow_intensity, tracking_noise_snow_anisotropy, tracking_noise_noise_intensity,
               random_seed):
        """Process the image through NTSC artifact effects."""
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
            # Enable artifacts
            "head_switching_enabled": head_switching_enabled,
            "head_switching_height": head_switching_height,
            "head_switching_offset": head_switching_offset,
            "head_switching_horizontal_shift": head_switching_horizontal_shift,
            "head_switching_mid_line_enabled": head_switching_mid_line_enabled,
            "head_switching_mid_line_position": head_switching_mid_line_position,
            "head_switching_mid_line_jitter": head_switching_mid_line_jitter,
            "tracking_noise_enabled": tracking_noise_enabled,
            "tracking_noise_height": tracking_noise_height,
            "tracking_noise_wave_intensity": tracking_noise_wave_intensity,
            "tracking_noise_snow_intensity": tracking_noise_snow_intensity,
            "tracking_noise_snow_anisotropy": tracking_noise_snow_anisotropy,
            "tracking_noise_noise_intensity": tracking_noise_noise_intensity,
            # Disable other effects
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
    async def execute(cls, image, head_switching_enabled, head_switching_height, head_switching_offset,
                     head_switching_horizontal_shift, head_switching_mid_line_enabled,
                     head_switching_mid_line_position, head_switching_mid_line_jitter,
                     tracking_noise_enabled, tracking_noise_height, tracking_noise_wave_intensity,
                     tracking_noise_snow_intensity, tracking_noise_snow_anisotropy, tracking_noise_noise_intensity,
                     random_seed):
        return cls.process(image, head_switching_enabled, head_switching_height, head_switching_offset,
                          head_switching_horizontal_shift, head_switching_mid_line_enabled,
                          head_switching_mid_line_position, head_switching_mid_line_jitter,
                          tracking_noise_enabled, tracking_noise_height, tracking_noise_wave_intensity,
                          tracking_noise_snow_intensity, tracking_noise_snow_anisotropy, tracking_noise_noise_intensity,
                          random_seed)
