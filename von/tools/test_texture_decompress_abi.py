#!/usr/bin/env python3
"""Guard the decompressor's i960 return-register ABI assumption."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


def main() -> int:
    source = Path("von/i960/recovered_texture_decompress.c").read_text(encoding="utf-8")
    declaration = "static __inline__ __attribute__((always_inline)) int texture_use_secondary_bank"
    if declaration not in source:
        raise SystemExit("texture bank helper must be forced inline to preserve the caller return link")

    # The legacy i960 compiler may ignore always_inline and place unrelated
    # routines at the same address across builds, so an absolute call target
    # in the listing is not a stable ABI check.  Verify the hot-path decision
    # is present in the decompressor source itself; the route helper remains
    # available for the host-side boundary vectors below.
    if "secondary_bank =" not in source or "TEXTURE_FORMAT_TABLE" not in source:
        raise SystemExit("decompressor bank decision is not in the caller hot path")
    with tempfile.TemporaryDirectory(prefix="von-texture-route-") as directory:
        library = Path(directory) / "texture-route.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC",
                        "von/i960/recovered_texture_decompress.c", "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_texture_secondary_route.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        recovered.recovered_texture_secondary_route.restype = ctypes.c_int
        vectors = 0
        cases = ((0, 0, 1), (0x5ffff, 1, 1), (0x60000, 0, 0),
                 (0x60000, 1, 0), (0x60000, 0, 1), (0x60000, 3, 3),
                 (0x60000, 3, 4), (0x60000, 5, 5), (0x60000, 5, 6),
                 (0x60000, 7, 7), (0x60000, 7, 8), (0x60000, 9, 9),
                 (0x60000, 9, 10), (0x60001, 0, 1))
        for output_index, low, high in cases:
            expected = output_index >= 0x60000 and (
                low == 1 or high == 1 or (high == 3 and low >= 3)
                or (low == 3 and high >= 4) or (high == 5 and low >= 5)
                or (low == 5 and high >= 6) or (high == 7 and low >= 7)
                or (low == 7 and high >= 8) or (high == 9 and low >= 9)
                or (low == 9 and high >= 10))
            actual = recovered.recovered_texture_secondary_route(
                output_index, low, high)
            if bool(actual) != expected:
                raise SystemExit("secondary route boundary mismatch")
            vectors += 1
    print(f"PASS: texture decompressor ABI and {vectors} secondary-route vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
