"""NTSC-RS Intermediate Node - Preset with scaling controls.

This node provides preset-based VHS/CRT looks with additional
control over resolution scaling and output size.

Note: Resolution scaling is done via PyTorch interpolation, not ntsc-rs
internal scale parameters (which affect signal processing, not dimensions).
"""

from comfy_api.latest import io

from .native import apply_ntsc
from .ntsc_node_scale import get_scale_values, resize
from .ntsc_presets import apply_intensity_to_preset, get_preset, get_preset_names

SCALE_PRESET_OPTIONS = ["Source (1x)", "Half (0.5x)", "Quarter (0.25x)", "Double (2x)", "Custom"]

FIELD_MODE_OPTIONS = ["InterleavedUpper", "InterleavedLower", "Both", "Alternating"]


class NtscRsIntermediateNode(io.ComfyNode):
    """Intermediate NTSC-RS node with presets and scaling controls."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Intermediate",
            display_name="NTSC-RS Intermediate",
            category="NTSC",
            description="VHS/CRT effect with preset configurations and scaling controls. Balance between simplicity and full parameter control.",
            inputs=[
                io.Image.Input(
                    "image", display_name="Image", tooltip="Image to apply NTSC effect to"
                ),
                # Preset Selection
                io.Combo.Input(
                    "preset",
                    display_name="Preset",
                    options=get_preset_names(),
                    default="vhs_classic",
                    tooltip="Preset configuration",
                ),
                io.Float.Input(
                    "intensity",
                    display_name="Intensity",
                    default=1.0,
                    min=0.0,
                    max=1.0,
                    step=0.01,
                    tooltip="Effect intensity multiplier",
                ),
                # Scaling Section
                io.Combo.Input(
                    "scale_preset",
                    display_name="Scale Preset",
                    options=SCALE_PRESET_OPTIONS,
                    default="Source (1x)",
                    tooltip="Output resolution preset",
                ),
                io.Float.Input(
                    "horizontal_scale",
                    display_name="H Scale",
                    default=1.0,
                    min=0.125,
                    max=8.0,
                    step=0.125,
                    tooltip="Horizontal scale factor (for Custom preset)",
                ),
                io.Float.Input(
                    "vertical_scale",
                    display_name="V Scale",
                    default=1.0,
                    min=0.125,
                    max=8.0,
                    step=0.125,
                    tooltip="Vertical scale factor (for Custom preset)",
                ),
                # Additional Controls
                io.Combo.Input(
                    "field_mode",
                    display_name="Field Mode",
                    options=FIELD_MODE_OPTIONS,
                    default="InterleavedUpper",
                    tooltip="Field processing mode",
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
                io.Image.Output(display_name="Image", tooltip="Processed image"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image,
        preset,
        intensity,
        scale_preset,
        horizontal_scale,
        vertical_scale,
        field_mode,
        random_seed,
    ):
        preset_config = get_preset(preset)
        preset_config["random_seed"] = random_seed
        preset_config["use_field"] = field_mode
        if intensity < 1.0:
            preset_config = apply_intensity_to_preset(preset_config, intensity)

        h_scale, v_scale = get_scale_values(scale_preset, horizontal_scale, vertical_scale)
        return io.NodeOutput(resize(apply_ntsc(image, preset_config), h_scale, v_scale))
