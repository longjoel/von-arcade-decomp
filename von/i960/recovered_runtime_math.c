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

/* Host-injectable form of the exact 0xf50a8 persistent-state store. */
void recovered_random_seed_state(volatile u32 *state, u32 seed)
{
    *state = seed;
}

void recovered_random_seed(u32 seed)
{
    recovered_random_seed_state(&RANDOM_STATE, seed);
}

/*
 * 0x73508 receives its argument in g0, but deliberately truncates it to a
 * signed halfword before comparing.  Keep that ABI detail at the public
 * wrapper: callers pass full-width subtractions, while the original leaf
 * classifies only their low 16 bits.
 *
 * The returned index is consumed immediately as a lookup-table index by the
 * match/profile paths (including 0x73e48, 0x74550, 0x7521c, 0x75348,
 * 0x75360, 0x76634, 0x76688, 0x76c9c, 0x76d40, and 0x76f9c).
 */
static u32 recovered_signed_band_value(s16 value)
{
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

u32 recovered_signed_band(u32 raw)
{
    return recovered_signed_band_value((s16)raw);
}
