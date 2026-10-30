"""Find, fetch, and call the compiled comfyui_ntsc_rs extension.

Load order: a binary in ./native/ (bundled, downloaded, or copied there by build_node.py),
then a pip-installed comfyui_ntsc_rs, then a one-time download of this version's binary
from the GitHub release. Nothing here installs packages or changes the Python environment.
"""

from __future__ import annotations

import importlib.util
import platform
import sys
import tomllib
import urllib.request
from functools import cache
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]["version"]
REPOSITORY = "gvastethecreator/comfyui-ntsc-rs"
NATIVE_DIR = ROOT / "native"
BUILD_COMMAND = f'"{sys.executable}" "{ROOT / "build_node.py"}"'

# (sys.platform, machine) -> release asset platform key. The extension uses the stable
# ABI (abi3), so one binary per OS/architecture covers Python 3.12 and newer.
PLATFORMS = {
    ("win32", "amd64"): "win_amd64",
    ("linux", "x86_64"): "linux_x86_64",
    ("linux", "aarch64"): "linux_aarch64",
    ("darwin", "arm64"): "macos_arm64",
    ("darwin", "x86_64"): "macos_x86_64",
}

problem: str | None = None


def binary_name() -> str | None:
    """Return this platform's release asset name, or None when no prebuilt binary exists."""
    key = PLATFORMS.get((sys.platform, platform.machine().lower()))
    if key is None:
        return None
    suffix = ".pyd" if sys.platform == "win32" else ".so"
    return f"comfyui_ntsc_rs-{VERSION}-{key}{suffix}"


def _load_file(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("comfyui_ntsc_rs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules["comfyui_ntsc_rs"] = module
    return module


def download(name: str) -> Path:
    """Fetch one release binary into ./native/ and drop binaries from older versions."""
    url = f"https://github.com/{REPOSITORY}/releases/download/v{VERSION}/{name}"
    target = NATIVE_DIR / name
    partial = target.with_suffix(".part")
    NATIVE_DIR.mkdir(exist_ok=True)
    print(f"[NTSC-RS] Downloading {url}", flush=True)
    with urllib.request.urlopen(url, timeout=60) as response, partial.open("wb") as file:
        file.write(response.read())
    partial.replace(target)
    for stale in NATIVE_DIR.glob("comfyui_ntsc_rs-*"):
        if stale != target:
            stale.unlink(missing_ok=True)
    return target


@cache
def load_native(allow_download: bool = True) -> ModuleType | None:
    """Return the native module, or None and set `problem` to a user-facing message."""
    global problem
    name = binary_name()
    bundled = NATIVE_DIR / name if name else None
    try:
        if bundled and bundled.is_file():
            return _load_file(bundled)
        try:
            import comfyui_ntsc_rs

            return comfyui_ntsc_rs
        except ImportError:
            pass
        if bundled and allow_download:
            return _load_file(download(name))
        reason = (
            f"no prebuilt binary for {sys.platform}/{platform.machine()}"
            if name is None
            else "the native binary is missing"
        )
    except Exception as error:  # noqa: BLE001 - any failure here must not crash ComfyUI
        reason = f"loading the native binary failed ({error})"
    problem = (
        f"[NTSC-RS] {reason}. Build it once with Rust installed (https://rustup.rs/):\n"
        f"    {BUILD_COMMAND}\n"
        "then restart ComfyUI."
    )
    return None


def require_native() -> ModuleType:
    native = load_native()
    if native is None:
        raise RuntimeError(problem)
    return native


def apply_ntsc(image, params: dict):
    """Run every frame of a ComfyUI IMAGE batch (B, H, W, C floats in 0..1) through ntsc-rs."""
    import numpy as np  # Deferred so build_node.py can use this module without torch.
    import torch

    native = require_native()
    frames = (image.detach().cpu().clamp(0.0, 1.0) * 255.0).to(torch.uint8).numpy()
    results = np.stack([native.apply_ntsc_filter(frame, params) for frame in frames])
    return torch.from_numpy(results).float() / 255.0
