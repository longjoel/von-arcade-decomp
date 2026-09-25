# MAME trace patches

The offline SCSP renderer (`von-godot/native/scsp`) needs register and
sound-RAM write traces from MAME. These two patches restore that capability to
the `mame/` submodule (it was dropped when the patch stack was folded into the
fork). Apply them before `vonctl build mame` when regenerating audio:

```sh
cd mame
git apply ../third_party/patches/0045-von-scsp-trace.patch \
          ../third_party/patches/0046-von-scsp-ram-trace.patch
cd .. && ./bin/vonctl build mame
```

- `0045` writes every SCSP register write to `$VON_SCSP_TRACE` (`W` lines),
  key-on/off to `K`/`O`, and dumps 512 KiB sound RAM to `$VON_SCSP_RAM_DUMP`.
- `0046` routes the 68000 sound RAM through `soundram_r/w` and writes every
  RAM write to `$VON_SCSP_RAM_TRACE` (`R` lines).

The Lua-only alternative does not work: a write tap over the shared sound RAM
segfaults MAME when the SCSP device accesses it.
