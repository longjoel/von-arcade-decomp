# Communication Z80 Disassembly

The communication-board firmware is `epr-18643a.7`, loaded by MAME into the
`cpu3` region with `ROM_LOAD16_WORD_SWAP`. Reconstruct the linear Z80 image and
listing with:

```sh
./scripts/disasm-cpu3.sh
```

The generated files are ignored build outputs:

- `von/build/disasm/vonj-cpu3.bin`
- `von/build/disasm/vonj-cpu3.lst`

The canonical image is 0x20000 bytes. Its initial bytes currently decode as:

```text
00000: a2        and  d
00001: c3 ff 01  jp   $01FF
00004: ff        rst  $38
...
0000e: c9        ret
```

This confirms the word-swapped extraction is producing valid Z80 instruction
boundaries, but the reset/vector interpretation is not assigned beyond the
observed target until the `0x01ff` path is followed and corroborated by MAME
runtime PCs.
