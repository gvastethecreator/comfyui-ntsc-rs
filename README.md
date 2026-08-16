<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/header/document.svg?title=ComfyUI+NTSC-RS&subtitle=Native+VHS%2C+CRT%2C+and+analog+signal+effects&logo=rust&theme=red&align=center&mode=dark" />
    <img alt="ComfyUI NTSC-RS — native VHS, CRT, and analog signal effects" src="https://shieldcn.dev/header/document.svg?title=ComfyUI+NTSC-RS&subtitle=Native+VHS%2C+CRT%2C+and+analog+signal+effects&logo=rust&theme=red&align=center&mode=light" />
  </picture>
</p>

<p align="center">
  <a href="https://github.com/gvastethecreator/comfyui-ntsc-rs/actions/workflows/ci.yml"><img alt="CI status" src="https://shieldcn.dev/github/ci/gvastethecreator/comfyui-ntsc-rs.svg?workflow=ci&branch=main&variant=secondary&size=xs" /></a>
  <a href="https://gvastethecreator.github.io/comfyui-ntsc-rs/"><img alt="Project site" src="https://shieldcn.dev/badge/site-pages-243f8f.svg?logo=githubpages&variant=branded&size=xs" /></a>
  <a href="https://www.python.org/"><img alt="Python 3.12 or newer" src="https://shieldcn.dev/badge/Python-3.12%2B-3776AB.svg?logo=python&variant=branded&size=xs" /></a>
  <a href="https://rustup.rs/"><img alt="Rust 1.89 or newer" src="https://shieldcn.dev/badge/Rust-1.89%2B-000000.svg?logo=rust&variant=branded&size=xs" /></a>
  <a href="LICENSE"><img alt="MIT, ISC, or Apache 2.0 license" src="https://shieldcn.dev/github/license/gvastethecreator/comfyui-ntsc-rs.svg?variant=secondary&size=xs" /></a>
</p>

Native VHS, CRT, and NTSC effects for ComfyUI. Ten nodes combine a Python UI layer with the vendored `ntsc-rs` signal processor compiled through Rust, PyO3, and Maturin.

[Project site](https://gvastethecreator.github.io/comfyui-ntsc-rs/) · [Source and issues](https://github.com/gvastethecreator/comfyui-ntsc-rs)

- Process ComfyUI image tensors through the native YIQ signal pipeline.
- Start quickly with 14 presets or expose more than 60 parameters.
- Chain isolated signal, scanline, artifact, noise, VHS, global, and scale nodes.
- Keep processing local: no account, telemetry, upload, or hosted inference.

## Output gallery

The source fixture was created with OpenAI Imagegen. Every processed frame below was rendered by the compiled extension and repository presets; these are not simulated overlays.

| Clean source | VHS Classic |
| --- | --- |
| <img src="docs/assets/gallery/source.webp" alt="Matte television, blue sphere, and red paper ribbon before processing" /> | <img src="docs/assets/gallery/vhs-classic.webp" alt="The same still life after the VHS Classic preset" /> |
| **CRT TV** | **Security Cam** |
| <img src="docs/assets/gallery/crt-tv.webp" alt="CRT TV output with softened horizontal detail and field texture" /> | <img src="docs/assets/gallery/security-cam.webp" alt="Security Camera output with noise and reduced clarity" /> |

See [gallery provenance](docs/assets/gallery/README.md) for the exact rendering boundary.

## Requirements

- ComfyUI with `comfy_api.latest`
- Python 3.12 or newer
- Rust 1.89 or newer
- Windows, Linux, or macOS toolchain able to build a native Python extension

This repository has no JavaScript package graph, so Bun and pnpm do not apply.

## Install

Clone the repository inside `ComfyUI/custom_nodes`, activate the same Python environment used by ComfyUI, then build and install the native wheel:

```powershell
git clone https://github.com/gvastethecreator/comfyui-ntsc-rs.git
cd comfyui-ntsc-rs
python -m pip install -r requirements.txt
python build_node.py --install
```

Restart ComfyUI. A successful load prints one concise `[NTSC-RS] Loaded 10 nodes` message.

`build_node.py` never installs tools, copies files, or changes a ComfyUI directory unless `--install` is explicitly passed. Use `--python PATH` when the target ComfyUI interpreter is not active:

```powershell
python build_node.py --python C:\path\to\ComfyUI\venv\Scripts\python.exe --install
```

## Nodes

| Node | Use |
| --- | --- |
| NTSC-RS Simple | Pick one of 14 presets and adjust intensity or saturation. |
| NTSC-RS Intermediate | Combine presets, scaling, field mode, and seed controls. |
| NTSC-RS Advanced | Control the complete signal-processing surface. |
| NTSC-RS Signal | Tune luma, chroma, smear, and sharpening. |
| NTSC-RS Scanlines | Set field mode, phase, and phase offset. |
| NTSC-RS Artifacts | Add head switching and tracking artifacts. |
| NTSC-RS Noise | Add composite, luma, chroma, and ringing noise. |
| NTSC-RS VHS | Control tape speed, chroma loss, sharpening, and edge wave. |
| NTSC-RS Global | Add snow, phase variation, and chroma delay. |
| NTSC-RS Scale | Apply horizontal and vertical signal scaling. |

Start with **Simple**. Use the chainable nodes when a workflow needs one isolated effect family. Use **Advanced** only when every parameter must be exposed.

## Development

Create and activate a local virtual environment before installing development tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts\verify.py
```

Common commands:

```powershell
python scripts\verify.py --fix     # format Python and Rust
python build_node.py --check       # validate the Rust binding
python build_node.py --dev         # build a fast development wheel
python build_node.py               # build an optimized wheel
python scripts\clean_generated.py  # remove local build and cache output
```

After installing a development wheel, run `python scripts/native_smoke.py` to check contiguous RGB, strided RGB, one-channel expansion, and invalid zero-channel input.

## Troubleshooting

- **`maturin>=1.14.1 is required`**: install `requirements.txt` in the selected Python environment.
- **`Rust/Cargo not found`**: install Rust from [rustup.rs](https://rustup.rs/) and restart the terminal.
- **Wheel tag does not match Python**: rebuild with the exact ComfyUI interpreter through `--python`.
- **Node import fails**: confirm ComfyUI uses Python 3.12+ and that `comfyui_ntsc_rs` is installed in that same environment.

## Project notes

- [Architecture](docs/ARCHITECTURE.md)
- [Dependencies and migration notes](docs/DEPENDENCIES.md)
- [Maintenance report](docs/MAINTENANCE_REPORT.md)
- [Known technical debt](docs/TECHNICAL_DEBT.md)

## Support

If this project saves you time, you can [sponsor the work on GitHub](https://github.com/sponsors/gvastethecreator) or [support it on Ko-fi](https://ko-fi.com/gvaste).

## License

This integration and its vendored components retain their declared MIT, ISC, and Apache-2.0 terms. See [LICENSE](LICENSE) and the vendored crate manifests.
