READ X:\agents-matrix\AGENTS.md BEFORE ANYTHING (skip if missing).

# Agent guide: comfyui-ntsc-rs

ComfyUI custom node pack (10 nodes, V3 API) over a Rust extension (`rust_binding/`, PyO3, abi3 for Python 3.12+).

## Install into a ComfyUI

1. Find the ComfyUI root (the folder with `main.py` and `custom_nodes/`) and the Python that runs it: `venv/` or `.venv/` inside ComfyUI, `python_embeded/python.exe` for the Windows portable build, or the Desktop app's `.venv`. Call it `$PY`.
2. Check the version: `ComfyUI/comfyui_version.py` must be 0.3.48 or newer.
3. Clone into `custom_nodes`, keeping the folder name:
   ```bash
   git clone https://github.com/gvastethecreator/comfyui-ntsc-rs.git ComfyUI/custom_nodes/comfyui-ntsc-rs
   ```
4. Fetch the native binary now instead of at first start:
   ```bash
   cd ComfyUI/custom_nodes/comfyui-ntsc-rs && $PY install.py
   ```
   Success prints at most one `Downloading` line and leaves `native/comfyui_ntsc_rs-<version>-<platform>.(pyd|so)` in place. Do not pip-install anything; `numpy` and `torch` already come with ComfyUI.
5. If step 4 prints `[NTSC-RS] ... Build it once` (no release asset, no network, unsupported platform), build it. This needs Rust (`rustup`) and takes about a minute:
   ```bash
   $PY -m pip install "maturin>=1.16,<2"
   $PY build_node.py
   ```
6. Restart ComfyUI. Check: the log has no `[NTSC-RS]` warning, and `GET /object_info/NtscRs_Simple` returns the node. To run one node end to end, queue `example_workflows/NTSC-RS_Simple_VHS.json` (it reads `input/example.png`).

## Layout

- `__init__.py`: `comfy_entrypoint()` registers the nodes. On ComfyUI older than 0.3.48 it loads nothing and prints why.
- `native.py`: finds the binary (`native/` first, then a pip-installed `comfyui_ntsc_rs`, then a download from the GitHub release `v<pyproject version>`), and `apply_ntsc()` runs an IMAGE batch through it.
- `ntsc_node*.py`: one node per file. `ntsc_presets.py`: the 14 presets.
- `example_workflows/`: registry templates (`.json` plus a `.jpg` thumbnail with the same name).
- `docs/`: GitHub Pages site. `docs/codemap/`: code map (update it when module boundaries change).

## Checks

- `python scripts/verify.py`: ruff, cargo fmt/check/test/clippy.
- `python build_node.py --dev && python scripts/native_smoke.py`: build into `native/` and test the NumPy boundary.
- On Windows with a full X: drive, set `CARGO_TARGET_DIR` outside the repo.

## Rules

- Keep the version in `pyproject.toml` and `rust_binding/Cargo.toml` equal; the release tag is `v<version>`, and `native.py` downloads that tag's assets.
- Do not publish to the Comfy Registry or create releases unless asked. `publish.yml` is manual on purpose.
- Chainable nodes other than Signal keep the signal stage neutral (`composite_sharpening` 0, no luma or chroma lowpass). Re-enabling ntsc-rs defaults there compounds the colour shift on every chained pass.
