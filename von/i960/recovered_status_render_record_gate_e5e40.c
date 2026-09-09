/* Status-render record gate recovered from i960 0xe5e40-0xe5e60. */
#include <stdint.h>

typedef uint32_t recovered_u32;

enum recovered_status_render_record_route_e5e40 {
    RECOVERED_STATUS_RENDER_FALLBACK_STRING = 0,
    RECOVERED_STATUS_RENDER_NUMERIC = 1
};

typedef struct {
    recovered_u32 record_word_plus4;
    recovered_u32 route;
    recovered_u32 selected_helper;
    recovered_u32 selected_asset;
    recovered_u32 record_base;
    recovered_u32 record_offset;
} recovered_status_render_record_gate_result_e5e40;

recovered_status_render_record_gate_result_e5e40
recovered_status_render_record_gate_e5e40(recovered_u32 record_word_plus4)
{
    recovered_status_render_record_gate_result_e5e40 result = {
        record_word_plus4,
        RECOVERED_STATUS_RENDER_NUMERIC,
        0x000e3a10U,
        0U,
        0x00578410U,
        4U
    };

    if (record_word_plus4 == 0xffffffffU) {
        result.route = RECOVERED_STATUS_RENDER_FALLBACK_STRING;
        result.selected_helper = 0x000e3a00U;
        result.selected_asset = 0x000e3b50U;
    }
    return result;
}
