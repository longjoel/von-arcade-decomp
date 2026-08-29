/* Recovered high-use runtime leaves at i960 0x73508 and 0xf5058. */

typedef unsigned int u32;
typedef signed short s16;

#define RANDOM_STATE (*(volatile u32 *)0x005785d0)

u32 recovered_random_step(u32 state)
{
    unsigned long long product;
    u32 low;
    u32 high;
    u32 folded;

    product = (unsigned long long)state * 0x5d588b65ULL;
    low = (u32)product;
    high = (u32)(product >> 32);
    folded = low + (high << 1) + (low >> 31);
    return folded & 0x7fffffffUL;
}

u32 recovered_random_next(void)
{
    u32 next = recovered_random_step(RANDOM_STATE);
    RANDOM_STATE = next;
    return next;
}

u32 recovered_signed_band(u32 raw)
{
    s16 value = (s16)raw;

    if (value >= 0) {
        if (value <= 0x038d)
            return 0;
        if (value <= 0x1554)
            return 1;
        if (value <= 0x3fff)
            return 2;
        if (value <= 0x5fff)
            return 3;
        return 4;
    }
    if (value < -0x6000)
        return 5;
    if (value < -0x4000)
        return 6;
    if (value < -0x1555)
        return 7;
    if (value < -0x038e)
        return 8;
    return 9;
}
