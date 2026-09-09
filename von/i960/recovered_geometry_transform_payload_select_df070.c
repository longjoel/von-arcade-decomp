/* Payload selection recovered from i960 0xdf070-0xdf120. */
#include "recovered_common.h"
#include "recovered_geometry_vector_select.h"

struct recovered_geometry_transform_payload_select_df070_input {
    recovered_u32 record_present;
    recovered_u32 record_class;
    recovered_u32 object_payload[3];
    recovered_u32 class_one_payload[3];
    recovered_u32 class_two_payload[3];
};

struct recovered_geometry_transform_payload_select_df070_plan {
    recovered_u32 selected_payload[3];
    recovered_u32 selected_class;
    recovered_u32 payload_selected;
};

void recovered_geometry_transform_payload_select_df070(
    const struct recovered_geometry_transform_payload_select_df070_input *input,
    struct recovered_geometry_transform_payload_select_df070_plan *plan)
{
    recovered_u32 selector;

    selector = input->record_class & 0xffffU;
    plan->selected_class = selector;
    plan->payload_selected = (input->record_present != 0U &&
                              (selector == 1U || selector == 2U)) ? 1U : 0U;

    if (input->record_present == 0U)
        return;
    recovered_geometry_select_vector((int32_t)selector, input->object_payload,
                                     input->class_one_payload,
                                     input->class_two_payload,
                                     plan->selected_payload);

}
