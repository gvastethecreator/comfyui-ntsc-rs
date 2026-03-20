"""NTSC-RS Advanced Node - Full parameter control for VHS/CRT effect.

This node provides complete 1:1 access to all ntsc-rs parameters.
For quick preset-based effects, use NtscRsSimpleNode instead.
"""

import torch
import numpy as np
from typing import Tuple, Optional

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io


USE_FIELD_OPTIONS = ["Alternating", "Upper", "Lower", "Both", "InterleavedUpper", "InterleavedLower"]
FILTER_TYPE_OPTIONS = ["ConstantK", "Butterworth"]
LUMA_LOWPASS_OPTIONS = ["None", "Box", "Notch"]
CHROMA_LOWPASS_OPTIONS = ["None", "Light", "Full"]
CHROMA_DEMOD_OPTIONS = ["Box", "Notch", "OneLineComb", "TwoLineComb"]
PHASE_SHIFT_OPTIONS = ["Degrees0", "Degrees90", "Degrees180", "Degrees270"]
VHS_TAPE_SPEED_OPTIONS = ["NONE", "SP", "LP", "EP"]


class NtscRsNode(io.ComfyNode):
    """Advanced NTSC-RS node with full parameter control."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Advanced",
            display_name="NTSC-RS (Advanced)",
            category="image/effects/ntsc",
            description="Full NTSC/VHS/CRT effect with complete parameter control. 1:1 quality with ntsc-rs library.",
            inputs=[
                io.Image.Input("image", tooltip="Image to apply NTSC effect to"),

                io.Header.Input("signal_processing", "Signal Processing", tooltip="Signal processing settings"),

                io.Combo.Input(
                    "filter_type",
                    options=FILTER_TYPE_OPTIONS,
                    default="Butterworth",
                    tooltip="NTSC decode filter type",
                ),
                io.Combo.Input(
                    "input_luma_filter",
                    options=LUMA_LOWPASS_OPTIONS,
                    default="Notch",
                    tooltip="Input luminance low-pass filter",
                ),
                io.Combo.Input(
                    "chroma_lowpass_in",
                    options=CHROMA_LOWPASS_OPTIONS,
                    default="Full",
                    tooltip="Input chroma low-pass filter",
                ),
                io.Combo.Input(
                    "chroma_demodulation",
                    options=CHROMA_DEMOD_OPTIONS,
                    default="Notch",
                    tooltip="Chroma demodulation filter",
                ),
                io.Combo.Input(
                    "chroma_lowpass_out",
                    options=CHROMA_LOWPASS_OPTIONS,
                    default="Full",
                    tooltip="Output chroma low-pass filter",
                ),
                io.Float.Input("luma_smear", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Luminance smear amount"),
                io.Float.Input("composite_sharpening", default=1.0, min=-1.0, max=2.0, step=0.01,
                    tooltip="Composite sharpening/preemphasis"),
                io.Boolean.Input("chroma_vert_blend", default=True,
                    tooltip="Vertically blend chroma between scanlines"),

                io.Header.Input("field_processing", "Field/Line Processing", tooltip="Field and scanline settings"),

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

                io.Header.Input("head_switching", "Head Switching", tooltip="VHS head switching artifact emulation"),

                io.Boolean.Input("head_switching_enabled", default=True,
                    tooltip="Enable head switching effect"),
                io.Int.Input("head_switching_height", default=8, min=0, max=24, step=1,
                    tooltip="Height of head switching artifact"),
                io.Int.Input("head_switching_offset", default=3, min=0, max=24, step=1,
                    tooltip="Head switching offset"),
                io.Float.Input("head_switching_horizontal_shift", default=72.0, min=-100.0, max=100.0, step=0.5,
                    tooltip="Horizontal shift amount"),
                io.Boolean.Input("head_switching_mid_line_enabled", default=True,
                    tooltip="Enable mid-line head switching"),
                io.Float.Input("head_switching_mid_line_position", default=0.95, min=0.0, max=1.0, step=0.01,
                    tooltip="Mid-line position"),
                io.Float.Input("head_switching_mid_line_jitter", default=0.03, min=0.0, max=1.0, step=0.001,
                    tooltip="Mid-line jitter amount"),

                io.Header.Input("tracking_noise", "Tracking Noise", tooltip="VHS tracking noise emulation"),

                io.Boolean.Input("tracking_noise_enabled", default=True,
                    tooltip="Enable tracking noise"),
                io.Int.Input("tracking_noise_height", default=12, min=0, max=120, step=1,
                    tooltip="Tracking noise height"),
                io.Float.Input("tracking_noise_wave_intensity", default=15.0, min=-50.0, max=50.0, step=0.5,
                    tooltip="Wave intensity"),
                io.Float.Input("tracking_noise_snow_intensity", default=0.025, min=0.0, max=1.0, step=0.001,
                    tooltip="Snow speckle intensity"),
                io.Float.Input("tracking_noise_snow_anisotropy", default=0.25, min=0.0, max=1.0, step=0.01,
                    tooltip="Snow anisotropy"),
                io.Float.Input("tracking_noise_noise_intensity", default=0.25, min=0.0, max=1.0, step=0.01,
                    tooltip="Non-speckle noise intensity"),

                io.Header.Input("composite_noise", "Composite Noise", tooltip="Composite signal noise"),

                io.Boolean.Input("composite_noise_enabled", default=True,
                    tooltip="Enable composite noise"),
                io.Float.Input("composite_noise_intensity", default=0.05, min=0.0, max=1.0, step=0.001,
                    tooltip="Composite noise intensity"),
                io.Float.Input("composite_noise_frequency", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Composite noise frequency"),
                io.Int.Input("composite_noise_detail", default=1, min=1, max=5, step=1,
                    tooltip="Composite noise detail (octaves)"),

                io.Header.Input("luma_noise", "Luma Noise", tooltip="Luminance noise"),

                io.Boolean.Input("luma_noise_enabled", default=True,
                    tooltip="Enable luminance noise"),
                io.Float.Input("luma_noise_intensity", default=0.01, min=0.0, max=1.0, step=0.001,
                    tooltip="Luminance noise intensity"),
                io.Float.Input("luma_noise_frequency", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Luminance noise frequency"),
                io.Int.Input("luma_noise_detail", default=1, min=1, max=5, step=1,
                    tooltip="Luminance noise detail (octaves)"),

                io.Header.Input("chroma_noise", "Chroma Noise", tooltip="Chrominance noise"),

                io.Boolean.Input("chroma_noise_enabled", default=True,
                    tooltip="Enable chrominance noise"),
                io.Float.Input("chroma_noise_intensity", default=0.1, min=0.0, max=1.0, step=0.001,
                    tooltip="Chrominance noise intensity"),
                io.Float.Input("chroma_noise_frequency", default=0.05, min=0.0, max=0.5, step=0.001,
                    tooltip="Chrominance noise frequency"),
                io.Int.Input("chroma_noise_detail", default=2, min=1, max=5, step=1,
                    tooltip="Chrominance noise detail (octaves)"),

                io.Header.Input("ringing", "Ringing Artifacts", tooltip="Ringing artifact emulation"),

                io.Boolean.Input("ringing_enabled", default=True,
                    tooltip="Enable ringing artifacts"),
                io.Float.Input("ringing_frequency", default=0.45, min=0.0, max=1.0, step=0.01,
                    tooltip="Ringing frequency"),
                io.Float.Input("ringing_power", default=4.0, min=1.0, max=10.0, step=0.1,
                    tooltip="Ringing power"),
                io.Float.Input("ringing_intensity", default=4.0, min=0.0, max=10.0, step=0.1,
                    tooltip="Ringing intensity"),

                io.Header.Input("vhs_settings", "VHS Settings", tooltip="VHS tape emulation"),

                io.Boolean.Input("vhs_enabled", default=True,
                    tooltip="Enable VHS settings"),
                io.Combo.Input(
                    "vhs_tape_speed",
                    options=VHS_TAPE_SPEED_OPTIONS,
                    default="LP",
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

                io.Header.Input("global_effects", "Global Effects", tooltip="Global noise and distortion effects"),

                io.Float.Input("snow_intensity", default=0.00025, min=0.0, max=100.0, step=0.00001,
                    tooltip="Snow speckle frequency (logarithmic)"),
                io.Float.Input("snow_anisotropy", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Snow anisotropy (row clustering)"),
                io.Float.Input("chroma_phase_noise_intensity", default=0.001, min=0.0, max=1.0, step=0.0001,
                    tooltip="Chroma phase noise intensity (logarithmic)"),
                io.Float.Input("chroma_phase_error", default=0.0, min=0.0, max=1.0, step=0.001,
                    tooltip="Chroma phase error"),
                io.Float.Input("chroma_delay_horizontal", default=0.0, min=-40.0, max=40.0, step=0.1,
                    tooltip="Horizontal chroma delay (pixels)"),
                io.Int.Input("chroma_delay_vertical", default=0, min=-20, max=20, step=1,
                    tooltip="Vertical chroma delay (scanlines)"),

                io.Header.Input("scale_settings", "Scale Settings", tooltip="Effect scaling"),

                io.Boolean.Input("scale_enabled", default=True,
                    tooltip="Enable scale settings"),
                io.Float.Input("horizontal_scale", default=1.0, min=0.125, max=8.0, step=0.125,
                    tooltip="Horizontal scale factor"),
                io.Float.Input("vertical_scale", default=1.0, min=0.125, max=8.0, step=0.125,
                    tooltip="Vertical scale factor"),
                io.Boolean.Input("scale_with_video_size", default=False,
                    tooltip="Multiply scale by video height"),

                io.Header.Input("misc", "Miscellaneous", tooltip="Other settings"),

                io.Int.Input("random_seed", default=0, min=-2147483648, max=2147483647, step=1,
                    tooltip="Random seed for noise generation"),

                io.Int.Input("frame_num", default=0, min=0, max=2147483647, step=1,
                    tooltip="Frame number (for temporal effects)"),
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
            search_aliases=["ntsc", "ntsc_rs", "vhs", "crt", "retro", "full"],
        )

    @classmethod
    def build_params_dict(cls, **kwargs) -> dict:
        """Build parameters dictionary from kwargs."""
        return {k: v for k, v in kwargs.items() if v is not None}

    @classmethod
    def process(cls, image, **kwargs):
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

        params = cls.build_params_dict(**kwargs)

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
    async def execute(cls, image, **kwargs):
        return cls.process(image, **kwargs)