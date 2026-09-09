/* Geometry status emitter dispatcher recovered from i960 0xe7340-0xe738c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 input_mode;
    recovered_u32 normalized_mode;
    recovered_u32 target;
    recovered_u32 mode_address;
    recovered_u32 variant_a;
    recovered_u32 variant_b;
    recovered_u32 variant_c;
    recovered_u32 variant_d;
} recovered_geometry_status_emit_dispatch_result_e7340;

recovered_geometry_status_emit_dispatch_result_e7340
recovered_geometry_status_emit_dispatch_e7340(recovered_u32 mode)
{
    recovered_geometry_status_emit_dispatch_result_e7340 result;

    result.input_mode = mode;
    result.normalized_mode = mode <= 3U ? mode : 0U;
    result.target = 0x000e6d80U;
    if (result.normalized_mode == 1U)
        result.target = 0x000e6ef0U;
    else if (result.normalized_mode == 2U)
        result.target = 0x000e7060U;
    else if (result.normalized_mode == 3U)
        result.target = 0x000e71d0U;
    result.mode_address = 0x005783dcU;
    result.variant_a = 0x000e6d80U;
    result.variant_b = 0x000e6ef0U;
    result.variant_c = 0x000e7060U;
    result.variant_d = 0x000e71d0U;
    return result;
}
