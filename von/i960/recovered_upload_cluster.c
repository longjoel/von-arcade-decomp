/* Executable upload-cluster driver for i960 0x29d50.
 *
 * This is the production counterpart of the pure schedule units
 * (recovered_upload_select_29d50.c, recovered_blend_kernel_29dec.c,
 * recovered_blend_loop_schedule_29e68.c,
 * recovered_blend_stride_schedule_29e4c.c,
 * recovered_direct_stride_schedule_29f60.c): it runs the same chain
 * against live windows instead of describing it. Window bases arrive as
 * parameters so host harnesses can substitute arrays for the mapped
 * device windows; the counter shift, guard, dispatch, kernel math, and
 * stride cadence match the listing exactly.
 *
 * Returns the number of texel stores performed (768 for a full run,
 * 0 when the sub-3 guard exits early).
 */
/* No libc headers: this file also ships in the freestanding i960 image. */
typedef unsigned int u32;
typedef signed int s32;

u32 recovered_blend_kernel_mul(u32 pixel, u32 factor);
u32 recovered_blend_kernel_fade(u32 pixel, u32 factor);

#define RECOVERED_UPLOAD_GUARD 3
#define RECOVERED_UPLOAD_PASSES 8U
#define RECOVERED_UPLOAD_INNER 32U

u32 recovered_upload_cluster_service(volatile u32 *fade_slot,
                                      volatile u32 *counter_slot,
                                      volatile u32 *mode_slot,
                                      volatile u32 *base_src0,
                                      volatile u32 *base_dst0,
                                      volatile u32 *base_src1,
                                      volatile u32 *base_dst1,
                                      volatile u32 *base_src2,
                                      volatile u32 *base_dst2)
{
    s32 counter = (s32)*counter_slot;
    u32 fade;
    u32 mode;
    u32 bank_words;
    volatile u32 *src0;
    volatile u32 *dst0;
    volatile u32 *src1;
    volatile u32 *dst1;
    volatile u32 *src2;
    volatile u32 *dst2;
    u32 pass;
    u32 stores = 0U;

    /* cmpibge 3,r7,0x29d6c: below-guards restore and return. */
    if (counter < RECOVERED_UPLOAD_GUARD)
        return 0U;
    *counter_slot = (u32)(counter + 1);
    /* shlo 12: the old counter selects a 4KB bank over the bases. */
    bank_words = (u32)counter << 10;
    src0 = base_src0 + bank_words;
    dst0 = base_dst0 + bank_words;
    src1 = base_src1 + bank_words;
    dst1 = base_dst1 + bank_words;
    src2 = base_src2 + bank_words;
    dst2 = base_dst2 + bank_words;
    fade = *fade_slot;
    mode = *mode_slot;

    if (mode == 0U) {
        /* Direct path: one factor for all three planes. cmpible
         * 0,r14 takes the fade form exactly when (s32)fade <= 0. */
        u32 use_fade = (s32)fade <= 0 ? 1U : 0U;
        u32 factor = use_fade ? fade : fade + 0x100U;
        for (pass = 0U; pass < RECOVERED_UPLOAD_PASSES; ++pass) {
            u32 inner;
            for (inner = 0U; inner < RECOVERED_UPLOAD_INNER; ++inner) {
                if (use_fade) {
                    *dst0 = recovered_blend_kernel_fade(*src0, factor);
                    *dst1 = recovered_blend_kernel_fade(*src1, factor);
                    *dst2 = recovered_blend_kernel_fade(*src2, factor);
                } else {
                    *dst0 = recovered_blend_kernel_mul(*src0, factor);
                    *dst1 = recovered_blend_kernel_mul(*src1, factor);
                    *dst2 = recovered_blend_kernel_mul(*src2, factor);
                }
                ++src0;
                ++dst0;
                ++src1;
                ++dst1;
                ++src2;
                ++dst2;
                stores += 3U;
            }
            src0 += 0x180U / 4U;
            dst0 += 0x180U / 4U;
            src1 += 0x180U / 4U;
            dst1 += 0x180U / 4U;
            src2 += 0x180U / 4U;
            dst2 += 0x180U / 4U;
        }
        return stores;
    }

    /* Blend path: r13 = 0x100 - fade selects the scale factor while the
     * set-bit planes keep the fade (add-back) form with g4. */
    {
        u32 scale = 0x100U - fade;
        for (pass = 0U; pass < RECOVERED_UPLOAD_PASSES; ++pass) {
            u32 inner;
            u32 fade0 = (mode >> 0) & 1U;
            u32 fade1 = (mode >> 1) & 1U;
            u32 fade2 = (mode >> 2) & 1U;
            for (inner = 0U; inner < RECOVERED_UPLOAD_INNER; ++inner) {
                *dst0 = fade0 ? recovered_blend_kernel_fade(*src0, fade)
                              : recovered_blend_kernel_mul(*src0, scale);
                *dst1 = fade1 ? recovered_blend_kernel_fade(*src1, fade)
                              : recovered_blend_kernel_mul(*src1, scale);
                *dst2 = fade2 ? recovered_blend_kernel_fade(*src2, fade)
                              : recovered_blend_kernel_mul(*src2, scale);
                ++src0;
                ++dst0;
                ++src1;
                ++dst1;
                ++src2;
                ++dst2;
                stores += 3U;
            }
            src0 += 0x180U / 4U;
            dst0 += 0x180U / 4U;
            src1 += 0x180U / 4U;
            dst1 += 0x180U / 4U;
            /* Pair 2 advances twice per pass: transition plus bottom. */
            src2 += 2U * (0x180U / 4U);
            dst2 += 2U * (0x180U / 4U);
        }
    }
    return stores;
}
