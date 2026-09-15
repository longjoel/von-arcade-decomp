#!/usr/bin/env sh
# Shim: the Virtual-On harness lives in `vonctl/`; see `vonctl --help`.
exec "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)/bin/vonctl" ghidra run "$@"
