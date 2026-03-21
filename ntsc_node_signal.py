"""NTSC Signal Processing Node.

Applies signal processing effects: filter type, luma/chroma filters, smear, sharpening.
Part of the chainable NTSC-RS node system.
"""

import torch
import numpy as np

try:
    from comfy_api.latest import io
except ImportError:
    from comfy import io


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

                io.Combo.Input("filter_type", display_name="Filter Type",
                    options=FILTER_TYPE_OPTIONS,
                    default="Butterworth",
                    tooltip="NTSC decode filter type",
                ),
                io.Combo.Input("input_luma_filter", display_name="Luma Filter",
                    options=LUMA_LOWPASS_OPTIONS,
                    default="Notch",
                    tooltip="Input luminance low-pass filter",
                ),
                io.Combo.Input("chroma_lowpass_in", display_name="Chroma Lowpass In",
                    options=CHROMA_LOWPASS_OPTIONS,
                    default="Full",
                    tooltip="Input chroma low-pass filter",
                ),
                io.Combo.Input("chroma_demodulation", display_name="Chroma Demodulation",
                    options=CHROMA_DEMOD_OPTIONS,
                    default="Notch",
                    tooltip="Chroma demodulation filter",
                ),
                io.Combo.Input("chroma_lowpass_out", display_name="Chroma Lowpass Out",
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
            search_aliases=["ntsc", "signal", "filter", "luma", "chroma"],
        )

    @classmethod
    def process(cls, image, filter_type, input_luma_filter, chroma_lowpass_in, chroma_demodulation,
                chroma_lowpass_out, luma_smear, composite_sharpening, chroma_vert_blend):
        """Process the image through NTSC signal effects."""
        try:
            import comfyui_ntsc_rs
            HAS_RUST = True
        except ImportError:
            HAS_RUST = False

        if not HAS_RUST:
            raise ImportError("comfyui_ntsc_rs native module not found.")

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
    async def execute(cls, image, filter_type, input_luma_filter, chroma_lowpass_in, chroma_demodulation,
                     chroma_lowpass_out, luma_smear, composite_sharpening, chroma_vert_blend):
        return cls.process(image, filter_type, input_luma_filter, chroma_lowpass_in, chroma_demodulation,
                          chroma_lowpass_out, luma_smear, composite_sharpening, chroma_vert_blend)
