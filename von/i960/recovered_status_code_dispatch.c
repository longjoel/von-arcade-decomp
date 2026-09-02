/* Status-code dispatcher and case table recovered from i960 0x1f710. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_code_block {
    u32 helper;
    u32 source;
    u32 width;
    u32 height;
};

struct recovered_status_code_dispatch_plan {
    struct recovered_status_code_block blanking_block;
    struct recovered_status_code_block selected_block;
    u32 selected_message;
    u32 selected_case;
    u32 text_column;
    u32 text_row;
};

void recovered_status_code_dispatch_plan(u32 selector, u32 caller_g3,
                                         u32 caller_g4, u32 caller_g5,
                                         u32 caller_g7,
                                         struct recovered_status_code_dispatch_plan *plan)
{
    plan->blanking_block.helper = 0x0001df00U;
    plan->blanking_block.source = 0U;
    plan->blanking_block.width = caller_g7 + 31U;
    plan->blanking_block.height = 3U;
    plan->text_column = 8U;
    plan->text_row = 14U;

    plan->selected_case = selector <= 7U ? selector : 8U;
    plan->selected_message = 0x0001f680U + (plan->selected_case << 4);
    plan->selected_block.helper = 0x0001df00U;
    plan->selected_block.source = 0U;
    plan->selected_block.width = caller_g7 + 31U;
    plan->selected_block.height = 3U;

    switch (plan->selected_case) {
    case 0U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe321cU;
        plan->selected_block.width = 30U;
        break;
    case 1U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe350eU;
        plan->selected_block.width = caller_g5 + 31U;
        break;
    case 2U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe35e6U;
        plan->selected_block.width = caller_g5 + 31U;
        break;
    case 3U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe343cU;
        plan->selected_block.width = caller_g4 + 31U;
        break;
    case 4U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe37faU;
        plan->selected_block.width = 31U;
        break;
    case 5U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe33b4U;
        plan->selected_block.width = caller_g3 + 31U;
        plan->selected_block.height = 2U;
        break;
    case 6U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe32d0U;
        plan->selected_block.width = caller_g7 + 31U;
        break;
    case 7U:
        plan->selected_block.helper = 0x0001dc90U;
        plan->selected_block.source = 0x02fe3746U;
        plan->selected_block.width = 30U;
        break;
    default:
        break;
    }
}
