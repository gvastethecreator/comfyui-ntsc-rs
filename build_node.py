#!/usr/bin/env python3
"""Build the comfyui-ntsc-rs native extension without mutating ComfyUI."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUST_BINDING = ROOT / "rust_binding"
WHEEL_DIRECTORY = RUST_BINDING / "target" / "wheels"
MINIMUM_MATURIN = (1, 14, 1)
LOCAL_PYTHONS = (
    ROOT / ".venv" / "Scripts" / "python.exe",
    ROOT / "venv" / "Scripts" / "python.exe",
)


def run(command: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    """Run a command directly and keep its output visible."""
    return subprocess.run(command, cwd=cwd, text=True, check=False)


def resolve_python(explicit: str | None) -> str:
    """Resolve an explicit interpreter, a project venv, or this Python."""
    if explicit:
        candidate = Path(explicit).expanduser()
        resolved = str(candidate.resolve()) if candidate.exists() else shutil.which(explicit)
        if resolved:
            return resolved
        raise SystemExit(f"Python interpreter not found: {explicit}")

    for candidate in LOCAL_PYTHONS:
        if candidate.is_file():
            return str(candidate)

    return sys.executable


def resolve_maturin(python: str) -> str | None:
    """Find maturin beside the selected interpreter or on PATH."""
    scripts = Path(python).resolve().parent
    for name in ("maturin.exe", "maturin"):
        candidate = scripts / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("maturin")


def maturin_version(executable: str) -> tuple[int, ...] | None:
    """Read the selected maturin executable's version."""
    result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return None
    try:
        version = result.stdout.strip().removeprefix("maturin ")
        return tuple(int(part) for part in version.split(".")[:3])
    except ValueError:
        return None


def require_tooling(python: str) -> str:
    """Fail with an actionable command when required build tools are absent."""
    if shutil.which("cargo") is None:
        raise SystemExit("Rust/Cargo not found. Install it from https://rustup.rs/.")

    executable = resolve_maturin(python)
    installed = maturin_version(executable) if executable else None
    if installed is None or installed < MINIMUM_MATURIN:
        required = ".".join(map(str, MINIMUM_MATURIN))
        raise SystemExit(
            f"maturin>={required} is required for {python}. "
            f'Install it with: "{python}" -m pip install -r "{ROOT / "requirements.txt"}"'
        )
    return executable


def build(python: str, *, release: bool, install: bool) -> Path:
    """Build one wheel and optionally install that exact artifact."""
    maturin = require_tooling(python)
    WHEEL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    previous = {path.resolve() for path in WHEEL_DIRECTORY.glob("*.whl")}

    command = [
        maturin,
        "build",
        "--locked",
        "--interpreter",
        python,
        "--out",
        str(WHEEL_DIRECTORY),
    ]
    if release:
        command.append("--release")

    profile = "release" if release else "development"
    print(f"Building {profile} wheel with {python}", flush=True)
    result = run(command, cwd=RUST_BINDING)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    candidates = sorted(
        WHEEL_DIRECTORY.glob("*.whl"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    if not candidates:
        raise SystemExit(f"Build succeeded but no wheel was found in {WHEEL_DIRECTORY}.")

    wheel = candidates[0]
    if wheel.resolve() in previous:
        print(f"Updated wheel: {wheel}", flush=True)
    else:
        print(f"Created wheel: {wheel}", flush=True)

    if install:
        result = run([python, "-m", "pip", "install", "--force-reinstall", "--no-deps", str(wheel)])
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        print(f"Installed {wheel.name} into {python}", flush=True)

    return wheel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev", action="store_true", help="Build an unoptimized wheel.")
    parser.add_argument("--install", action="store_true", help="Install the wheel after building.")
    parser.add_argument("--python", help="Target Python executable or command.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run Cargo check instead of building a wheel.",
    )
    args = parser.parse_args()

    python = resolve_python(args.python)

    if args.check:
        require_tooling(python)
        return run(["cargo", "check", "--locked"], cwd=RUST_BINDING).returncode

    build(python, release=not args.dev, install=args.install)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
