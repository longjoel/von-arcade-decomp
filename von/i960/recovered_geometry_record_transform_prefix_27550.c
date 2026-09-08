/* Geometry record-transform constructor prefix recovered from 0x27550-0x2766c. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_transform_profile_route_27550 {
    RECOVERED_TRANSFORM_PROFILE_NONE = 0,
    RECOVERED_TRANSFORM_PROFILE_274A0 = 1,
    RECOVERED_TRANSFORM_PROFILE_26D60 = 2,
    RECOVERED_TRANSFORM_PROFILE_273F0 = 3,
    RECOVERED_TRANSFORM_PROFILE_273D0 = 4,
    RECOVERED_TRANSFORM_PROFILE_27130 = 5,
};

struct recovered_geometry_record_transform_prefix_27550 {
    u32 record_zero_fields;
    u32 record_one_field;
    u32 reset_transform_fields;
    u32 profile_route;
    u32 selected_profile_pointer;
    u32 profile_helper_called;
    u32 stage_selector_called;
    u32 producer_called;
};

void recovered_geometry_record_transform_prefix_27550(
    u32 mode, u32 record_kind,
    struct recovered_geometry_record_transform_prefix_27550 *out)
{
    out->record_zero_fields = 1U;
    out->record_one_field = 1U;
    out->reset_transform_fields = 1U;
    out->profile_helper_called = 0U;
    out->selected_profile_pointer = 0U;

    if (mode == 1U) {
        out->profile_route = record_kind == 9U
            ? RECOVERED_TRANSFORM_PROFILE_274A0
            : RECOVERED_TRANSFORM_PROFILE_273F0;
    } else if (mode == 0U) {
        out->profile_route = record_kind == 9U
            ? RECOVERED_TRANSFORM_PROFILE_274A0
            : RECOVERED_TRANSFORM_PROFILE_26D60;
    } else if (mode == 3U) {
        out->profile_route = RECOVERED_TRANSFORM_PROFILE_27130;
    } else if (mode == 4U) {
        out->profile_route = RECOVERED_TRANSFORM_PROFILE_273D0;
    } else {
        out->profile_route = RECOVERED_TRANSFORM_PROFILE_NONE;
    }
    switch (out->profile_route) {
    case RECOVERED_TRANSFORM_PROFILE_274A0:
        out->selected_profile_pointer = 0x000274a0U;
        out->profile_helper_called = 1U;
        break;
    case RECOVERED_TRANSFORM_PROFILE_26D60:
        out->selected_profile_pointer = 0x00026d60U;
        break;
    case RECOVERED_TRANSFORM_PROFILE_273F0:
        out->selected_profile_pointer = 0x000273f0U;
        break;
    case RECOVERED_TRANSFORM_PROFILE_273D0:
        out->selected_profile_pointer = 0x000273d0U;
        break;
    case RECOVERED_TRANSFORM_PROFILE_27130:
        out->selected_profile_pointer = 0x00027130U;
        break;
    default:
        break;
    }
    out->stage_selector_called = 1U;
    out->producer_called = 1U;
}
