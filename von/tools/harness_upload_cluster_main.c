/* Host harness main for the upload-cluster driver.
 *
 * Not part of the i960 image: it executes
 * recovered_upload_cluster_service against array windows and checks
 * store counts, counter bumps, and oracle-derived first/last/xor
 * words per plane (constants from the independent integer model).
 * Returns 0 only when every scenario matches.
 */
#include <stdint.h>
#include <stdio.h>

typedef uint32_t u32;

u32 recovered_upload_cluster_service(volatile u32 *fade_slot,
                                      volatile u32 *counter_slot,
                                      volatile u32 *mode_slot,
                                      volatile u32 *base_src0,
                                      volatile u32 *base_dst0,
                                      volatile u32 *base_src1,
                                      volatile u32 *base_dst1,
                                      volatile u32 *base_src2,
                                      volatile u32 *base_dst2);

#define WORDS 8192U

static u32 src0[WORDS];
static u32 dst0[WORDS];
static u32 src1[WORDS];
static u32 dst1[WORDS];
static u32 src2[WORDS];
static u32 dst2[WORDS];

static u32 pattern(u32 index)
{
    return 0xA5000000U | ((index * 0x010203U) & 0xFFFFFFU);
}

static void fill(void)
{
    u32 i;
    for (i = 0U; i < WORDS; ++i) {
        u32 px = pattern(i);
        src0[i] = px;
        src1[i] = px;
        src2[i] = px;
        dst0[i] = 0U;
        dst1[i] = 0U;
        dst2[i] = 0U;
    }
}

/* XOR over the pairs 0/1 footprint: 8 passes of 32 words with a
 * 0x180 stride between passes. Pair 2 uses a wider cadence and is
 * covered by first/last word checks instead. */
static u32 plane_xor(const volatile u32 *dst, u32 base)
{
    u32 x = 0U;
    u32 pass;
    u32 inner;
    for (pass = 0U; pass < 8U; ++pass) {
        for (inner = 0U; inner < 32U; ++inner)
            x ^= dst[base + pass * (32U + 96U) + inner];
    }
    return x;
}

static int failures;

static void check(const char *name, u32 got, u32 want)
{
    if (got != want) {
        printf("MISMATCH %s: got 0x%08lx want 0x%08lx\n", name,
               (unsigned long)got, (unsigned long)want);
        ++failures;
    }
}

int main(void)
{
    volatile u32 fade_slot;
    volatile u32 counter_slot;
    volatile u32 mode_slot;
    u32 stores;

    /* Guard scenario: counter 2 performs nothing. */
    fill();
    fade_slot = 0x80U;
    counter_slot = 2U;
    mode_slot = 0U;
    stores = recovered_upload_cluster_service(
        &fade_slot, &counter_slot, &mode_slot, src0, dst0, src1, dst1,
        src2, dst2);
    check("guard.stores", stores, 0U);
    check("guard.counter", counter_slot, 2U);
    check("guard.dst", dst0[4096], 0U);

    /* Direct scenario: fade 0x80 over bank 4. */
    fill();
    fade_slot = 0x80U;
    counter_slot = 4U;
    mode_slot = 0U;
    stores = recovered_upload_cluster_service(
        &fade_slot, &counter_slot, &mode_slot, src0, dst0, src1, dst1,
        src2, dst2);
    check("direct.stores", stores, 768U);
    check("direct.counter", counter_slot, 5U);
    check("direct.first", dst0[4096], 0x00300000U);
    check("direct.last", dst0[5023], 0x0029014BU);
    check("direct.xor", plane_xor(dst0, 4096U), 0x00000000U);
    check("direct.p2last", dst2[5023], 0x0029014BU);

    /* Direct fade form: fade 0 is an identity run over bank 4. */
    fill();
    fade_slot = 0U;
    counter_slot = 4U;
    mode_slot = 0U;
    stores = recovered_upload_cluster_service(
        &fade_slot, &counter_slot, &mode_slot, src0, dst0, src1, dst1,
        src2, dst2);
    check("fade.stores", stores, 768U);
    check("fade.first", dst1[4096], 0x00200000U);
    check("fade.last", dst1[5023], 0x00C600DDU);
    check("fade.xor", plane_xor(dst1, 4096U), 0x00000000U);

    /* Blend scenario: mode 0b101 over bank 5. */
    fill();
    fade_slot = 0x80U;
    counter_slot = 5U;
    mode_slot = 0x5U;
    stores = recovered_upload_cluster_service(
        &fade_slot, &counter_slot, &mode_slot, src0, dst0, src1, dst1,
        src2, dst2);
    check("blend.stores", stores, 768U);
    check("blend.counter", counter_slot, 6U);
    check("blend.p0first", dst0[5120], 0x00BC7F80U);
    check("blend.p0last", dst0[6047], 0x01B580CCU);
    check("blend.p0xor", plane_xor(dst0, 5120U), 0x00080000U);
    check("blend.p1first", dst1[5120], 0x00140000U);
    check("blend.p1last", dst1[6047], 0x0067006EU);
    check("blend.p2first", dst2[5120], 0x00BC7F80U);
    check("blend.p2last", dst2[6719], 0x012D009CU);

    if (failures == 0)
        printf("HARNESS PASS: guard, direct, fade, blend\n");
    return failures != 0;
}
