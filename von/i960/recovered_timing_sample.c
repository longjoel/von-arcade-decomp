/* Recovered deterministic portion of i960 0x00018ab0. */

#include <stdint.h>

struct recovered_timing_sample_state {
    uint32_t latest;
    uint32_t low;
    uint32_t high;
};

/*
 * 0x28de8 supplies sample.  The caller always records it as the latest
 * sample; profile 4 additionally tightens the low/high extrema.
 */
void recovered_timing_sample_update(struct recovered_timing_sample_state *state,
                                    uint32_t sample,
                                    uint32_t profile)
{
    state->latest = sample;
    if (profile != 4U)
        return;
    if (sample < state->low)
        state->low = sample;
    if (sample > state->high)
        state->high = sample;
}
