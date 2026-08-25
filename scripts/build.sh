#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
"$ROOT_DIR/scripts/prepare-mame.sh"
require_command make
require_command brew

MESA_PREFIX="$(brew_prefix mesa)"
ALSA_PREFIX="$(brew_prefix alsa-lib)"
BREW_PREFIX="$(brew --prefix)"

# Keep MAME's quoted utility/frontend headers ahead of Brew's transitive PNG headers.
BREW_CFLAGS="-I$MESA_PREFIX/include -I$ALSA_PREFIX/include -I$BREW_PREFIX/include -I$BREW_PREFIX/include/SDL2"
BREW_CXXFLAGS="-iquote $MAME_DIR/src/frontend/mame -iquote $MAME_DIR/src/lib/util $BREW_CFLAGS"
BREW_LDFLAGS="-L$MESA_PREFIX/lib -L$BREW_PREFIX/lib"

printf 'Building reduced Virtual-On MAME target...\n'
(
    cd "$MAME_DIR"
    touch makefile
    rm -f build/generated/mame/von/drivlist.cpp
    CFLAGS="$BREW_CFLAGS" \
    CXXFLAGS="$BREW_CXXFLAGS" \
    LDFLAGS="$BREW_LDFLAGS" \
    make REGENIE=1 TARGET=mame SUBTARGET=von \
        SOURCES=src/mame/sega/model2.cpp \
        USE_QTDEBUG=0 NO_USE_MIDI=1 NO_USE_PORTAUDIO=1 NO_USE_PIPEWIRE=1 NO_USE_PULSEAUDIO=1 \
        -j"${JOBS:-$(nproc)}"
)
printf 'Built %s\n' "$MAME_BIN"
