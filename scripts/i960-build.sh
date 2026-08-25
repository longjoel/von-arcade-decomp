#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="ghcr.io/nkito/i960_sbc@sha256:c4baf40df8c6db1774e2bb87020824ca0d99201b11fb1944ef3a6d2922bd4b6c"
SRC_DIR="$ROOT_DIR/von/i960"
OUT_DIR="$ROOT_DIR/von/build/i960"

command -v docker >/dev/null 2>&1 || {
    printf 'error: docker is required\n' >&2
    exit 1
}

mkdir -p "$OUT_DIR"

docker run --rm \
    -v "$ROOT_DIR:/src" \
    -w /src/von/i960 \
    --entrypoint /bin/bash \
    "$IMAGE" \
    -lc '
set -euo pipefail
mkdir -p /src/von/build/i960

CPU_FLAG=""
if i960-elf-gcc -mkb -x c -c /dev/null -o /tmp/i960-kb-probe.o >/dev/null 2>&1; then
    CPU_FLAG="-mkb"
elif i960-elf-gcc -msa -x c -c /dev/null -o /tmp/i960-sa-probe.o >/dev/null 2>&1; then
    CPU_FLAG="-msa"
else
    printf "error: compiler has no supported i960 CPU mode\n" >&2
    exit 1
fi

printf "Using i960 CPU mode: %s\n" "$CPU_FLAG"
i960-elf-gcc "$CPU_FLAG" -O1 -ffreestanding -fno-builtin -fno-common \
    -c main.c -o /src/von/build/i960/main.o
i960-elf-gcc "$CPU_FLAG" -O1 -ffreestanding -fno-builtin -fno-common \
    -c recovered_geometry.c -o /src/von/build/i960/recovered_geometry.o
i960-elf-gcc "$CPU_FLAG" -O1 -ffreestanding -fno-builtin -fno-common \
    -c recovered_geometry_commands.c -o /src/von/build/i960/recovered_geometry_commands.o
i960-elf-gcc "$CPU_FLAG" -O1 -ffreestanding -fno-builtin -fno-common \
    -c recovered_texture.c -o /src/von/build/i960/recovered_texture.o
i960-elf-as -ahls=/src/von/build/i960/start.lst start.s \
    -o /src/von/build/i960/start.o
i960-elf-gcc "$CPU_FLAG" -nostdlib -nostartfiles \
    /src/von/build/i960/start.o /src/von/build/i960/main.o \
    /src/von/build/i960/recovered_geometry.o \
    /src/von/build/i960/recovered_geometry_commands.o \
    /src/von/build/i960/recovered_texture.o \
    -T link.ld -Wl,-Map,/src/von/build/i960/prototype.map \
    -o /src/von/build/i960/prototype.elf
i960-elf-objcopy -O binary /src/von/build/i960/prototype.elf \
    /src/von/build/i960/prototype.bin
cp /src/von/build/i960/prototype.bin /src/von/build/i960/prototype-maincpu.bin
truncate -s 2097152 /src/von/build/i960/prototype-maincpu.bin
i960-elf-objdump -m i960 -b binary --adjust-vma=0 -D \
    /src/von/build/i960/prototype.bin > /src/von/build/i960/prototype.lst

rm -rf /src/von/build/rompath/vonjdev
mkdir -p /src/von/build/rompath/vonjdev
ln -s ../../i960/prototype-maincpu.bin \
    /src/von/build/rompath/vonjdev/prototype-maincpu.bin
for rom in \
    mpr-18648.11 mpr-18649.12 mpr-18650.9 mpr-18651.10 \
    mpr-18662.29 mpr-18663.30 mpr-18654.17 mpr-18655.21 \
    mpr-18656.18 mpr-18657.22 mpr-18660.27 mpr-18658.25 \
    mpr-18661.28 mpr-18659.26 epr-18643a.7 epr-18670.31 \
    mpr-18652.32 mpr-18653.34; do
    ln -s "../../../artifacts/$rom" "/src/von/build/rompath/vonjdev/$rom"
done
printf "Built /src/von/build/i960/prototype.bin\n"
'
