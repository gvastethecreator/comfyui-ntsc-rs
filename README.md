# ComfyUI NTSC-RS

<!-- IMAGE PLACEHOLDER - Add your preview images here -->
<!-- 
![NTSC-RS Preview](assets/preview.gif)
![NTSC-RS Nodes](assets/nodes.png)
-->
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/comfyui-ntscrs?style=social)](https://github.com/YOUR_USERNAME/comfyui-ntscrs)
[![License](https://img.shields.io/badge/license-MIT%2FISC%2FApache--2.0-blue)](LICENSE)
[![Rust](https://img.shields.io/badge/rust-1.85%2B-orange)](https://rustup.rs/)

================================================================================
Native VHS/CRT/NTSC Video Effect Processing for ComfyUI
================================================================================

A ComfyUI custom node extension providing high-quality VHS and CRT video effect
emulation using the [ntsc-rs](https://github.com/ntsc-rs/ntsc-rs) Rust library via
native PyO3 bindings.

## Features

- **Native Rust Binding** - High-performance tensor processing via PyO3 (no subprocess)
- **10 Node Types** - 3 Full nodes + 7 Chainable category nodes
- **60+ Parameters** - Complete access to ntsc-rs signal processing
- **14 VHS/CRT Presets** - Quick access to classic looks
- **Chainable Nodes** - Combine category-specific nodes for custom pipelines
- **1:1 Quality** - Direct access to ntsc-rs `apply_effect_to_yiq()`

## Quick Preview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  BEFORE                        AFTER (VHS Classic)                        │
│  ┌─────────┐                  ┌─────────┐                                 │
│  │         │    ───────►      │ ░░░░░░░ │                                 │
│  │  Clean  │                  │ ░ VHS ░ │                                 │
│  │  Image  │                  │ ░░░░░░░ │                                 │
│  └─────────┘                  └─────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Nodes Overview

### Full Nodes (All Effects Combined)

| Node | Description |
|------|-------------|
| **NTSC-RS Simple** | Preset-based with intensity/saturation control |
| **NTSC-RS Intermediate** | Presets with scaling controls |
| **NTSC-RS Advanced** | Full parameter access (60+ settings) |

### Category Nodes (Chainable)

Each node applies ONLY its category of effects, allowing flexible pipelines:

| Node | Effects Applied |
|------|----------------|
| **NTSC-RS Signal** | Filter types, luma/chroma filters, smear, sharpening |
| **NTSC-RS Scanlines** | Field mode, scanline phase shift |
| **NTSC-RS Artifacts** | Head switching, tracking noise |
| **NTSC-RS Noise** | Composite, luma, chroma noise, ringing |
| **NTSC-RS VHS** | Tape speed, chroma loss, sharpen, edge wave |
| **NTSC-RS Global** | Snow speckles, chroma phase, delays |
| **NTSC-RS Scale** | Resolution scaling (H/V) |

## Installation

### Option 1: Pre-built Wheel (Recommended)

```bash
# Navigate to your ComfyUI custom_nodes directory
cd path/to/ComfyUI/custom_nodes

# Clone this repository
git clone https://github.com/YOUR_USERNAME/comfyui-ntscrs.git
cd comfyui-ntscrs

# Install the pre-built wheel for your Python environment
pip install wheels/comfyui_ntsc_rs-0.1.0-cp312-cp312-win_amd64.whl
```

**Note**: Replace `cp312` with your Python version if different (e.g., `cp311` for Python 3.11).

### Option 2: Build from Source

If you need to rebuild the native extension:

```bash
# Install build dependencies
pip install maturin

# Clone and build
git clone https://github.com/YOUR_USERNAME/comfyui-ntscrs.git
cd comfyui-ntscrs
python build_node.py
```

Requirements for building:
- Rust toolchain (1.85+ for Rust 2024 edition support)
- Maturin (`pip install maturin`)

### Post-Installation

1. Restart ComfyUI
2. The nodes will appear under category: `NTSC`

## Usage

### Quick Start with Presets

Use `NTSC-RS Simple` for quick VHS/CRT looks:

```
Image → [NTSC-RS Simple] → Output
         preset: VHS Classic
         intensity: 1.0
```

### Chainable Category Nodes

Combine multiple category nodes for custom processing:

```
Image → [NTSC-RS Signal] → [NTSC-RS Scanlines] → [NTSC-RS VHS] → Output
              ↓                   ↓                    ↓
         filter: Butterworth   field: InterleavedUpper   tape: SP
         luma: Notch          phase: 180°              chroma_loss: 0.000025
```

### Full Control

Use `NTSC-RS Advanced` for complete parameter access:

```
Image → [NTSC-RS Advanced] → Output
         filter_type: Butterworth
         head_switching_enabled: True
         vhs_tape_speed: SP
         ... (60+ parameters)
```

## Presets

### VHS Presets

| Preset | Description |
|--------|-------------|
| VHS Classic | Standard VHS SP recording quality |
| VHS Worn | Well-used tape with tracking issues |
| VHS Professional | High-quality S-VHS recording |
| VHS Economy | Low-quality EP recording |
| VHS Baby | Degraded, old tape |

### CRT Presets

| Preset | Description |
|--------|-------------|
| CRT TV | Old television with CRT display |
| CRT Arcade | Arcade monitor with sharp pixels |
| PVM Style | Professional video monitor |

### Other Presets

| Preset | Description |
|--------|-------------|
| Clean NTSC | Minimal processing, clean output |
| Game Console | Retro console (NES/SNES era) |
| Camcorder | Handheld camera recording |
| Security Cam | Low-quality surveillance |
| Test Pattern | Technical test signal |
| Cassette Recorder | Audio cassette tape emulation |

## Changelog

### [0.1.0] - 2026-03-21

#### Added
- 10 node types: 3 Full + 7 Chainable category nodes
- 14 VHS/CRT presets
- Native PyO3 Rust binding (no subprocess)
- `ntsc-rs` library via vendored copy
- ASCII-formatted startup logs
- VS Code tasks.json for build/deploy

#### Fixed
- Scale node now performs actual image resizing via PyTorch (was using ntsc-rs internal scale params which don't change dimensions)
- Intermediate node now performs actual image resizing
- All category nodes properly disable non-relevant effects for optimized processing

#### Changed
- README updated with better documentation and image placeholders
- All nodes now use `display_name` for readable labels in ComfyUI UI

## Tensor Processing Pipeline

```
PyTorch [B,H,W,C] float32
    ↓
numpy [H,W,C] uint8 (RGB)
    ↓
Rust: YIQ colorspace conversion
    ↓
ntsc-rs: apply_effect_to_yiq()
    ↓
Rust: YIQ to RGB conversion
    ↓
numpy [H,W,C] uint8
    ↓
PyTorch [B,H,W,C] float32
```

## Development

### VS Code Tasks

Press `Ctrl+Shift+P` and type "Run Task" to access:

| Task | Description |
|------|-------------|
| Build Rust Extension | Builds the PyO3 Rust extension |
| Copy to ComfyUI | Copies all files to ComfyUI custom_nodes |
| Build & Copy All | Builds and copies in one step |
| Copy Python Files Only | Quick Python-only sync |
| Clear ComfyUI Cache | Removes __pycache__ folders |
| Full Deploy Cycle | Build + Copy + Clear cache |

### Project Structure

```
comfyui-ntscrs/
├── __init__.py                 # ComfyUI extension entry point
├── ntsc_node.py               # Advanced node (60+ parameters)
├── ntsc_node_simple.py         # Simple preset-based node
├── ntsc_node_intermediate.py    # Intermediate with scaling
├── ntsc_presets.py            # 14 preset definitions
│
├── ntsc_node_signal.py         # Category: Signal processing
├── ntsc_node_scanlines.py      # Category: Scanlines/fields
├── ntsc_node_artifacts.py      # Category: Head switching
├── ntsc_node_noise.py          # Category: Noise layers
├── ntsc_node_vhs.py            # Category: VHS effects
├── ntsc_node_global.py          # Category: Global effects
├── ntsc_node_scale.py          # Category: Scaling
│
├── build_node.py               # Rust binding build script
├── wheels/                     # Pre-built wheels
│   └── comfyui_ntsc_rs-*.whl
├── rust_binding/              # PyO3 Rust project
│   ├── Cargo.toml
│   ├── pyproject.toml
│   └── src/lib.rs
├── .vscode/
│   ├── settings.json
│   └── tasks.json
└── vendor/                    # Vendored ntsc-rs
    ├── ntscrs/
    └── macros/
```

## Troubleshooting

### "Module not found: comfyui_ntsc_rs"

Install the wheel:
```bash
pip install wheels/comfyui_ntsc_rs-0.1.0-cp312-cp312-win_amd64.whl
```

### Build fails with Rust errors

Make sure you have Rust 1.85+:
```bash
rustc --version
cargo --version
```

If not, install from https://rustup.rs/

### Nodes not appearing in UI

1. Check ComfyUI console for `[NTSC-RS]` log messages
2. Ensure the extension loaded without errors
3. Try clearing `__pycache__` in the custom_nodes folder
4. Restart ComfyUI completely

### Scale/Resize not working

The Scale node uses PyTorch interpolation for actual resizing. The ntsc-rs
internal `horizontal_scale` and `vertical_scale` parameters only affect signal
processing (filter bandwidth), not image dimensions.

## Building Wheels for Other Platforms

To build a wheel for a different platform (e.g., Linux from Windows):

```bash
# Install cross-compilation toolchain
rustup target add x86_64-unknown-linux-gnu

# Build
python build_node.py --target x86_64-unknown-linux-gnu
```

## Technical Notes

### Category Nodes Optimization

Category nodes are designed for **minimal processing**. Each node:
- Applies ONLY its category of effects
- Disables all other effect categories
- Sets unaffected parameters to safe defaults

This allows chaining without unnecessary computation.

### ntsc-rs Parameters

The underlying ntsc-rs library provides:

| Category | Parameters |
|----------|------------|
| Signal Processing | 7 (filter types, smear, sharpening) |
| Field Processing | 3 (field mode, phase) |
| VHS Artifacts | 13 (head switching, tracking) |
| Noise Layers | 15 (composite, luma, chroma, ringing) |
| VHS Effects | 9 (tape speed, chroma loss, sharpen, edge wave) |
| Global Effects | 6 (snow, chroma phase, delays) |
| Scaling | 4 (horizontal, vertical, video-size) |

**Total: 60+ parameters**

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT / ISC / Apache-2.0 (same as ntsc-rs)

ntsc-rs is licensed under MIT OR ISC OR Apache-2.0.

## References

- [ntsc-rs](https://github.com/ntsc-rs/ntsc-rs) - Original Rust library
- [PyO3](https://pyo3.rs/) - Python/Rust bindings
- [ComfyUI Custom Nodes](https://docs.comfy.org/development/core-concepts/custom-nodes) - ComfyUI development docs
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) - For easy installation
