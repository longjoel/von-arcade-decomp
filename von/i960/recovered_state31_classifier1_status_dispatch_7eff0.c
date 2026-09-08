/* Classifier-1 status dispatch recovered from i960 0x7eff0-0x7f098. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_classifier1_status_dispatch_7eff0_plan {
    u32 classifier_result;
    u32 classifier_gate_passed;
    u32 original_status;
    u32 normalized_index;
    u32 table_target;
    u32 published_status;
    u32 common_callback_target;
    u32 callback_argument;
    u32 common_tail_target;
    u32 bypass_target;
};

void recovered_state31_classifier1_status_dispatch_7eff0(
    u32 classifier_result, u32 status_504d94, u32 related_pointer,
    struct recovered_state31_classifier1_status_dispatch_7eff0_plan *plan)
{
    static const u32 targets[12] = {
        0x0007f040U, 0x0007f068U, 0x0007f070U, 0x0007f080U,
        0x0007f08cU, 0x0007f08cU, 0x0007f08cU, 0x0007f08cU,
        0x0007f08cU, 0x0007f08cU, 0x0007f050U, 0x0007f058U
    };
    const u32 index = status_504d94 - 8U;
    u32 target = 0x0007f08cU;
    u32 published = status_504d94;

    if (index <= 11U) {
        target = targets[index];
        if (index == 0U)
            published = 1U;
        else if (index == 1U)
            published = 4U;
        else if (index == 2U)
            published = 5U;
        else if (index == 3U)
            published = 6U;
        else if (index == 10U)
            published = 2U;
        else if (index == 11U)
            published = 3U;
    }

    plan->classifier_result = classifier_result;
    plan->classifier_gate_passed = classifier_result == 1U ? 1U : 0U;
    plan->original_status = status_504d94;
    plan->normalized_index = index;
    plan->table_target = target;
    plan->published_status = published;
    plan->common_callback_target = 0x00079050U;
    plan->callback_argument = related_pointer;
    plan->common_tail_target = 0x0007f08cU;
    plan->bypass_target = classifier_result == 1U ? 0U : 0x0007f098U;
}
