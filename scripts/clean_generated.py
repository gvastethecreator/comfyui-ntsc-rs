"""Remove only generated files owned by this repository."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = (
    ROOT / ".mypy_cache",
    ROOT / ".pytest_cache",
    ROOT / ".ruff_cache",
    ROOT / "htmlcov",
    ROOT / "rust_binding" / "target",
)
FILES = (ROOT / ".coverage",)


def main() -> int:
    removed = 0
    for directory in DIRECTORIES:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"Removed {directory.relative_to(ROOT)}")
            removed += 1

    for cache in ROOT.rglob("__pycache__"):
        if ".scratch" not in cache.parts:
            shutil.rmtree(cache)
            print(f"Removed {cache.relative_to(ROOT)}")
            removed += 1

    for file in FILES:
        if file.exists():
            file.unlink()
            print(f"Removed {file.relative_to(ROOT)}")
            removed += 1

    print(f"Cleaned {removed} generated path(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
