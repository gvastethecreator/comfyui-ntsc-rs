"""Exercise the installed native extension at its public NumPy boundary."""

from __future__ import annotations

import comfyui_ntsc_rs
import numpy as np


def main() -> int:
    source = np.arange(32 * 48 * 3, dtype=np.uint8).reshape(32, 48, 3)

    contiguous = comfyui_ntsc_rs.apply_ntsc_filter(source, {"random_seed": 7})
    assert contiguous.shape == source.shape
    assert contiguous.dtype == np.uint8
    assert np.any(contiguous != source)

    non_contiguous_source = source[:, ::2, :]
    non_contiguous = comfyui_ntsc_rs.apply_ntsc_filter(non_contiguous_source, {"random_seed": 7})
    assert non_contiguous.shape == non_contiguous_source.shape
    assert non_contiguous.dtype == np.uint8

    one_channel = comfyui_ntsc_rs.apply_ntsc_filter(source[:, :, :1], {"random_seed": 7})
    assert one_channel.shape == source.shape
    assert one_channel.dtype == np.uint8

    try:
        comfyui_ntsc_rs.apply_ntsc_filter(np.empty((4, 4, 0), dtype=np.uint8), {})
    except ValueError as error:
        assert str(error) == "image must contain at least one channel"
    else:
        raise AssertionError("A zero-channel input must be rejected.")

    print("Native smoke passed: contiguous RGB, strided RGB, one channel, and invalid input.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
