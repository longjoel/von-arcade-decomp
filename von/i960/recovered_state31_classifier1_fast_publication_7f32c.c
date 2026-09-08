/* Classifier-result-1 fast publication recovered from i960 0x7f32c-0x7f364. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_classifier1_fast_publication_7f32c_plan {
    u32 classifier_result;
    u32 r6_compare_equal_zero;
    u32 classifier_gate_passed;
    u32 selector_written;
    u32 selector_destination;
    u32 selector_value;
    u32 control_written;
    u32 control_destination;
    u32 control_value;
    u32 target;
    u32 alternate_target;
    u32 failure_target;
};

void recovered_state31_classifier1_fast_publication_7f32c(
    u32 classifier_result, u32 r6_compare_equal_zero,
    struct recovered_state31_classifier1_fast_publication_7f32c_plan *plan)
{
    const u32 classifier_passed = classifier_result == 1U ? 1U : 0U;
    const u32 compare_equal = r6_compare_equal_zero ? 1U : 0U;
    const u32 fast_return = classifier_passed && compare_equal;

    plan->classifier_result = classifier_result;
    plan->r6_compare_equal_zero = compare_equal;
    plan->classifier_gate_passed = classifier_passed;
    plan->selector_written = classifier_passed;
    plan->selector_destination = classifier_passed ? 0x00504d9cU : 0U;
    plan->selector_value = classifier_passed ? 3U : 0U;
    plan->control_written = fast_return;
    plan->control_destination = fast_return ? 0x00504da0U : 0U;
    plan->control_value = fast_return ? 0x64U : 0U;
    plan->target = fast_return ? 0x0007f360U :
                   (classifier_passed ? 0x0007f364U : 0x0007f44cU);
    plan->alternate_target = 0x0007f364U;
    plan->failure_target = 0x0007f44cU;
}
