"""ComfyUI NTSC-RS extension entry points and legacy node mappings."""

from comfy_api.latest import ComfyExtension

from .ntsc_node import NtscRsNode
from .ntsc_node_artifacts import NtscRsArtifactsNode
from .ntsc_node_global import NtscRsGlobalNode
from .ntsc_node_intermediate import NtscRsIntermediateNode
from .ntsc_node_noise import NtscRsNoiseNode
from .ntsc_node_scale import NtscRsScaleNode
from .ntsc_node_scanlines import NtscRsScanlinesNode
from .ntsc_node_signal import NtscRsSignalNode
from .ntsc_node_simple import NtscRsSimpleNode
from .ntsc_node_vhs import NtscRsVHSNode

NODE_CLASSES = (
    NtscRsNode,
    NtscRsSimpleNode,
    NtscRsIntermediateNode,
    NtscRsSignalNode,
    NtscRsScanlinesNode,
    NtscRsArtifactsNode,
    NtscRsNoiseNode,
    NtscRsVHSNode,
    NtscRsGlobalNode,
    NtscRsScaleNode,
)


class NtscRsExtension(ComfyExtension):
    """Register the full and chainable NTSC-RS nodes with ComfyUI."""

    async def get_node_list(self):
        return list(NODE_CLASSES)

    async def on_load(self):
        print("[NTSC-RS] Loaded 10 nodes (3 full, 7 chainable).", flush=True)


async def comfy_entrypoint() -> NtscRsExtension:
    """Return the extension instance for the current ComfyUI API."""
    return NtscRsExtension()


# Keep the legacy mappings for older ComfyUI loaders.
NODE_CLASS_MAPPINGS = {
    "NtscRs_Advanced": NtscRsNode,
    "NtscRs_Simple": NtscRsSimpleNode,
    "NtscRs_Intermediate": NtscRsIntermediateNode,
    "NtscRs_Signal": NtscRsSignalNode,
    "NtscRs_Scanlines": NtscRsScanlinesNode,
    "NtscRs_Artifacts": NtscRsArtifactsNode,
    "NtscRs_Noise": NtscRsNoiseNode,
    "NtscRs_VHS": NtscRsVHSNode,
    "NtscRs_Global": NtscRsGlobalNode,
    "NtscRs_Scale": NtscRsScaleNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NtscRs_Advanced": "NTSC-RS Advanced",
    "NtscRs_Simple": "NTSC-RS Simple",
    "NtscRs_Intermediate": "NTSC-RS Intermediate",
    "NtscRs_Signal": "NTSC-RS Signal",
    "NtscRs_Scanlines": "NTSC-RS Scanlines",
    "NtscRs_Artifacts": "NTSC-RS Artifacts",
    "NtscRs_Noise": "NTSC-RS Noise",
    "NtscRs_VHS": "NTSC-RS VHS",
    "NtscRs_Global": "NTSC-RS Global",
    "NtscRs_Scale": "NTSC-RS Scale",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "NtscRsArtifactsNode",
    "NtscRsExtension",
    "NtscRsGlobalNode",
    "NtscRsIntermediateNode",
    "NtscRsNode",
    "NtscRsNoiseNode",
    "NtscRsScaleNode",
    "NtscRsScanlinesNode",
    "NtscRsSignalNode",
    "NtscRsSimpleNode",
    "NtscRsVHSNode",
    "comfy_entrypoint",
]
