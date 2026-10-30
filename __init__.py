"""ComfyUI NTSC-RS extension: V3 entry point (ComfyUI 0.3.48+)."""

try:
    from comfy_api.latest import ComfyExtension
except ImportError as error:  # ComfyUI older than 0.3.48 has no V3 node API.
    ComfyExtension = None
    print(f"[NTSC-RS] Needs ComfyUI 0.3.48 or newer ({error}); no nodes were loaded.", flush=True)
    NODE_CLASS_MAPPINGS = {}  # Lets the old loader skip this pack without an error.

if ComfyExtension is not None:
    from . import native
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

    # Resolve (or fetch) the native binary now so a missing one is reported once at
    # startup. The nodes register either way; running one then raises the same message.
    if native.load_native() is None:
        print(native.problem, flush=True)

    class NtscRsExtension(ComfyExtension):
        """Register the full and chainable NTSC-RS nodes with ComfyUI."""

        async def get_node_list(self):
            return list(NODE_CLASSES)

    async def comfy_entrypoint() -> NtscRsExtension:
        """Return the extension instance for the current ComfyUI API."""
        return NtscRsExtension()
