"""NTSC Global Effects Node.

Applies global effects: snow, chroma phase noise/error, chroma delay.
Part of the chainable NTSC-RS node system.
"""

from comfy_api.latest import io

from .native import apply_ntsc


class NtscRsGlobalNode(io.ComfyNode):
    """NTSC Global Effects node - snow, chroma phase, delays."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Global",
            display_name="NTSC-RS Global",
            category="NTSC",
            description="Global effects: snow speckles, chroma phase noise/error, chroma delay. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to process"),
                io.Float.Input(
                    "snow_intensity",
                    display_name="Snow Intensity",
                    default=0.00025,
                    min=0.0,
                    max=100.0,
                    step=0.00001,
                    tooltip="Snow speckle frequency (logarithmic)",
                ),
                io.Float.Input(
                    "snow_anisotropy",
                    display_name="Snow Anisotropy",
                    default=0.5,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    tooltip="Snow anisotropy (row clustering)",
                ),
                io.Float.Input(
                    "chroma_phase_noise_intensity",
                    display_name="Chroma Phase Noise",
                    default=0.001,
                    min=0.0,
                    max=1.0,
                    step=0.0001,
                    tooltip="Chroma phase noise intensity (logarithmic)",
                ),
                io.Float.Input(
                    "chroma_phase_error",
                    display_name="Chroma Phase Error",
                    default=0.0,
                    min=0.0,
                    max=1.0,
                    step=0.001,
                    tooltip="Chroma phase error",
                ),
                io.Float.Input(
                    "chroma_delay_horizontal",
                    display_name="Chroma Delay H",
                    default=0.0,
                    min=-40.0,
                    max=40.0,
                    step=0.1,
                    tooltip="Horizontal chroma delay (pixels)",
                ),
                io.Int.Input(
                    "chroma_delay_vertical",
                    display_name="Chroma Delay V",
                    default=0,
                    min=-20,
                    max=20,
                    step=1,
                    tooltip="Vertical chroma delay (scanlines)",
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
        snow_intensity,
        snow_anisotropy,
        chroma_phase_noise_intensity,
        chroma_phase_error,
        chroma_delay_horizontal,
        chroma_delay_vertical,
        random_seed,
    ):
        """Process the image through NTSC global effects."""
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
            "composite_noise_enabled": False,
            "luma_noise_enabled": False,
            "chroma_noise_enabled": False,
            "ringing_enabled": False,
            "vhs_enabled": False,
            # Enable global effects
            "snow_intensity": snow_intensity,
            "snow_anisotropy": snow_anisotropy,
            "chroma_phase_noise_intensity": chroma_phase_noise_intensity,
            "chroma_phase_error": chroma_phase_error,
            "chroma_delay_horizontal": chroma_delay_horizontal,
            "chroma_delay_vertical": chroma_delay_vertical,
            # Disable scale
            "scale_enabled": True,
            "horizontal_scale": 1.0,
            "vertical_scale": 1.0,
            "scale_with_video_size": False,
            "random_seed": random_seed,
        }

        return io.NodeOutput(apply_ntsc(image, params))
