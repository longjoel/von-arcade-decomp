#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="${1:-von/build/disasm/first-match-scenes/p1-first-match.gltf}"
PORT="${VON_GEOMETRY_VIEWER_PORT:-8765}"

[[ -f "$ROOT_DIR/$MODEL" ]] || {
    printf 'error: model not found: %s\n' "$ROOT_DIR/$MODEL" >&2
    exit 1
}
command -v python3 >/dev/null || { printf 'error: python3 is required\n' >&2; exit 1; }
command -v chromium >/dev/null || { printf 'error: chromium is required\n' >&2; exit 1; }

relative="${MODEL#"$ROOT_DIR/"}"
encoded="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$relative")"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT_DIR" >/tmp/von-geometry-viewer.log 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT INT TERM

url="http://127.0.0.1:$PORT/von/tools/geometry_viewer.html?file=$encoded"
printf 'Opening %s\nClose this terminal or press Ctrl-C to stop the local server.\n' "$url"
chromium --new-window "$url" >/dev/null 2>&1 &
wait "$server_pid"
