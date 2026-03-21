"""ComfyUI NTSC-RS Extension.

A ComfyUI custom node extension that provides VHS/CRT/NTSC video effects
using the ntsc-rs Rust library for native tensor processing.

================================================================================
NTSC-RS: Native VHS/CRT/NTSC Signal Processing for ComfyUI
================================================================================

Provides high-quality VHS and CRT video effect emulation with the following
node types:

FULL NODES (all effects in one node):
  - NTSC-RS Simple    : Preset-based with intensity control
  - NTSC-RS Intermediate : Presets with scaling controls
  - NTSC-RS Advanced  : Full parameter control

CATEGORY NODES (chainable, single category each):
  - NTSC-RS Signal    : Filter types, luma/chroma processing
  - NTSC-RS Scanlines : Field mode, scanline phase
  - NTSC-RS Artifacts : Head switching, tracking noise
  - NTSC-RS Noise     : Composite, luma, chroma noise, ringing
  - NTSC-RS VHS       : Tape speed, chroma loss, sharpen, edge wave
  - NTSC-RS Global    : Snow, chroma phase, delays
  - NTSC-RS Scale     : Resolution scaling

================================================================================
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     NTSC-RS Extension for ComfyUI                           ║
║          Native VHS/CRT/NTSC Signal Processing (Rust + PyO3)               ║
╚══════════════════════════════════════════════════════════════════════════════╝
""", flush=True)

print("[NTSC-RS] Initializing extension...", flush=True)

try:
    from comfy_api.latest import ComfyExtension, io
    print("[NTSC-RS] ✓ Using comfy_api.latest", flush=True)
except ImportError as e:
    print(f"[NTSC-RS] ✗ comfy_api.latest import failed: {e}", flush=True)
    raise

print("[NTSC-RS] Loading node modules...", flush=True)
print("─" * 76, flush=True)

# Main nodes
try:
    from .ntsc_node import NtscRsNode
    print(f"[NTSC-RS]   ✓ NtscRsNode (Advanced)     : {NtscRsNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_simple import NtscRsSimpleNode
    print(f"[NTSC-RS]   ✓ NtscRsSimpleNode (Simple) : {NtscRsSimpleNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsSimpleNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_intermediate import NtscRsIntermediateNode
    print(f"[NTSC-RS]   ✓ NtscRsIntermediateNode     : {NtscRsIntermediateNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsIntermediateNode: {e}", flush=True)
    raise

print("─" * 76, flush=True)
print("[NTSC-RS] Loading category (chainable) nodes...", flush=True)
print("─" * 76, flush=True)

# Category nodes
try:
    from .ntsc_node_signal import NtscRsSignalNode
    print(f"[NTSC-RS]   ✓ NtscRsSignalNode          : {NtscRsSignalNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsSignalNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_scanlines import NtscRsScanlinesNode
    print(f"[NTSC-RS]   ✓ NtscRsScanlinesNode       : {NtscRsScanlinesNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsScanlinesNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_artifacts import NtscRsArtifactsNode
    print(f"[NTSC-RS]   ✓ NtscRsArtifactsNode       : {NtscRsArtifactsNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsArtifactsNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_noise import NtscRsNoiseNode
    print(f"[NTSC-RS]   ✓ NtscRsNoiseNode           : {NtscRsNoiseNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsNoiseNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_vhs import NtscRsVHSNode
    print(f"[NTSC-RS]   ✓ NtscRsVHSNode             : {NtscRsVHSNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsVHSNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_global import NtscRsGlobalNode
    print(f"[NTSC-RS]   ✓ NtscRsGlobalNode          : {NtscRsGlobalNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsGlobalNode: {e}", flush=True)
    raise

try:
    from .ntsc_node_scale import NtscRsScaleNode
    print(f"[NTSC-RS]   ✓ NtscRsScaleNode           : {NtscRsScaleNode}", flush=True)
except Exception as e:
    print(f"[NTSC-RS]   ✗ Failed to import NtscRsScaleNode: {e}", flush=True)
    raise


class NtscRsExtension(ComfyExtension):
    """NTSC-RS ComfyUI Extension.

    Provides VHS/CRT/NTSC video effect processing with multiple node types.

    Full Nodes (all effects combined):
        - Simple   : Preset-based with intensity/saturation control
        - Intermediate : Presets with scaling controls
        - Advanced  : Full parameter access

    Category Nodes (chainable, single category each):
        - Signal    : Filter types, luma/chroma filters, smear, sharpening
        - Scanlines : Field mode, scanline phase shift
        - Artifacts : Head switching, tracking noise
        - Noise     : Composite, luma, chroma noise, ringing
        - VHS       : Tape speed, chroma loss, sharpen, edge wave
        - Global    : Snow speckles, chroma phase noise/error, delays
        - Scale     : Horizontal/vertical resolution scaling
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
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  NTSC-RS Extension loaded successfully!                                      ║
║                                                                              ║
║  Nodes available: 3 Full + 7 Category = 10 total                            ║
║  Library: ntsc-rs (Rust) via PyO3                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
""", flush=True)


async def comfy_entrypoint() -> NtscRsExtension:
    """Entry point for ComfyUI to load this extension."""
    print("[NTSC-RS] comfy_entrypoint called, returning NtscRsExtension", flush=True)
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
    "NtscRs_Advanced": "NTSC-RS Advanced",
    "NtscRs_Simple": "NTSC-RS Simple",
    "NtscRs_Intermediate": "NTSC-RS Intermediate",
    # Category nodes
    "NtscRs_Signal": "NTSC-RS Signal",
    "NtscRs_Scanlines": "NTSC-RS Scanlines",
    "NtscRs_Artifacts": "NTSC-RS Artifacts",
    "NtscRs_Noise": "NTSC-RS Noise",
    "NtscRs_VHS": "NTSC-RS VHS",
    "NtscRs_Global": "NTSC-RS Global",
    "NtscRs_Scale": "NTSC-RS Scale",
}

print("─" * 76, flush=True)
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
