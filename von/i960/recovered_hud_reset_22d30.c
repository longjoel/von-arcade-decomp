/* HUD/reset route recovered from i960 0x22d30-0x22dc4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_hud_reset_plan {
    u32 fill_destination;
    u32 fill_group_count;
    u32 halfwords_per_group;
    u32 fill_value;
    u32 cleared_state_count;
    u32 cleared_state_address[4];
    u32 generator_mask;
    u32 generator_modulus;
    u32 generated_value;
    u32 stored_504d00;
    u32 uses_fallback_504d00;
};

void recovered_hud_reset_plan(u32 caller_r1, u32 generator_value,
                              u32 fallback_503a98,
                              struct recovered_hud_reset_plan *plan)
{
    plan->fill_destination = 0x0100c940U;
    plan->fill_group_count = caller_r1 + 31U;
    plan->halfwords_per_group = 4U;
    plan->fill_value = 0xffffU;
    plan->cleared_state_count = 4U;
    plan->cleared_state_address[0] = 0x00504d26U;
    plan->cleared_state_address[1] = 0x00504cfcU;
    plan->cleared_state_address[2] = 0x00504d08U;
    plan->cleared_state_address[3] = 0x00504d04U;
    plan->generator_mask = 0xfffU;
    plan->generator_modulus = 5U;
    plan->generated_value = (generator_value & plan->generator_mask) % 5U;
    /* cmpibl 3,g0 branches only when the reduced value is greater than 3. */
    plan->uses_fallback_504d00 = plan->generated_value > 3U ? 1U : 0U;
    plan->stored_504d00 = plan->uses_fallback_504d00
        ? fallback_503a98 + 4U : plan->generated_value;
}
