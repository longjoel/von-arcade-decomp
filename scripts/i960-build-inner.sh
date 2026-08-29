#!/usr/bin/env bash
set -euo pipefail

CPU_FLAG=""
if i960-elf-gcc -mkb -x c -c /dev/null -o /tmp/i960-kb-probe.o >/dev/null 2>&1; then
    CPU_FLAG="-mkb"
elif i960-elf-gcc -msa -x c -c /dev/null -o /tmp/i960-sa-probe.o >/dev/null 2>&1; then
    CPU_FLAG="-msa"
else
    printf 'error: compiler has no supported i960 CPU mode\n' >&2
    exit 1
fi

printf 'Using i960 CPU mode: %s\n' "$CPU_FLAG"
mkdir -p /src/von/build/i960

for source in main recovered_io recovered_host_queue recovered_host_control recovered_runtime_math recovered_audio_queue recovered_geometry recovered_geometry_commands recovered_text recovered_texture recovered_geometry_profile recovered_texture_decompress reconstructed_main; do
    i960-elf-gcc "$CPU_FLAG" -O1 -ffreestanding -fno-builtin -fno-common \
        -c "/src/von/i960/$source.c" -o "/src/von/build/i960/$source.o"
done

i960-elf-gcc "$CPU_FLAG" -O1 -ffreestanding -fno-builtin -fno-common \
    -c /src/von/i960/reconstructed_reset.c \
    -o /src/von/build/i960/reconstructed_reset.o

i960-elf-as -ahls=/src/von/build/i960/start.lst /src/von/i960/start.s \
    -o /src/von/build/i960/start.o
i960-elf-as -ahls=/src/von/build/i960/start_reconstructed.lst /src/von/i960/start_reconstructed.s \
    -o /src/von/build/i960/start_reconstructed.o

COMMON_OBJECTS=(
    /src/von/build/i960/recovered_io.o
    /src/von/build/i960/recovered_host_queue.o
    /src/von/build/i960/recovered_host_control.o
    /src/von/build/i960/recovered_runtime_math.o
    /src/von/build/i960/recovered_audio_queue.o
    /src/von/build/i960/recovered_geometry.o
    /src/von/build/i960/recovered_geometry_commands.o
    /src/von/build/i960/recovered_text.o
    /src/von/build/i960/recovered_texture.o
    /src/von/build/i960/recovered_geometry_profile.o
    /src/von/build/i960/recovered_texture_decompress.o
)

i960-elf-gcc "$CPU_FLAG" -nostdlib -nostartfiles \
    /src/von/build/i960/start.o /src/von/build/i960/main.o \
    "${COMMON_OBJECTS[@]}" \
    -T /src/von/i960/link.ld -Wl,-Map,/src/von/build/i960/prototype.map \
    -o /src/von/build/i960/prototype.elf
i960-elf-objcopy -O binary /src/von/build/i960/prototype.elf \
    /src/von/build/i960/prototype.bin
i960-elf-objdump -m i960 -b binary --adjust-vma=0 \
    -D /src/von/build/i960/prototype.bin > /src/von/build/i960/prototype.lst

i960-elf-gcc "$CPU_FLAG" -nostdlib -nostartfiles \
    /src/von/build/i960/start_reconstructed.o \
    /src/von/build/i960/reconstructed_main.o \
    "${COMMON_OBJECTS[@]}" \
    -T /src/von/i960/link.ld -Wl,-Map,/src/von/build/i960/reconstructed.map \
    -o /src/von/build/i960/reconstructed.elf
i960-elf-objcopy -O binary /src/von/build/i960/reconstructed.elf \
    /src/von/build/i960/reconstructed.bin
i960-elf-objdump -m i960 -b binary --adjust-vma=0 \
    -D /src/von/build/i960/reconstructed.bin > /src/von/build/i960/reconstructed.lst

i960-elf-gcc "$CPU_FLAG" -nostdlib -nostartfiles \
    /src/von/build/i960/reconstructed_reset.o \
    -T /src/von/i960/reset_slice.ld \
    -Wl,-Map,/src/von/build/i960/reconstructed_reset.map \
    -o /src/von/build/i960/reconstructed_reset.elf
i960-elf-objcopy -O binary /src/von/build/i960/reconstructed_reset.elf \
    /src/von/build/i960/reconstructed_reset.bin
truncate -s 184 /src/von/build/i960/reconstructed_reset.bin
i960-elf-objdump -m i960 -b binary --adjust-vma=0x930 \
    -D /src/von/build/i960/reconstructed_reset.bin > /src/von/build/i960/reconstructed_reset.lst

cp /src/von/build/i960/prototype.bin /src/von/build/i960/prototype-maincpu.bin
truncate -s 2097152 /src/von/build/i960/prototype-maincpu.bin
rm -rf /src/von/build/rompath/vonjdev
mkdir -p /src/von/build/rompath/vonjdev
ln -s ../../i960/prototype-maincpu.bin \
    /src/von/build/rompath/vonjdev/prototype-maincpu.bin

cp /src/von/build/i960/vonj-original-maincpu.bin \
    /src/von/build/i960/reconstructed-maincpu.bin
dd if=/src/von/build/i960/reconstructed.bin \
    of=/src/von/build/i960/reconstructed-maincpu.bin \
    bs=4096 conv=notrunc status=none
rm -rf /src/von/build/rompath/reconstructed/vonjdev
mkdir -p /src/von/build/rompath/reconstructed/vonjdev
ln -s ../../../i960/reconstructed-maincpu.bin \
    /src/von/build/rompath/reconstructed/vonjdev/prototype-maincpu.bin

for rom in \
    mpr-18648.11 mpr-18649.12 mpr-18650.9 mpr-18651.10 \
    mpr-18662.29 mpr-18663.30 mpr-18654.17 mpr-18655.21 \
    mpr-18656.18 mpr-18657.22 mpr-18660.27 mpr-18658.25 \
    mpr-18661.28 mpr-18659.26 epr-18643a.7 epr-18670.31 \
    mpr-18652.32 mpr-18653.34; do
    ln -s "../../../../artifacts/$rom" \
        "/src/von/build/rompath/reconstructed/vonjdev/$rom"
done

printf 'Built prototype and reconstructed i960 images\n'
