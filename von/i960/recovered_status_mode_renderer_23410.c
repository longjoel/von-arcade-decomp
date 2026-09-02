/* Stateful status-mode renderer recovered from i960 0x23410-0x23504. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_mode_renderer_plan {
    u32 eligible;
    u32 draws_block;
    u32 mode;
    u32 mode_table;
    u32 helper;
    u32 source_table;
    u32 source_table_selector;
    u32 source_table_entry;
    u32 source_table_index;
    u32 width;
    u32 height;
    u32 column;
    u32 row;
    u32 next_generator_state;
    u32 next_status_state;
    u32 generator_modulus;
};

void recovered_status_mode_renderer_plan(
    u32 gate_503a7c, u32 mode, u32 status_504d26,
    u32 state_504d00, u32 state_504cfc, u32 generator_modulus,
    struct recovered_status_mode_renderer_plan *plan)
{
    u32 status_low16 = status_504d26 & 0xffffU;
    u32 selector = state_504d00 & 15U;
    u32 accepted = mode <= 4U || mode == 7U || mode == 9U;

    plan->eligible = gate_503a7c == 0U && accepted ? 1U : 0U;
    plan->draws_block = plan->eligible && (status_504d26 & 15U) == 0U
        ? 1U : 0U;
    plan->mode = mode;
    plan->mode_table = 0x005770f0U;
    plan->helper = 0x0001dd80U;
    plan->source_table = 0x02ea289cU;
    plan->source_table_selector = selector;
    plan->source_table_entry = 0x02ea289cU + selector * 8U;
    plan->source_table_index = state_504cfc;
    plan->width = plan->draws_block ? 2U : 0U;
    plan->height = plan->draws_block ? 4U : 0U;
    plan->column = plan->draws_block
        ? (62U - (status_low16 >> 3)) & 63U : 0U;
    plan->row = plan->draws_block ? 31U + state_504cfc : 0U;
    plan->generator_modulus = generator_modulus;
    plan->next_generator_state = plan->eligible && generator_modulus != 0U
        ? (state_504cfc + 1U) % generator_modulus : state_504cfc;
    plan->next_status_state = plan->eligible
        ? (status_504d26 - 2U) & 0x1ffU : status_504d26;
}
