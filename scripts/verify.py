"""Run the project quality gates without changing the environment."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUST = ROOT / "rust_binding"


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print(f"> {' '.join(command)}", flush=True)
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)


def require(command: str, install: str) -> None:
    if shutil.which(command) is None:
        raise SystemExit(f"{command} was not found. {install}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="Apply Python and Rust formatting.")
    args = parser.parse_args()

    require("cargo", "Install Rust from https://rustup.rs/.")

    if args.fix:
        run([sys.executable, "-m", "ruff", "check", ".", "--fix"])
        run([sys.executable, "-m", "ruff", "format", "."])
        run(["cargo", "fmt", "--all"], cwd=RUST)
        return 0

    run([sys.executable, "-m", "ruff", "check", "."])
    run([sys.executable, "-m", "ruff", "format", "--check", "."])
    run(
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "-x",
            r"[\\/](?:\.venv|target|\.git)[\\/]",
            ".",
        ]
    )
    run(["cargo", "fmt", "--all", "--", "--check"], cwd=RUST)
    run(["cargo", "check", "--locked", "--all-features"], cwd=RUST)
    run(["cargo", "test", "--locked", "--all-features"], cwd=RUST)
    run(
        ["cargo", "clippy", "--locked", "--all-targets", "--all-features", "--", "-D", "warnings"],
        cwd=RUST,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
