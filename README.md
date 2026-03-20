# ComfyUI NTSC-RS

A native ComfyUI custom node providing VHS/CRT/NTSC video effect processing using the [ntsc-rs](https://github.com/ntsc-rs/ntsc-rs) Rust library.

## Features

- **Native Rust binding** - High-performance tensor processing via PyO3
- **Two node types**:
  - **NTSC-RS (Simple)**: Quick access to VHS/CRT looks via presets
  - **NTSC-RS (Advanced)**: Complete 1:1 access to all 60+ ntsc-rs parameters
- **6 Presets included**: VHS Classic, VHS Worn, CRT TV, Clean NTSC, Game Console, Cassette Recorder
- **Full batch support** - Processes multiple images efficiently
- **1:1 Quality** - Uses ntsc-rs directly via `apply_effect_to_yiq()`

## Requirements

- Python 3.10+
- ComfyUI
- Windows, Linux, or macOS

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
2. The nodes will appear under category: `image/effects/ntsc`

## Nodes

### NTSC-RS (Simple)

Quick access to VHS/CRT effects using presets.

**Inputs:**
| Input | Type | Description |
|-------|------|-------------|
| image | Image | Image to process |
| preset | Combo | Preset name (see below) |
| intensity | Float | Effect intensity (0.0-1.0) |
| saturation | Float | Color saturation (-1.0 to 2.0) |
| random_seed | Int | Random seed for noise |

### NTSC-RS (Advanced)

Full parameter control with 60+ settings organized into categories:

- **Signal Processing**: filter_type, luma/chroma filters, smear, sharpening
- **Field/Line Processing**: field mode, scanline phase
- **Head Switching**: VHS head switching artifact emulation
- **Tracking Noise**: VHS tracking noise settings
- **Composite/Luma/Chroma Noise**: Separate noise layers
- **Ringing Artifacts**: Ringing effect control
- **VHS Settings**: Tape speed, chroma loss, sharpen, edge wave
- **Global Effects**: Snow, chroma phase noise/error, delays
- **Scale Settings**: Horizontal/vertical effect scaling

## Presets

| Preset | Description |
|--------|-------------|
| VHS Classic | Standard VHS SP recording quality |
| VHS Worn | Well-used tape with tracking issues |
| CRT TV | Old television with CRT display |
| Clean NTSC | Minimal NTSC processing |
| Game Console | Retro console (NES/SNES era) |
| Cassette Recorder | Audio cassette tape emulation |

## Tensor Processing Pipeline

```
PyTorch [B,H,W,C] float32 → 
numpy [H,W,C] uint8 → 
Rust: YiqView + apply_effect_to_yiq() →
numpy [H,W,C] uint8 → 
PyTorch [B,H,W,C] float32
```

## Project Structure

```
comfyui-ntscrs/
├── __init__.py              # ComfyUI extension entry point
├── ntsc_node.py             # Advanced node (60+ parameters)
├── ntsc_node_simple.py      # Simple preset-based node
├── ntsc_presets.py          # Preset definitions
├── build_node.py            # Rust binding build script
├── wheels/                  # Pre-built wheels
│   └── comfyui_ntsc_rs-*.whl
├── rust_binding/            # PyO3 Rust project (for building)
│   ├── Cargo.toml
│   ├── pyproject.toml
│   └── src/lib.rs
└── vendor/                  # Vendored ntsc-rs (for building)
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

## Building Wheels for Other Platforms

To build a wheel for a different platform (e.g., Linux from Windows):

```bash
# Install cross-compilation toolchain
rustup target add x86_64-unknown-linux-gnu

# Build
python build_node.py --target x86_64-unknown-linux-gnu
```

## License

MIT / ISC / Apache-2.0 (same as ntsc-rs)

ntsc-rs is licensed under MIT OR ISC OR Apache-2.0.

## References

- [ntsc-rs](https://github.com/ntsc-rs/ntsc-rs) - Original Rust library
- [PyO3](https://pyo3.rs/) - Python/Rust bindings
- [ComfyUI Custom Nodes](https://docs.comfy.org/development/core-concepts/custom-nodes) - ComfyUI development docs
