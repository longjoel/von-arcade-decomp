/* Window-clear schedule recovered from i960 0x1c618-0x1cf0.
 *
 * The routine saves the caller link, clears its own link register,
 * zeroes eight halfword service slots (0x504d24-0x504d32) plus two
 * word slots (0x504d34, 0x504d38), then blank-fills four halfword
 * device windows with the cleared value: 16384 at 0x1000000, 4096 at
 * 0x100c000, 2048 at 0x1008000, and 8 at 0x100a000. Each countdown
 * loop (setbit count, subo, stos, cmpi, bg) performs exactly its
 * setbit count of stores before the greater-than test fails at zero.
 * Return goes one-way through the saved link. Every effect is
 * constant, so the plan takes no inputs.
 */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_window_clear_run {
    u32 base;
    u32 halfwords;
};

struct recovered_window_clear_plan {
    u32 half_slot_base;
    u32 half_slots;
    u32 word_slot_base;
    u32 word_slots;
    struct recovered_window_clear_run fills[4];
    u32 total_halfwords;
};

void recovered_window_clear_plan(struct recovered_window_clear_plan *plan)
{
    plan->half_slot_base = 0x00504d24U;
    plan->half_slots = 8U;
    plan->word_slot_base = 0x00504d34U;
    plan->word_slots = 2U;
    plan->fills[0].base = 0x01000000U;
    plan->fills[0].halfwords = 16384U;
    plan->fills[1].base = 0x0100c000U;
    plan->fills[1].halfwords = 4096U;
    plan->fills[2].base = 0x01008000U;
    plan->fills[2].halfwords = 2048U;
    plan->fills[3].base = 0x0100a000U;
    plan->fills[3].halfwords = 8U;
    plan->total_halfwords = plan->half_slots + 16384U + 4096U + 2048U + 8U;
}
