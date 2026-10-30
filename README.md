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
    <a href="LICENSE"><img alt="MIT license" src="https://shieldcn.dev/github/license/gvastethecreator/comfyui-ntsc-rs.svg?variant=secondary&size=xs" /></a>
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

## Example workflows

[`example_workflows/`](example_workflows) holds four graphs. ComfyUI lists them under **Templates → comfyui-ntsc-rs**; you can also drop a JSON file onto the canvas. Each `.jpg` is the real output of its workflow (ComfyUI 0.43, seed 23).

| Workflow | Graph |
| --- | --- |
| [Simple VHS](example_workflows/NTSC-RS_Simple_VHS.json) | Load Image → Simple (`vhs_classic`) → Save |
| [Intermediate CRT](example_workflows/NTSC-RS_Intermediate_CRT.json) | Load Image → Intermediate (`crt_tv`) → Save |
| [Chain worn tape](example_workflows/NTSC-RS_Chain_Worn_Tape.json) | Load Image → Signal → Artifacts → Noise → VHS → Save |
| [Advanced security cam](example_workflows/NTSC-RS_Advanced_Security_Cam.json) | Load Image → Advanced (EP tape, snow, phase error) → Save |

## Requirements

- ComfyUI 0.3.48 or newer (V3 node API, `comfy_entrypoint`).
- Python 3.12 or newer. NumPy comes with ComfyUI; PyTorch comes with ComfyUI and is not pinned here.
- A prebuilt binary exists for Windows x64, Linux x64/arm64 (glibc 2.17+) and macOS arm64/x64. Other platforms need Rust 1.89+ to build it.

## Install

**ComfyUI-Manager or Comfy Registry:** search for *NTSC-RS* and install, or run `comfy node install comfyui-ntsc-rs`. Restart ComfyUI.

**Git clone:**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/gvastethecreator/comfyui-ntsc-rs.git
```

Restart ComfyUI. On first start, the node downloads the binary that matches this version and platform from the [GitHub release](https://github.com/gvastethecreator/comfyui-ntsc-rs/releases) into `native/`. After that it works offline. Nothing is installed into the Python environment. A successful start prints no NTSC-RS warning.

**Build from source** (no prebuilt binary, offline machine, or local changes). Install [Rust](https://rustup.rs/), then run with the Python that runs ComfyUI:

```bash
python -m pip install "maturin>=1.16,<2"
python build_node.py
```

`build_node.py` builds one abi3 wheel and copies its extension into `native/`, where the node loads it. Add `--install` to also pip-install the wheel into `--python PATH`.

If the binary is missing, ComfyUI still starts: the console prints the reason and the exact build command, and running a node raises the same message.

Agents: follow [AGENTS.md](AGENTS.md).

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
| NTSC-RS Scale | Resize the image (presets or custom horizontal/vertical factors). |

Start with **Simple**. Use the chainable nodes when a workflow needs one isolated effect family; put **Signal** first, because the other chainable nodes keep the signal stage neutral. Use **Advanced** only when every parameter must be exposed. The full input list is on the [project site](https://gvastethecreator.github.io/comfyui-ntsc-rs/#reference).

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install numpy torch "maturin==1.16.0" "ruff==0.17.3"
python scripts/verify.py          # ruff, cargo fmt/check/test/clippy
python build_node.py --dev        # fast build into native/
python scripts/native_smoke.py    # load native/ like the node does and check the NumPy boundary
```

`Cargo.lock` is authoritative; builds pass `--locked`. `python scripts/verify.py --fix` formats Python and Rust. `python scripts/clean_generated.py` removes build output.

Release: bump `version` in `pyproject.toml` and `rust_binding/Cargo.toml`, push a `vX.Y.Z` tag, and publish the draft release that [release.yml](.github/workflows/release.yml) creates. Then run [publish.yml](.github/workflows/publish.yml) by hand to push the node, with binaries bundled, to the Comfy Registry (needs the `REGISTRY_ACCESS_TOKEN` secret).

## Troubleshooting

- **`[NTSC-RS] ... HTTP Error 404`**: no release exists yet for this version, or GitHub is unreachable. Build from source.
- **`no prebuilt binary for <os>/<arch>`**: build from source.
- **`Rust/Cargo not found`**: install Rust from [rustup.rs](https://rustup.rs/) and restart the terminal.
- **`Needs ComfyUI 0.3.48 or newer`**: update ComfyUI.

## Support

If this project saves you time, you can [sponsor the work on GitHub](https://github.com/sponsors/gvastethecreator) or [support it on Ko-fi](https://ko-fi.com/gvaste).

## License

MIT. The vendored [ntsc-rs](https://github.com/valadaptive/ntsc-rs) is offered under MIT OR ISC OR Apache-2.0 and is used here under MIT; see [LICENSE](LICENSE) and [rust_binding/vendor/LICENSE-MIT](rust_binding/vendor/LICENSE-MIT).
