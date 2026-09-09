/* Fallback object admission recovered from i960 0xe76d0-0xe7850. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 object_tag_byte;
    recovered_u32 caller_tag_byte;
    recovered_u32 tags_match;
    recovered_u32 special_caller_tag;
    recovered_u32 special_match;
    recovered_u32 helper_target;
    recovered_u32 route;
    recovered_u32 accepted_target;
    recovered_u32 rejected_target;
    recovered_u32 emitter_dispatch_target;
    recovered_u32 direct_packet_target;
} recovered_geometry_object_fallback_admission_result_e76d0;

enum recovered_geometry_object_fallback_admission_route_e76d0 {
    RECOVERED_GEOMETRY_OBJECT_FALLBACK_REJECT = 0,
    RECOVERED_GEOMETRY_OBJECT_FALLBACK_EMITTER = 2,
    RECOVERED_GEOMETRY_OBJECT_FALLBACK_DIRECT = 3
};

recovered_geometry_object_fallback_admission_result_e76d0
recovered_geometry_object_fallback_admission_e76d0(recovered_u32 object_tag,
                                                   recovered_u32 caller_tag,
                                                   recovered_u32 queue_flag)
{
    recovered_geometry_object_fallback_admission_result_e76d0 result;

    result.object_tag_byte = object_tag & 0xffU;
    result.caller_tag_byte = caller_tag & 0xffU;
    result.tags_match = result.object_tag_byte == result.caller_tag_byte;
    result.special_caller_tag = 62U;
    result.special_match = result.caller_tag_byte == 62U;
    result.helper_target = 0x000f50c8U;
    result.accepted_target = 0x000e76fcU;
    result.rejected_target = 0x000e7850U;
    result.emitter_dispatch_target = 0x000e7340U;
    result.direct_packet_target = 0x000e7874U;
    if (!(result.tags_match || result.special_match))
        result.route = RECOVERED_GEOMETRY_OBJECT_FALLBACK_REJECT;
    else if (queue_flag == 0U)
        result.route = RECOVERED_GEOMETRY_OBJECT_FALLBACK_EMITTER;
    else
        result.route = RECOVERED_GEOMETRY_OBJECT_FALLBACK_DIRECT;
    return result;
}
