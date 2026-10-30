"""ComfyUI-Manager install hook: fetch this platform's prebuilt native binary into ./native/."""

import native

if native.load_native() is None:
    print(native.problem)
