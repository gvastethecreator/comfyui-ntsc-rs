# Code map: comfy-ntscrs

Generated: 2026-10-30T17:08:27Z | Commit: `e77ab9ba22b2` | Schema: 2
Generation: `462c1c95fad6cf8bfb8ec966c84c11d40119cd8d24d92733ebc41ca0e00a4b45`
Scope: . | Inventory: working-tree
Nodes: 43 | Edges: 106 | Flows: 0

## Coverage

- Analysis: **partial**; 19 analyzed of 23 included files.
- Configuration files: 4; omitted untracked files: 0.
- Unresolved references and analysis limits: 20.
- Static references and call paths do not prove runtime execution or test coverage.

## Modules

- `__init__.py` | module | Repository | callers: none | callees: external:python:comfy_api, native.py, ntsc_node.py, ntsc_node_artifacts.py | tests: 0 | entry: none
- `build_node.py` | module | Repository | callers: none | callees: external:python:__future__, external:python:argparse, external:python:argparse, external:python:pathlib | tests: 0 | entry: none
- `external:python:__future__` | external | External | callers: build_node.py, native.py, scripts/clean_generated.py, scripts/native_smoke.py | callees: none | tests: 0 | entry: none
- `external:python:argparse` | external | External | callers: build_node.py, build_node.py, scripts/verify.py, scripts/verify.py | callees: none | tests: 0 | entry: none
- `external:python:comfy_api` | external | External | callers: __init__.py, ntsc_node.py, ntsc_node_artifacts.py, ntsc_node_global.py | callees: none | tests: 0 | entry: none
- `external:python:comfyui_ntsc_rs` | external | External | callers: native.py | callees: none | tests: 0 | entry: none
- `external:python:functools` | external | External | callers: native.py | callees: none | tests: 0 | entry: none
- `external:python:importlib` | external | External | callers: native.py | callees: none | tests: 0 | entry: none
- `external:python:numpy` | external | External | callers: native.py, scripts/native_smoke.py, scripts/native_smoke.py | callees: none | tests: 0 | entry: none
- `external:python:pathlib` | external | External | callers: build_node.py, build_node.py, native.py, native.py | callees: none | tests: 0 | entry: none
- `external:python:platform` | external | External | callers: native.py, native.py | callees: none | tests: 0 | entry: none
- `external:python:shutil` | external | External | callers: build_node.py, build_node.py, scripts/clean_generated.py, scripts/clean_generated.py | callees: none | tests: 0 | entry: none
- `external:python:subprocess` | external | External | callers: build_node.py, build_node.py, scripts/verify.py, scripts/verify.py | callees: none | tests: 0 | entry: none
- `external:python:sys` | external | External | callers: build_node.py, native.py, scripts/native_smoke.py, scripts/verify.py | callees: none | tests: 0 | entry: none
- `external:python:tomllib` | external | External | callers: native.py, native.py | callees: none | tests: 0 | entry: none
- `external:python:torch` | external | External | callers: native.py, ntsc_node_scale.py, ntsc_node_scale.py | callees: none | tests: 0 | entry: none
- `external:python:types` | external | External | callers: native.py | callees: none | tests: 0 | entry: none
- `external:python:urllib` | external | External | callers: native.py | callees: none | tests: 0 | entry: none
- `external:python:zipfile` | external | External | callers: build_node.py, build_node.py | callees: none | tests: 0 | entry: none
- `external:rust:ntsc_rs` | external | External | callers: rust_binding/src/lib.rs, rust_binding/src/lib.rs | callees: none | tests: 0 | entry: none
- Showing 20 of 43 nodes. Query `impact --module <path>` or open the HTML hierarchy for the rest.

## Edges

- `__init__.py` -> `external:python:comfy_api` | imports
- `__init__.py` -> `native.py` | imports
- `__init__.py` -> `ntsc_node.py` | imports
- `__init__.py` -> `ntsc_node_artifacts.py` | imports
- `__init__.py` -> `ntsc_node_global.py` | imports
- `__init__.py` -> `ntsc_node_intermediate.py` | imports
- `__init__.py` -> `ntsc_node_noise.py` | imports
- `__init__.py` -> `ntsc_node_scale.py` | imports
- `__init__.py` -> `ntsc_node_scanlines.py` | imports
- `__init__.py` -> `ntsc_node_signal.py` | imports
- `__init__.py` -> `ntsc_node_simple.py` | imports
- `__init__.py` -> `ntsc_node_vhs.py` | imports
- `build_node.py` -> `external:python:__future__` | imports
- `build_node.py` -> `external:python:argparse` | calls
- `build_node.py` -> `external:python:argparse` | imports
- `build_node.py` -> `external:python:pathlib` | calls
- `build_node.py` -> `external:python:pathlib` | imports
- `build_node.py` -> `external:python:shutil` | calls
- `build_node.py` -> `external:python:shutil` | imports
- `build_node.py` -> `external:python:subprocess` | calls
- `build_node.py` -> `external:python:subprocess` | imports
- `build_node.py` -> `external:python:sys` | imports
- `build_node.py` -> `external:python:zipfile` | calls
- `build_node.py` -> `external:python:zipfile` | imports
- `build_node.py` -> `native.py` | imports
- `install.py` -> `native.py` | calls
- `install.py` -> `native.py` | imports
- `native.py` -> `external:python:__future__` | imports
- `native.py` -> `external:python:comfyui_ntsc_rs` | imports
- `native.py` -> `external:python:functools` | imports
- `native.py` -> `external:python:importlib` | imports
- `native.py` -> `external:python:numpy` | imports
- `native.py` -> `external:python:pathlib` | calls
- `native.py` -> `external:python:pathlib` | imports
- `native.py` -> `external:python:platform` | calls
- `native.py` -> `external:python:platform` | imports
- `native.py` -> `external:python:sys` | imports
- `native.py` -> `external:python:tomllib` | calls
- `native.py` -> `external:python:tomllib` | imports
- `native.py` -> `external:python:torch` | imports
- `native.py` -> `external:python:types` | imports
- `native.py` -> `external:python:urllib` | imports
- `ntsc_node.py` -> `external:python:comfy_api` | imports
- `ntsc_node.py` -> `native.py` | calls
- `ntsc_node.py` -> `native.py` | imports
- `ntsc_node_artifacts.py` -> `external:python:comfy_api` | imports
- `ntsc_node_artifacts.py` -> `native.py` | calls
- `ntsc_node_artifacts.py` -> `native.py` | imports
- `ntsc_node_global.py` -> `external:python:comfy_api` | imports
- `ntsc_node_global.py` -> `native.py` | calls
- Showing 50 of 106 edges; JSON contains every edge and its evidence.

## Unknown

- `ntsc_node.py:32`: object-member-call-not-resolved (io)
- `ntsc_node.py:575`: object-member-call-not-resolved (io)
- `ntsc_node_artifacts.py:17`: object-member-call-not-resolved (io)
- `ntsc_node_artifacts.py:213`: object-member-call-not-resolved (io)
- `ntsc_node_global.py:17`: object-member-call-not-resolved (io)
- `ntsc_node_global.py:142`: object-member-call-not-resolved (io)
- `ntsc_node_intermediate.py:26`: object-member-call-not-resolved (io)
- `ntsc_node_intermediate.py:120`: object-member-call-not-resolved (io)
- `ntsc_node_noise.py:17`: object-member-call-not-resolved (io)
- `ntsc_node_noise.py:241`: object-member-call-not-resolved (io)
- `ntsc_node_scale.py:46`: object-member-call-not-resolved (io)
- `ntsc_node_scale.py:87`: object-member-call-not-resolved (io)

## Flows

- no source-backed call path from a recognized trigger

## Architecture changes

- Nodes: +0 / -0; edges: +0 / -0.
- Boundary changes: 0; new cycles: 0.

## Read next

- Use `status` before relying on this generation.
- Use `impact --changed` for possible impact and related test evidence.
- Use `diff --before <model> --after <model>` for architecture changes.
