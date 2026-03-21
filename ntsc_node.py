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
            display_name="NTSC-RS Advanced",
            category="NTSC",
            description="Full NTSC/VHS/CRT effect with complete parameter control. 1:1 quality with ntsc-rs library.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to apply NTSC effect to"),

                # Signal Processing
                io.Combo.Input("filter_type", "Filter Type",
                    options=FILTER_TYPE_OPTIONS,
                    default="Butterworth",
                    tooltip="NTSC decode filter type",
                ),
                io.Combo.Input("input_luma_filter", "Luma Filter",
                    options=LUMA_LOWPASS_OPTIONS,
                    default="Notch",
                    tooltip="Input luminance low-pass filter",
                ),
                io.Combo.Input("chroma_lowpass_in", "Chroma Lowpass In",
                    options=CHROMA_LOWPASS_OPTIONS,
                    default="Full",
                    tooltip="Input chroma low-pass filter",
                ),
                io.Combo.Input("chroma_demodulation", "Chroma Demodulation",
                    options=CHROMA_DEMOD_OPTIONS,
                    default="Notch",
                    tooltip="Chroma demodulation filter",
                ),
                io.Combo.Input("chroma_lowpass_out", "Chroma Lowpass Out",
                    options=CHROMA_LOWPASS_OPTIONS,
                    default="Full",
                    tooltip="Output chroma low-pass filter",
                ),
                io.Float.Input("luma_smear", display_name="Luma Smear", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Luminance smear amount"),
                io.Float.Input("composite_sharpening", display_name="Sharpening", default=1.0, min=-1.0, max=2.0, step=0.01,
                    tooltip="Composite sharpening/preemphasis"),
                io.Boolean.Input("chroma_vert_blend", display_name="Chroma Vert Blend", default=True,
                    tooltip="Vertically blend chroma between scanlines"),

                # Field/Line Processing
                io.Combo.Input("use_field", "Field Mode",
                    options=USE_FIELD_OPTIONS,
                    default="InterleavedUpper",
                    tooltip="Field usage mode",
                ),
                io.Combo.Input("video_scanline_phase_shift", "Scanline Phase",
                    options=PHASE_SHIFT_OPTIONS,
                    default="Degrees180",
                    tooltip="Video scanline phase shift",
                ),
                io.Int.Input("phase_offset", display_name="Phase Offset", default=0, min=0, max=3, step=1,
                    tooltip="Phase shift offset"),

                # Head Switching
                io.Boolean.Input("head_switching_enabled", display_name="Head Switching On", default=True,
                    tooltip="Enable head switching effect"),
                io.Int.Input("head_switching_height", display_name="Head Height", default=8, min=0, max=24, step=1,
                    tooltip="Height of head switching artifact"),
                io.Int.Input("head_switching_offset", display_name="Head Offset", default=3, min=0, max=24, step=1,
                    tooltip="Head switching offset"),
                io.Float.Input("head_switching_horizontal_shift", display_name="Horizontal Shift", default=72.0, min=-100.0, max=100.0, step=0.5,
                    tooltip="Horizontal shift amount"),
                io.Boolean.Input("head_switching_mid_line_enabled", display_name="Mid Line On", default=True,
                    tooltip="Enable mid-line head switching"),
                io.Float.Input("head_switching_mid_line_position", display_name="Mid Line Pos", default=0.95, min=0.0, max=1.0, step=0.01,
                    tooltip="Mid-line position"),
                io.Float.Input("head_switching_mid_line_jitter", display_name="Mid Line Jitter", default=0.03, min=0.0, max=1.0, step=0.001,
                    tooltip="Mid-line jitter amount"),

                # Tracking Noise
                io.Boolean.Input("tracking_noise_enabled", display_name="Tracking Noise On", default=True,
                    tooltip="Enable tracking noise"),
                io.Int.Input("tracking_noise_height", display_name="Tracking Height", default=12, min=0, max=120, step=1,
                    tooltip="Tracking noise height"),
                io.Float.Input("tracking_noise_wave_intensity", display_name="Wave Intensity", default=15.0, min=-50.0, max=50.0, step=0.5,
                    tooltip="Wave intensity"),
                io.Float.Input("tracking_noise_snow_intensity", display_name="Snow Intensity", default=0.025, min=0.0, max=1.0, step=0.001,
                    tooltip="Snow speckle intensity"),
                io.Float.Input("tracking_noise_snow_anisotropy", display_name="Snow Anisotropy", default=0.25, min=0.0, max=1.0, step=0.01,
                    tooltip="Snow anisotropy"),
                io.Float.Input("tracking_noise_noise_intensity", display_name="Noise Intensity", default=0.25, min=0.0, max=1.0, step=0.01,
                    tooltip="Non-speckle noise intensity"),

                # Composite Noise
                io.Boolean.Input("composite_noise_enabled", display_name="Composite Noise On", default=True,
                    tooltip="Enable composite noise"),
                io.Float.Input("composite_noise_intensity", display_name="Composite Intensity", default=0.05, min=0.0, max=1.0, step=0.001,
                    tooltip="Composite noise intensity"),
                io.Float.Input("composite_noise_frequency", display_name="Composite Frequency", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Composite noise frequency"),
                io.Int.Input("composite_noise_detail", display_name="Composite Detail", default=1, min=1, max=5, step=1,
                    tooltip="Composite noise detail (octaves)"),

                # Luma Noise
                io.Boolean.Input("luma_noise_enabled", display_name="Luma Noise On", default=True,
                    tooltip="Enable luminance noise"),
                io.Float.Input("luma_noise_intensity", display_name="Luma Intensity", default=0.01, min=0.0, max=1.0, step=0.001,
                    tooltip="Luminance noise intensity"),
                io.Float.Input("luma_noise_frequency", display_name="Luma Frequency", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Luminance noise frequency"),
                io.Int.Input("luma_noise_detail", display_name="Luma Detail", default=1, min=1, max=5, step=1,
                    tooltip="Luminance noise detail (octaves)"),

                # Chroma Noise
                io.Boolean.Input("chroma_noise_enabled", display_name="Chroma Noise On", default=True,
                    tooltip="Enable chrominance noise"),
                io.Float.Input("chroma_noise_intensity", display_name="Chroma Intensity", default=0.1, min=0.0, max=1.0, step=0.001,
                    tooltip="Chrominance noise intensity"),
                io.Float.Input("chroma_noise_frequency", display_name="Chroma Frequency", default=0.05, min=0.0, max=0.5, step=0.001,
                    tooltip="Chrominance noise frequency"),
                io.Int.Input("chroma_noise_detail", display_name="Chroma Detail", default=2, min=1, max=5, step=1,
                    tooltip="Chrominance noise detail (octaves)"),

                # Ringing
                io.Boolean.Input("ringing_enabled", display_name="Ringing On", default=True,
                    tooltip="Enable ringing artifacts"),
                io.Float.Input("ringing_frequency", display_name="Ringing Freq", default=0.45, min=0.0, max=1.0, step=0.01,
                    tooltip="Ringing frequency"),
                io.Float.Input("ringing_power", display_name="Ringing Power", default=4.0, min=1.0, max=10.0, step=0.1,
                    tooltip="Ringing power"),
                io.Float.Input("ringing_intensity", display_name="Ringing Intensity", default=4.0, min=0.0, max=10.0, step=0.1,
                    tooltip="Ringing intensity"),

                # VHS Settings
                io.Boolean.Input("vhs_enabled", display_name="VHS On", default=True,
                    tooltip="Enable VHS settings"),
                io.Combo.Input("vhs_tape_speed", "Tape Speed",
                    options=VHS_TAPE_SPEED_OPTIONS,
                    default="LP",
                    tooltip="VHS tape speed (affects high-frequency cutoff)",
                ),
                io.Float.Input("vhs_chroma_loss", display_name="Chroma Loss", default=0.000025, min=0.0, max=1.0, step=0.000001,
                    tooltip="Chroma loss probability per scanline"),
                io.Boolean.Input("vhs_sharpen_enabled", display_name="Sharpen On", default=True,
                    tooltip="Enable VHS sharpening"),
                io.Float.Input("vhs_sharpen_intensity", display_name="Sharpen Intensity", default=0.25, min=0.0, max=5.0, step=0.01,
                    tooltip="VHS sharpen intensity"),
                io.Float.Input("vhs_sharpen_frequency", display_name="Sharpen Freq", default=1.0, min=0.5, max=4.0, step=0.01,
                    tooltip="VHS sharpen frequency"),
                io.Boolean.Input("vhs_edge_wave_enabled", display_name="Edge Wave On", default=True,
                    tooltip="Enable edge wave effect"),
                io.Float.Input("vhs_edge_wave_intensity", display_name="Edge Intensity", default=0.5, min=0.0, max=20.0, step=0.01,
                    tooltip="Edge wave intensity (pixels)"),
                io.Float.Input("vhs_edge_wave_speed", display_name="Edge Speed", default=4.0, min=0.0, max=10.0, step=0.1,
                    tooltip="Edge wave speed"),
                io.Float.Input("vhs_edge_wave_frequency", display_name="Edge Freq", default=0.05, min=0.0, max=0.5, step=0.001,
                    tooltip="Edge wave frequency"),
                io.Int.Input("vhs_edge_wave_detail", display_name="Edge Detail", default=2, min=1, max=5, step=1,
                    tooltip="Edge wave detail (octaves)"),

                # Global Effects
                io.Float.Input("snow_intensity", display_name="Snow Intensity", default=0.00025, min=0.0, max=100.0, step=0.00001,
                    tooltip="Snow speckle frequency (logarithmic)"),
                io.Float.Input("snow_anisotropy", display_name="Snow Anisotropy", default=0.5, min=0.0, max=1.0, step=0.01,
                    tooltip="Snow anisotropy (row clustering)"),
                io.Float.Input("chroma_phase_noise_intensity", display_name="Phase Noise", default=0.001, min=0.0, max=1.0, step=0.0001,
                    tooltip="Chroma phase noise intensity (logarithmic)"),
                io.Float.Input("chroma_phase_error", display_name="Phase Error", default=0.0, min=0.0, max=1.0, step=0.001,
                    tooltip="Chroma phase error"),
                io.Float.Input("chroma_delay_horizontal", display_name="H Chroma Delay", default=0.0, min=-40.0, max=40.0, step=0.1,
                    tooltip="Horizontal chroma delay (pixels)"),
                io.Int.Input("chroma_delay_vertical", display_name="V Chroma Delay", default=0, min=-20, max=20, step=1,
                    tooltip="Vertical chroma delay (scanlines)"),

                # Scale Settings
                io.Boolean.Input("scale_enabled", display_name="Scale On", default=True,
                    tooltip="Enable scale settings"),
                io.Float.Input("horizontal_scale", display_name="H Scale", default=1.0, min=0.125, max=8.0, step=0.125,
                    tooltip="Horizontal scale factor"),
                io.Float.Input("vertical_scale", display_name="V Scale", default=1.0, min=0.125, max=8.0, step=0.125,
                    tooltip="Vertical scale factor"),
                io.Boolean.Input("scale_with_video_size", display_name="Scale With Size", default=False,
                    tooltip="Multiply scale by video height"),

                # Misc
                io.Int.Input("random_seed", display_name="Seed", default=0, min=-2147483648, max=2147483647, step=1,
                    tooltip="Random seed for noise generation"),
                io.Int.Input("frame_num", display_name="Frame Num", default=0, min=0, max=2147483647, step=1,
                    tooltip="Frame number (for temporal effects)"),
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
