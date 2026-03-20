"""ComfyUI NTSC-RS Extension.

A ComfyUI custom node extension that provides VHS/CRT/NTSC effects
using the ntsc-rs Rust library for native tensor processing.
"""

from typing import List, Type
from typing_extensions import override

try:
    from comfy_api.latest import ComfyExtension, io
except ImportError:
    from comfy import ComfyExtension, io

from ntsc_node import NtscRsNode
from ntsc_node_simple import NtscRsSimpleNode


class NtscRsExtension(ComfyExtension):
    """NTSC-RS ComfyUI Extension.

    Provides VHS/CRT/NTSC video effect processing with two node types:
    - NtscRs_Advanced: Full parameter control (60+ settings)
    - NtscRs_Simple: Preset-based quick access
    """

    @override
    async def get_node_list(self) -> List[Type[io.ComfyNode]]:
        """Return list of node classes provided by this extension."""
        return [NtscRsNode, NtscRsSimpleNode]

    @override
    async def on_load(self):
        """Called when the extension is loaded."""
        pass


async def comfy_entrypoint() -> NtscRsExtension:
    """Entry point for ComfyUI to load this extension."""
    return NtscRsExtension()


WEB_DIRECTORY = "./js"

NODE_CLASS_MAPPINGS = {
    "NtscRs_Advanced": NtscRsNode,
    "NtscRs_Simple": NtscRsSimpleNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NtscRs_Advanced": "NTSC-RS (Advanced)",
    "NtscRs_Simple": "NTSC-RS (Simple)",
}

__all__ = [
    "NtscRsNode",
    "NtscRsSimpleNode",
    "NtscRsExtension",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]