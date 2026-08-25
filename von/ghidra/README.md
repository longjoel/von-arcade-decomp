# Ghidra i960 Analysis

The local Ghidra 11.3.1 installation does not ship with an i960 processor
definition. Install the pinned Apache-licensed community module with:

```sh
GHIDRA_HOME=/path/to/ghidra_11.3.1_PUBLIC ./scripts/install-ghidra-i960.sh
```

Then import and analyze the reconstructed `vonj` host ROM with:

```sh
GHIDRA_HOME=/path/to/ghidra_11.3.1_PUBLIC ./scripts/ghidra-i960.sh
```

The script reconstructs `von/build/disasm/vonj-maincpu.bin`, imports it as
`i960:LE:32:default`, runs normal Ghidra analysis, and applies the labels in
`AnnotateVonI960.py`. It then writes a focused reset/UI/geometry report using
`ReportVonI960.py`. The Ghidra project and report are generated under the
ignored `von/build/ghidra/` directory and should not be committed.

The processor module is an external dependency. Keep the pinned revision and
the import/annotation scripts under version control; do not copy the generated
Ghidra database into the repository.
