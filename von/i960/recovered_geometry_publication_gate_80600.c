/* Publication gate recovered from i960 0x80600-0x80650. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_publication_gate_80600_plan {
    u32 global_counter;
    u32 counter_threshold;
    int32_t comparison_value;
    int32_t first_threshold;
    u32 mode_word;
    int32_t second_threshold;
    int32_t third_threshold;
    u32 counter_gate_passed;
    u32 first_comparison_passed;
    u32 mode4_comparison_passed;
    u32 mode5_comparison_passed;
    u32 publication_gate_passed;
    u32 target;
};

/*
 * The first cmpible rejects counters through 0x5dc.  The first cmpr branches
 * to the status tail when comparison_value < first_threshold.  Otherwise,
 * mode 4 uses second_threshold and mode 5 uses third_threshold; both use the
 * same strict-less admission, while all other modes reject at 0x806f4.
 */
void recovered_geometry_publication_gate_80600(
    u32 global_counter,
    int32_t comparison_value,
    int32_t first_threshold,
    u32 mode_word,
    int32_t second_threshold,
    int32_t third_threshold,
    struct recovered_geometry_publication_gate_80600_plan *plan)
{
    const u32 counter_passed = global_counter > 0x5dcU ? 1U : 0U;
    const u32 first_passed = comparison_value < first_threshold ? 1U : 0U;
    const u32 mode4_passed = mode_word == 4U &&
                             comparison_value < second_threshold ? 1U : 0U;
    const u32 mode5_passed = mode_word == 5U &&
                             comparison_value < third_threshold ? 1U : 0U;
    const u32 admitted = counter_passed != 0U &&
                         (first_passed != 0U || mode4_passed != 0U ||
                          mode5_passed != 0U) ? 1U : 0U;

    plan->global_counter = global_counter;
    plan->counter_threshold = 0x5dcU;
    plan->comparison_value = comparison_value;
    plan->first_threshold = first_threshold;
    plan->mode_word = mode_word;
    plan->second_threshold = second_threshold;
    plan->third_threshold = third_threshold;
    plan->counter_gate_passed = counter_passed;
    plan->first_comparison_passed = first_passed;
    plan->mode4_comparison_passed = mode4_passed;
    plan->mode5_comparison_passed = mode5_passed;
    plan->publication_gate_passed = admitted;
    plan->target = admitted != 0U ? 0x00080650U : 0x000806f4U;
}
