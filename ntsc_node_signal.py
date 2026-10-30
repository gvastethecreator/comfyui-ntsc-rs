"""NTSC Signal Processing Node.

Applies signal processing effects: filter type, luma/chroma filters, smear, sharpening.
Part of the chainable NTSC-RS node system.
"""

from comfy_api.latest import io

from .native import apply_ntsc

FILTER_TYPE_OPTIONS = ["ConstantK", "Butterworth"]
LUMA_LOWPASS_OPTIONS = ["None", "Box", "Notch"]
CHROMA_LOWPASS_OPTIONS = ["None", "Light", "Full"]
CHROMA_DEMOD_OPTIONS = ["Box", "Notch", "OneLineComb", "TwoLineComb"]


class NtscRsSignalNode(io.ComfyNode):
    """NTSC Signal Processing node - filter type, luma/chroma filters, smear, sharpening."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Signal",
            display_name="NTSC-RS Signal",
            category="NTSC",
            description="Signal processing: filter type, luma/chroma filters, smear, and sharpening. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to process"),
                io.Combo.Input(
                    "filter_type",
                    display_name="Filter Type",
                    options=FILTER_TYPE_OPTIONS,
                    default="Butterworth",
                    tooltip="NTSC decode filter type",
                ),
                io.Combo.Input(
                    "input_luma_filter",
                    display_name="Luma Filter",
                    options=LUMA_LOWPASS_OPTIONS,
                    default="Notch",
                    tooltip="Input luminance low-pass filter",
                ),
                io.Combo.Input(
                    "chroma_lowpass_in",
                    display_name="Chroma Lowpass In",
                    options=CHROMA_LOWPASS_OPTIONS,
                    default="Full",
                    tooltip="Input chroma low-pass filter",
                ),
                io.Combo.Input(
                    "chroma_demodulation",
                    display_name="Chroma Demodulation",
                    options=CHROMA_DEMOD_OPTIONS,
                    default="Notch",
                    tooltip="Chroma demodulation filter",
                ),
                io.Combo.Input(
                    "chroma_lowpass_out",
                    display_name="Chroma Lowpass Out",
                    options=CHROMA_LOWPASS_OPTIONS,
                    default="Full",
                    tooltip="Output chroma low-pass filter",
                ),
                io.Float.Input(
                    "luma_smear",
                    display_name="Luma Smear",
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    tooltip="Luminance smear amount",
                ),
                io.Float.Input(
                    "composite_sharpening",
                    display_name="Sharpening",
                    default=1.0,
                    min=-1.0,
                    max=2.0,
                    step=0.01,
                    tooltip="Composite sharpening/preemphasis",
                ),
                io.Boolean.Input(
                    "chroma_vert_blend",
                    display_name="Chroma Vert Blend",
                    default=True,
                    tooltip="Vertically blend chroma between scanlines",
                ),
            ],
            outputs=[
                io.Image.Output(display_name="Image", tooltip="Processed image"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image,
        filter_type,
        input_luma_filter,
        chroma_lowpass_in,
        chroma_demodulation,
        chroma_lowpass_out,
        luma_smear,
        composite_sharpening,
        chroma_vert_blend,
    ):
        """Process the image through NTSC signal effects."""
        params = {
            "filter_type": filter_type,
            "input_luma_filter": input_luma_filter,
            "chroma_lowpass_in": chroma_lowpass_in,
            "chroma_demodulation": chroma_demodulation,
            "chroma_lowpass_out": chroma_lowpass_out,
            "luma_smear": luma_smear,
            "composite_sharpening": composite_sharpening,
            "chroma_vert_blend": chroma_vert_blend,
            # Disable all other effects
            "use_field": "InterleavedUpper",
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
