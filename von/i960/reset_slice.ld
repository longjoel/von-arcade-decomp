MEMORY
{
    /* Leave room for compiler-generated prologue/epilogue while comparing
     * only the original bounded range 0x930-0x9e8. */
    rom (rx) : ORIGIN = 0x00000930, LENGTH = 0x00001000
}

SECTIONS
{
    .text 0x00000930 :
    {
        *(.text*)
    } > rom
}
