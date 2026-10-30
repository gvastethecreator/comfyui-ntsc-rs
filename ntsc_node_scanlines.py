"""NTSC Scanlines Node.

Applies field/scanline processing: field mode, scanline phase shift.
Part of the chainable NTSC-RS node system.
"""

from comfy_api.latest import io

from .native import apply_ntsc

USE_FIELD_OPTIONS = [
    "Alternating",
    "Upper",
    "Lower",
    "Both",
    "InterleavedUpper",
    "InterleavedLower",
]
PHASE_SHIFT_OPTIONS = ["Degrees0", "Degrees90", "Degrees180", "Degrees270"]


class NtscRsScanlinesNode(io.ComfyNode):
    """NTSC Scanlines node - field mode and scanline phase processing."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Scanlines",
            display_name="NTSC-RS Scanlines",
            category="NTSC",
            description="Field and scanline processing: field mode and scanline phase shift. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to process"),
                io.Combo.Input(
                    "use_field",
                    display_name="Use Field",
                    options=USE_FIELD_OPTIONS,
                    default="InterleavedUpper",
                    tooltip="Field usage mode",
                ),
                io.Combo.Input(
                    "video_scanline_phase_shift",
                    display_name="Video Scanline Phase Shift",
                    options=PHASE_SHIFT_OPTIONS,
                    default="Degrees180",
                    tooltip="Video scanline phase shift",
                ),
                io.Int.Input(
                    "video_scanline_phase_shift_offset",
                    display_name="Phase Shift Offset",
                    default=0,
                    min=0,
                    max=3,
                    step=1,
                    tooltip="Phase shift offset",
                ),
            ],
            outputs=[
                io.Image.Output(tooltip="Processed image"),
            ],
        )

    @classmethod
    def execute(
        cls, image, use_field, video_scanline_phase_shift, video_scanline_phase_shift_offset
    ):
        """Process the image through NTSC scanline effects."""
        params = {
            # Neutral signal stage: the Signal node owns these. Re-applying ntsc-rs defaults
            # here compounded pre-emphasis on every chained pass (strong colour shift).
            "filter_type": "Butterworth",
            "input_luma_filter": "None",
            "chroma_lowpass_in": "None",
            "chroma_demodulation": "Notch",
            "chroma_lowpass_out": "None",
            "luma_smear": 0.0,
            "composite_sharpening": 0.0,
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

        return io.NodeOutput(apply_ntsc(image, params))
