"""NTSC-RS Simple Node - Preset-based VHS/CRT effect.

This node provides quick access to common VHS/CRT looks using presets.
For full control over all parameters, use NtscRsNode instead.
"""

from comfy_api.latest import io

from .native import apply_ntsc
from .ntsc_presets import apply_intensity_to_preset, get_preset, get_preset_names


class NtscRsSimpleNode(io.ComfyNode):
    """Simple NTSC-RS node with preset-based VHS/CRT effects."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="NtscRs_Simple",
            display_name="NTSC-RS Simple",
            category="NTSC",
            description="VHS/CRT effect with preset configurations. For full parameter control, use the Advanced node.",
            inputs=[
                io.Image.Input(
                    "image", display_name="Image", tooltip="Image to apply NTSC effect to"
                ),
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
                io.Float.Input(
                    "saturation",
                    display_name="Saturation",
                    default=0.25,
                    min=-1.0,
                    max=2.0,
                    step=0.01,
                    tooltip="Color saturation adjustment",
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
    def execute(cls, image, preset, intensity, saturation, random_seed):
        preset_config = get_preset(preset)
        preset_config["random_seed"] = random_seed
        preset_config["composite_sharpening"] = preset_config.get("composite_sharpening", 1.0) * (
            1.0 + saturation
        )
        if intensity < 1.0:
            preset_config = apply_intensity_to_preset(preset_config, intensity)
        return io.NodeOutput(apply_ntsc(image, preset_config))
