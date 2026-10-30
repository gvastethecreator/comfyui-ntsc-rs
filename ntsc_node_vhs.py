"""NTSC VHS Node.

Applies VHS-specific effects: tape speed, chroma loss, sharpen, edge wave.
Part of the chainable NTSC-RS node system.
"""

from comfy_api.latest import io

from .native import apply_ntsc

VHS_TAPE_SPEED_OPTIONS = ["NONE", "SP", "LP", "EP"]


class NtscRsVHSNode(io.ComfyNode):
    """NTSC VHS node - tape speed, chroma loss, sharpen, edge wave effects."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_VHS",
            display_name="NTSC-RS VHS",
            category="NTSC",
            description="VHS-specific effects: tape speed, chroma loss, sharpening, edge wave. Chain after other NTSC category nodes.",
            inputs=[
                io.Image.Input("image", display_name="Image", tooltip="Image to process"),
                io.Combo.Input(
                    "vhs_tape_speed",
                    display_name="VHS Tape Speed",
                    options=VHS_TAPE_SPEED_OPTIONS,
                    default="SP",
                    tooltip="VHS tape speed (affects high-frequency cutoff)",
                ),
                io.Float.Input(
                    "vhs_chroma_loss",
                    display_name="VHS Chroma Loss",
                    default=0.000025,
                    min=0.0,
                    max=1.0,
                    step=0.000001,
                    tooltip="Chroma loss probability per scanline",
                ),
                io.Boolean.Input(
                    "vhs_sharpen_enabled",
                    display_name="VHS Sharpen",
                    default=True,
                    tooltip="Enable VHS sharpening",
                ),
                io.Float.Input(
                    "vhs_sharpen_intensity",
                    display_name="Sharpen Intensity",
                    default=0.25,
                    min=0.0,
                    max=5.0,
                    step=0.01,
                    tooltip="VHS sharpen intensity",
                ),
                io.Float.Input(
                    "vhs_sharpen_frequency",
                    display_name="Sharpen Frequency",
                    default=1.0,
                    min=0.5,
                    max=4.0,
                    step=0.01,
                    tooltip="VHS sharpen frequency",
                ),
                io.Boolean.Input(
                    "vhs_edge_wave_enabled",
                    display_name="Edge Wave",
                    default=True,
                    tooltip="Enable edge wave effect",
                ),
                io.Float.Input(
                    "vhs_edge_wave_intensity",
                    display_name="Edge Wave Intensity",
                    default=0.5,
                    min=0.0,
                    max=20.0,
                    step=0.01,
                    tooltip="Edge wave intensity (pixels)",
                ),
                io.Float.Input(
                    "vhs_edge_wave_speed",
                    display_name="Edge Wave Speed",
                    default=4.0,
                    min=0.0,
                    max=10.0,
                    step=0.1,
                    tooltip="Edge wave speed",
                ),
                io.Float.Input(
                    "vhs_edge_wave_frequency",
                    display_name="Edge Wave Frequency",
                    default=0.05,
                    min=0.0,
                    max=0.5,
                    step=0.001,
                    tooltip="Edge wave frequency",
                ),
                io.Int.Input(
                    "vhs_edge_wave_detail",
                    display_name="Edge Wave Detail",
                    default=2,
                    min=1,
                    max=5,
                    step=1,
                    tooltip="Edge wave detail (octaves)",
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
        vhs_tape_speed,
        vhs_chroma_loss,
        vhs_sharpen_enabled,
        vhs_sharpen_intensity,
        vhs_sharpen_frequency,
        vhs_edge_wave_enabled,
        vhs_edge_wave_intensity,
        vhs_edge_wave_speed,
        vhs_edge_wave_frequency,
        vhs_edge_wave_detail,
        random_seed,
    ):
        """Process the image through NTSC VHS effects."""
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

        return io.NodeOutput(apply_ntsc(image, params))
