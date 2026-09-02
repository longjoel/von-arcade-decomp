/* Static formatter recovered from 0x000e3830 / 0x000e3a10. */
typedef unsigned char u8;

/* Emit the two ASCII digits selected by the ROM's glyph calls.
 * The callers provide nonnegative values; values above 99 become "99". */
int recovered_text_two_digit(int value, u8 out[2])
{
    if (value > 99)
        value = 99;
    if (value < 0)
        return 0;
    out[0] = (u8)('0' + value / 10);
    out[1] = (u8)('0' + value % 10);
    return 1;
}
