/* Deterministic counter transition recovered from i960 routine 0x73498. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_match_result_counter_output {
    u32 pair_first;
    u32 pair_second;
    u32 cleared_504d9c;
    u32 cleared_504da4;
};

/*
 * The routine loads the pair at 0x504db0, increments its second word, and
 * compares that result with the supplied limit.  The two flags report the
 * conditional stores performed on the overflow path; zero means no store.
 */
void recovered_match_result_counter_73498(
    u32 pair_first, u32 pair_second, u32 limit,
    u32 global_504d98, u32 global_504dc0,
    struct recovered_match_result_counter_output *output)
{
    u32 next = pair_second + 1U;

    output->pair_first = pair_first;
    output->pair_second = next;
    output->cleared_504d9c = 0U;
    output->cleared_504da4 = 0U;

    if (next <= limit)
        return;

    output->pair_second = 0xffffffffU;
    output->cleared_504d9c = 1U;
    if (global_504d98 != 0U && global_504dc0 <= 99U)
        output->cleared_504da4 = 1U;
}
