"""NTSC Noise Node.

Applies noise effects: composite, luma, and chroma noise.
Part of the chainable NTSC-RS node system.
"""

from comfy_api.latest import io

from .native import apply_ntsc


class NtscRsNoiseNode(io.ComfyNode):
    """NTSC Noise node - composite, luma, and chroma noise effects."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Noise",
            display_name="NTSC-RS Noise",
            category="NTSC",
            description="Noise effects: composite, luma, and chroma noise. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to process"),
                io.Boolean.Input(
                    "composite_noise_enabled",
                    display_name="Composite Noise",
                    default=True,
                    tooltip="Enable composite noise",
                ),
                io.Float.Input(
                    "composite_noise_intensity",
                    display_name="Composite Intensity",
                    default=0.05,
                    min=0.0,
                    max=1.0,
                    step=0.001,
                    tooltip="Composite noise intensity",
                ),
                io.Float.Input(
                    "composite_noise_frequency",
                    display_name="Composite Frequency",
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    tooltip="Composite noise frequency",
                ),
                io.Int.Input(
                    "composite_noise_detail",
                    display_name="Composite Detail",
                    default=1,
                    min=1,
                    max=5,
                    step=1,
                    tooltip="Composite noise detail (octaves)",
                ),
                io.Boolean.Input(
                    "luma_noise_enabled",
                    display_name="Luma Noise",
                    default=True,
                    tooltip="Enable luminance noise",
                ),
                io.Float.Input(
                    "luma_noise_intensity",
                    display_name="Luma Intensity",
                    default=0.01,
                    min=0.0,
                    max=1.0,
                    step=0.001,
                    tooltip="Luminance noise intensity",
                ),
                io.Float.Input(
                    "luma_noise_frequency",
                    display_name="Luma Frequency",
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    tooltip="Luminance noise frequency",
                ),
                io.Int.Input(
                    "luma_noise_detail",
                    display_name="Luma Detail",
                    default=1,
                    min=1,
                    max=5,
                    step=1,
                    tooltip="Luminance noise detail (octaves)",
                ),
                io.Boolean.Input(
                    "chroma_noise_enabled",
                    display_name="Chroma Noise",
                    default=True,
                    tooltip="Enable chrominance noise",
                ),
                io.Float.Input(
                    "chroma_noise_intensity",
                    display_name="Chroma Intensity",
                    default=0.1,
                    min=0.0,
                    max=1.0,
                    step=0.001,
                    tooltip="Chrominance noise intensity",
                ),
                io.Float.Input(
                    "chroma_noise_frequency",
                    display_name="Chroma Frequency",
                    default=0.05,
                    min=0.0,
                    max=0.5,
                    step=0.001,
                    tooltip="Chrominance noise frequency",
                ),
                io.Int.Input(
                    "chroma_noise_detail",
                    display_name="Chroma Detail",
                    default=2,
                    min=1,
                    max=5,
                    step=1,
                    tooltip="Chrominance noise detail (octaves)",
                ),
                io.Boolean.Input(
                    "ringing_enabled",
                    display_name="Ringing",
                    default=True,
                    tooltip="Enable ringing artifacts",
                ),
                io.Float.Input(
                    "ringing_frequency",
                    display_name="Ringing Frequency",
                    default=0.45,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    tooltip="Ringing frequency",
                ),
                io.Float.Input(
                    "ringing_power",
                    display_name="Ringing Power",
                    default=4.0,
                    min=1.0,
                    max=10.0,
                    step=0.1,
                    tooltip="Ringing power",
                ),
                io.Float.Input(
                    "ringing_intensity",
                    display_name="Ringing Intensity",
                    default=4.0,
                    min=0.0,
                    max=10.0,
                    step=0.1,
                    tooltip="Ringing intensity",
                ),
                io.Int.Input(
                    "random_seed",
                    display_name="Seed",
                    default=0,
                    min=-2147483648,
                    max=2147483647,
                    step=1,
                    tooltip="Random seed for noise generation",
                ),
            ],
            outputs=[
                io.Image.Output(tooltip="Processed image"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image,
        composite_noise_enabled,
        composite_noise_intensity,
        composite_noise_frequency,
        composite_noise_detail,
        luma_noise_enabled,
        luma_noise_intensity,
        luma_noise_frequency,
        luma_noise_detail,
        chroma_noise_enabled,
        chroma_noise_intensity,
        chroma_noise_frequency,
        chroma_noise_detail,
        ringing_enabled,
        ringing_frequency,
        ringing_power,
        ringing_intensity,
        random_seed,
    ):
        """Process the image through NTSC noise effects."""
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
            "use_field": "InterleavedUpper",
            "video_scanline_phase_shift": "Degrees180",
            "video_scanline_phase_shift_offset": 0,
            "head_switching_enabled": False,
            "tracking_noise_enabled": False,
            # Enable noise
            "composite_noise_enabled": composite_noise_enabled,
            "composite_noise_intensity": composite_noise_intensity,
            "composite_noise_frequency": composite_noise_frequency,
            "composite_noise_detail": composite_noise_detail,
            "luma_noise_enabled": luma_noise_enabled,
            "luma_noise_intensity": luma_noise_intensity,
            "luma_noise_frequency": luma_noise_frequency,
            "luma_noise_detail": luma_noise_detail,
            "chroma_noise_enabled": chroma_noise_enabled,
            "chroma_noise_intensity": chroma_noise_intensity,
            "chroma_noise_frequency": chroma_noise_frequency,
            "chroma_noise_detail": chroma_noise_detail,
            "ringing_enabled": ringing_enabled,
            "ringing_frequency": ringing_frequency,
            "ringing_power": ringing_power,
            "ringing_intensity": ringing_intensity,
            # Disable other effects
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

        return io.NodeOutput(apply_ntsc(image, params))
