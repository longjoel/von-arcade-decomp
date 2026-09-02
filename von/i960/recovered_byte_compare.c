/* Recovered i960 byte-range comparison primitive at 0x000f5c58. */

typedef unsigned int u32;
typedef unsigned char u8;

/*
 * The ROM compares at most length bytes and returns the first left-minus-
 * right unsigned-byte difference.  Equal ranges return zero, including a
 * zero-length range.
 */
u32 recovered_byte_compare(const u8 *left, const u8 *right, u32 length)
{
    while (length != 0U) {
        u8 left_byte = *left++;
        u8 right_byte = *right++;
        if (left_byte != right_byte)
            return (u32)left_byte - (u32)right_byte;
        --length;
    }
    return 0U;
}
