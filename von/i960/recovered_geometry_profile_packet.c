/* Byte-accurate framing recovered from i960 0xc5d70. */

#include <stdint.h>

/*
 * Build the command words written to 0x884000.  The four profile-3 math
 * words are intentionally supplied by the caller as [g4, g6, g1, g5]: they
 * are produced by the i960 extended floating-point sequence at
 * 0xc5dac-0xc5e70.  fifo_result is
 * the mapped-FIFO value read back by the common tail before its three writes
 * to 0x804000.
 */
uint32_t recovered_geometry_profile_packet(
    uint32_t profile,
    uint32_t input,
    uint32_t output_tag,
    const uint32_t profile3_math[4],
    const uint32_t fallback_words[3],
    uint32_t fifo_result,
    uint32_t command[14],
    uint32_t output[4])
{
    uint32_t masked7 = (input << 7) & 0xffffU;
    uint32_t masked6 = (input << 6) & 0xffffU;

    if (profile == 3U) {
        command[0] = 28U;
        command[1] = masked7;
        command[2] = 27U;
        command[3] = masked6;
        command[4] = 28U;
        command[5] = profile3_math[0];
        command[6] = 28U;
        command[7] = profile3_math[0];
        command[8] = 28U;
        command[9] = masked6;
        command[10] = 43U;
        command[11] = profile3_math[1];
        command[12] = profile3_math[2];
        command[13] = profile3_math[3];
        output[0] = fifo_result;
        output[1] = fifo_result;
        output[2] = fifo_result;
        output[3] = output_tag;
        return 14U;
    }

    command[0] = 43U;
    command[1] = fallback_words[0];
    command[2] = fallback_words[1];
    command[3] = fallback_words[2];
    output[0] = fifo_result;
    output[1] = fifo_result;
    output[2] = fifo_result;
    output[3] = output_tag;
    return 4U;
}
