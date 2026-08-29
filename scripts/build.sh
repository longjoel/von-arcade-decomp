#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
"$ROOT_DIR/scripts/prepare-mame.sh"
require_command make
if command -v brew >/dev/null 2>&1 && brew list --formula mesa >/dev/null 2>&1 && brew list --formula alsa-lib >/dev/null 2>&1; then
    MESA_PREFIX="$(brew_prefix mesa)"
    ALSA_PREFIX="$(brew_prefix alsa-lib)"
    BREW_PREFIX="$(brew --prefix)"
    export CFLAGS="-I$MESA_PREFIX/include -I$ALSA_PREFIX/include -I$BREW_PREFIX/include -I$BREW_PREFIX/include/SDL2 ${CFLAGS:-}"
    export CXXFLAGS="-iquote $MAME_DIR/src/frontend/mame -iquote $MAME_DIR/src/lib/util $CFLAGS ${CXXFLAGS:-}"
    export LDFLAGS="-L$MESA_PREFIX/lib -L$BREW_PREFIX/lib ${LDFLAGS:-}"
fi

printf 'Building reduced Virtual-On MAME target...\n'
(
    cd "$MAME_DIR"
    touch makefile
    rm -f build/generated/mame/von/drivlist.cpp
    make REGENIE=1 TARGET=mame SUBTARGET=von \
        SOURCES=src/mame/sega/model2.cpp \
        USE_QTDEBUG=0 NO_USE_MIDI=1 NO_USE_PORTAUDIO=1 NO_USE_PIPEWIRE=1 NO_USE_PULSEAUDIO=1 \
        -j"${JOBS:-$(nproc)}"
)
[[ -x "$MAME_DIR/von" ]] || die "local MAME build did not produce $MAME_DIR/von"
mkdir -p "$(dirname "$MAME_BIN")"
cp "$MAME_DIR/von" "$MAME_BIN"
chmod +x "$MAME_BIN"
printf 'Built %s\n' "$MAME_BIN"
