#!/usr/bin/env python3
"""Guard the decompressor's i960 return-register ABI assumption."""

from pathlib import Path


def main() -> int:
    source = Path("von/i960/recovered_texture_decompress.c").read_text(encoding="utf-8")
    declaration = "static __inline__ __attribute__((always_inline)) int texture_use_secondary_bank"
    if declaration not in source:
        raise SystemExit("texture bank helper must be forced inline to preserve the caller return link")

    listing = Path("von/build/i960/reconstructed.lst")
    if listing.exists() and listing.stat().st_mtime >= Path("von/i960/recovered_texture_decompress.c").stat().st_mtime:
        text = listing.read_text(encoding="utf-8")
        if "callx\t0x38e0" in text:
            raise SystemExit("reconstructed listing still contains the out-of-line bank helper call")
    print("PASS: texture decompressor preserves the return-link ABI contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
