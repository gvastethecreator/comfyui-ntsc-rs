"""ComfyUI NTSC-RS Extension.

A ComfyUI custom node extension that provides VHS/CRT/NTSC effects
using the ntsc-rs Rust library for native tensor processing.
"""

print("[NTSC-RS] Extension loading...", flush=True)

try:
    from comfy_api.latest import ComfyExtension, io
    print("[NTSC-RS] Using comfy_api.latest", flush=True)
except ImportError as e:
    print(f"[NTSC-RS] comfy_api.latest import failed: {e}", flush=True)
    raise

# Main nodes
try:
    from .ntsc_node import NtscRsNode
    print(f"[NTSC-RS] NtscRsNode loaded: {NtscRsNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_simple import NtscRsSimpleNode
    print(f"[NTSC-RS] NtscRsSimpleNode loaded: {NtscRsSimpleNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsSimpleNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_intermediate import NtscRsIntermediateNode
    print(f"[NTSC-RS] NtscRsIntermediateNode loaded: {NtscRsIntermediateNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsIntermediateNode: {e}", flush=True)
    raise

# Category nodes
try:
    from .ntsc_node_signal import NtscRsSignalNode
    print(f"[NTSC-RS] NtscRsSignalNode loaded: {NtscRsSignalNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsSignalNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_scanlines import NtscRsScanlinesNode
    print(f"[NTSC-RS] NtscRsScanlinesNode loaded: {NtscRsScanlinesNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsScanlinesNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_artifacts import NtscRsArtifactsNode
    print(f"[NTSC-RS] NtscRsArtifactsNode loaded: {NtscRsArtifactsNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsArtifactsNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_noise import NtscRsNoiseNode
    print(f"[NTSC-RS] NtscRsNoiseNode loaded: {NtscRsNoiseNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsNoiseNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_vhs import NtscRsVHSNode
    print(f"[NTSC-RS] NtscRsVHSNode loaded: {NtscRsVHSNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsVHSNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_global import NtscRsGlobalNode
    print(f"[NTSC-RS] NtscRsGlobalNode loaded: {NtscRsGlobalNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsGlobalNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_scale import NtscRsScaleNode
    print(f"[NTSC-RS] NtscRsScaleNode loaded: {NtscRsScaleNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS] Failed to import NtscRsScaleNode: {e}", flush=True)
    raise


class NtscRsExtension(ComfyExtension):
    """NTSC-RS ComfyUI Extension.

    Provides VHS/CRT/NTSC video effect processing with multiple node types:
    - Full nodes: Simple, Intermediate, Advanced
    - Category nodes: Signal, Scanlines, Artifacts, Noise, VHS, Global, Scale
    """

    async def get_node_list(self):
        """Return list of node classes provided by this extension."""
        return [
            # Full nodes
            NtscRsNode,
            NtscRsSimpleNode,
            NtscRsIntermediateNode,
            # Category nodes (chainable)
            NtscRsSignalNode,
            NtscRsScanlinesNode,
            NtscRsArtifactsNode,
            NtscRsNoiseNode,
            NtscRsVHSNode,
            NtscRsGlobalNode,
            NtscRsScaleNode,
        ]

    async def on_load(self):
        """Called when the extension is loaded."""
        print("[NTSC-RS] Extension loaded successfully!", flush=True)


async def comfy_entrypoint() -> NtscRsExtension:
    """Entry point for ComfyUI to load this extension."""
    print("[NTSC-RS] comfy_entrypoint called", flush=True)
    return NtscRsExtension()


WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    # Full nodes
    "NtscRs_Advanced": NtscRsNode,
    "NtscRs_Simple": NtscRsSimpleNode,
    "NtscRs_Intermediate": NtscRsIntermediateNode,
    # Category nodes
    "NtscRs_Signal": NtscRsSignalNode,
    "NtscRs_Scanlines": NtscRsScanlinesNode,
    "NtscRs_Artifacts": NtscRsArtifactsNode,
    "NtscRs_Noise": NtscRsNoiseNode,
    "NtscRs_VHS": NtscRsVHSNode,
    "NtscRs_Global": NtscRsGlobalNode,
    "NtscRs_Scale": NtscRsScaleNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Full nodes
    "NtscRs_Advanced": "NTSC-RS (Advanced)",
    "NtscRs_Simple": "NTSC-RS (Simple)",
    "NtscRs_Intermediate": "NTSC-RS (Intermediate)",
    # Category nodes
    "NtscRs_Signal": "NTSC Signal",
    "NtscRs_Scanlines": "NTSC Scanlines",
    "NtscRs_Artifacts": "NTSC Artifacts",
    "NtscRs_Noise": "NTSC Noise",
    "NtscRs_VHS": "NTSC VHS",
    "NtscRs_Global": "NTSC Global",
    "NtscRs_Scale": "NTSC Scale",
}

print("[NTSC-RS] Module initialization complete", flush=True)

__all__ = [
    # Nodes
    "NtscRsNode",
    "NtscRsSimpleNode",
    "NtscRsIntermediateNode",
    "NtscRsSignalNode",
    "NtscRsScanlinesNode",
    "NtscRsArtifactsNode",
    "NtscRsNoiseNode",
    "NtscRsVHSNode",
    "NtscRsGlobalNode",
    "NtscRsScaleNode",
    # Extension
    "NtscRsExtension",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
