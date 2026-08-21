MEMORY
{
    rom (rx)  : ORIGIN = 0x00000000, LENGTH = 0x00200000
    ram (rwx) : ORIGIN = 0x00500000, LENGTH = 0x00100000
}

SECTIONS
{
    .text :
    {
        KEEP(*(.text))
        *(.rodata*)
    } > rom

    .data :
    {
        *(.data*)
    } > ram AT > rom

    .bss (NOLOAD) :
    {
        *(.bss*)
        *(COMMON)
    } > ram

    _end = .;
}

_checksum = -(_system_address_table + _rom_prcb + _start_ip);
