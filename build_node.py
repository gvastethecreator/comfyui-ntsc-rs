#!/usr/bin/env python3
"""Build script for the comfyui-ntsc-rs Rust binding."""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def safe_print(text):
    """Print text safely handling encoding issues."""
    if text is None:
        return
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        try:
            sys.stdout.buffer.write(text.encode('utf-8', errors='replace'))
            sys.stdout.buffer.write(b'\n')
        except Exception:
            print(str(text, errors='replace'))

SCRIPT_DIR = Path(__file__).parent.resolve()
RUST_BINDING_DIR = SCRIPT_DIR / "rust_binding"

COMFYUI_POSSIBLE_LOCATIONS = [
    SCRIPT_DIR / "venv" / "Scripts" / "python.exe",
    SCRIPT_DIR.parent / "venv" / "Scripts" / "python.exe",
    SCRIPT_DIR.parent.parent / "venv" / "Scripts" / "python.exe",
    Path("A:/ComfyUI/venv/Scripts/python.exe"),
    Path("A:/StabilityMatrix/Data/Packages/ComfyUI/venv/Scripts/python.exe"),
    Path("C:/ComfyUI/venv/Scripts/python.exe"),
]


def check_rust():
    """Check if Rust/Cargo is installed."""
    if shutil.which("cargo") is None:
        print("Error: Rust/Cargo not found. Install from https://rustup.rs/")
        return False
    return True


def get_torch_info(python: str) -> dict:
    """Get PyTorch and CUDA info from the target Python."""
    try:
        result = subprocess.run(
            [python, "-c", "import torch; print(torch.__version__); print(torch.version.cuda if torch.cuda.is_available() else 'CPU')"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return {
                "torch_version": lines[0] if len(lines) > 0 else "unknown",
                "cuda_version": lines[1] if len(lines) > 1 else "CPU"
            }
    except Exception:
        pass
    return {"torch_version": "unknown", "cuda_version": "CPU"}


def get_build_python():
    """Find the Python interpreter from ComfyUI venv."""
    for comfyui_python in COMFYUI_POSSIBLE_LOCATIONS:
        if comfyui_python.exists():
            print(f"Found ComfyUI Python: {comfyui_python}")
            torch_info = get_torch_info(str(comfyui_python))
            print(f"  PyTorch: {torch_info['torch_version']}")
            print(f"  CUDA: {torch_info['cuda_version']}")
            return str(comfyui_python)

    for python in [sys.executable, "python", "python3", "py"]:
        try:
            result = subprocess.run(
                [python, "-c", "import torch; print(torch.__version__)"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                print(f"Using system Python: {python} ({result.stdout.strip()})")
                return python
        except Exception:
            pass

    print("Error: Could not find ComfyUI Python")
    return None


def build():
    """Build the Rust binding using maturin."""
    if not check_rust():
        sys.exit(1)

    python = get_build_python()
    if python is None:
        sys.exit(1)

    print(f"Installing maturin and setuptools-rust in target environment...")
    result = subprocess.run(
        [python, "-m", "pip", "install", "maturin", "setuptools-rust"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        print(f"Failed to install dependencies:")
        safe_print(result.stderr)
        sys.exit(1)

    print(f"Building comfyui_ntsc_rs wheel...")
    result = subprocess.run(
        [python, "-m", "maturin", "build", "--release", "--interpreter", python],
        cwd=RUST_BINDING_DIR,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode != 0:
        print(f"Build failed:")
        safe_print(result.stderr)
        sys.exit(1)

    wheel_path = RUST_BINDING_DIR / "target" / "release" / "wheels"
    if wheel_path.exists():
        for whl in wheel_path.glob("*.whl"):
            print(f"Installing wheel: {whl.name}")
            install_result = subprocess.run(
                [python, "-m", "pip", "install", "--force-reinstall", str(whl)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if install_result.returncode == 0:
                print("Wheel installed successfully!")
            else:
                print(f"Failed to install wheel:")
                print(install_result.stderr)
                sys.exit(1)

    print("Build successful!")
    return True


def develop():
    """Build in development mode for faster iteration."""
    if not check_rust():
        sys.exit(1)

    python = get_build_python()
    if python is None:
        sys.exit(1)

    print(f"Installing maturin and setuptools-rust...")
    result = subprocess.run(
        [python, "-m", "pip", "install", "maturin", "setuptools-rust"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        print(f"Failed to install dependencies:")
        safe_print(result.stderr)
        sys.exit(1)

    print(f"Building comfyui_ntsc_rs wheel (dev mode)...")
    result = subprocess.run(
        [python, "-m", "maturin", "build", "--interpreter", python],
        cwd=RUST_BINDING_DIR,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode != 0:
        print(f"Build failed:")
        safe_print(result.stderr)
        sys.exit(1)

    wheel_path = RUST_BINDING_DIR / "target" / "release" / "wheels"
    if wheel_path.exists():
        for whl in wheel_path.glob("*.whl"):
            print(f"Installing wheel: {whl.name}")
            install_result = subprocess.run(
                [python, "-m", "pip", "install", "--force-reinstall", str(whl)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if install_result.returncode == 0:
                print("Wheel installed successfully!")
            else:
                print(f"Failed to install wheel:")
                print(install_result.stderr)
                sys.exit(1)

    print("Build successful!")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build comfyui-ntsc-rs Rust binding")
    parser.add_argument("--dev", action="store_true", help="Build in development mode")
    args = parser.parse_args()

    if args.dev:
        develop()
    else:
        build()