/* Per-texel blend kernel shared by the 0x29d50 masked-blend loops.
 *
 * Every loop body in 0x29dc0-0x2a0bc reduces to one of two forms over the
 * masked pixel (in & 0x00ff00ff): a scaled form out = (factor * masked) >> 8
 * (bit-clear blend arm, direct arm) or a fade form
 * out = masked + (factor * (masked - mask)) >> 8 (bit-set blend arm,
 * direct arm). Products keep the low 32 bits; shifts are logical.
 */
#include <stdint.h>

typedef uint32_t u32;

#define RECOVERED_BLEND_MASK 0x00ff00ffU

static u32 recovered_blend_mullo(u32 factor, u32 value)
{
    return (u32)((uint64_t)factor * (uint64_t)value);
}

u32 recovered_blend_kernel_mul(u32 pixel, u32 factor)
{
    u32 masked = pixel & RECOVERED_BLEND_MASK;

    return recovered_blend_mullo(factor, masked) >> 8;
}

u32 recovered_blend_kernel_fade(u32 pixel, u32 factor)
{
    u32 masked = pixel & RECOVERED_BLEND_MASK;
    u32 diff = masked - RECOVERED_BLEND_MASK;

    return masked + (recovered_blend_mullo(factor, diff) >> 8);
}
