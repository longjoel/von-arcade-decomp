#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
require_command tar

"$ROOT_DIR/scripts/build.sh"
"$ROOT_DIR/scripts/test.sh"

VERSION="${VON_VERSION:-$(date -u +%Y%m%dT%H%M%SZ)}"
PACKAGE_NAME="von-arcade-decomp-$VERSION"
STAGE_DIR="$ROOT_DIR/von/build/deploy/$PACKAGE_NAME"
DIST_DIR="$ROOT_DIR/dist"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/bin" "$STAGE_DIR/scripts" "$STAGE_DIR/von/tools"
cp "$MAME_BIN" "$STAGE_DIR/bin/von"
cp "$ROOT_DIR/von/README.md" "$ROOT_DIR/von/rom_manifest.json" "$STAGE_DIR/von/"
cp "$ROOT_DIR/von/tools/mame_runner.py" "$ROOT_DIR/von/tools/rom_audit.py" "$STAGE_DIR/von/tools/"
cp "$ROOT_DIR/scripts/common.sh" "$ROOT_DIR/scripts/run.sh" "$ROOT_DIR/scripts/run-twin.sh" "$STAGE_DIR/scripts/"
chmod +x "$STAGE_DIR/bin/von" "$STAGE_DIR/scripts/run.sh"
chmod +x "$STAGE_DIR/scripts/run-twin.sh"

mkdir -p "$DIST_DIR"
tar -C "$ROOT_DIR/von/build/deploy" -czf "$DIST_DIR/$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"
printf 'Created %s\n' "$DIST_DIR/$PACKAGE_NAME.tar.gz"
printf '%s\n' 'ROMs are intentionally excluded from the deployment package.'
