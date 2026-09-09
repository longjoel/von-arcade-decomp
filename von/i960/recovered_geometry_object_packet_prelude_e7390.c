/* Object packet admission prelude recovered from i960 0xe7390-0xe7420. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 object_tag_byte;
    recovered_u32 caller_tag_byte;
    recovered_u32 tags_match;
    recovered_u32 queue_flag;
    recovered_u32 route;
    recovered_u32 mismatch_target;
    recovered_u32 emitter_dispatch_target;
    recovered_u32 direct_packet_target;
} recovered_geometry_object_packet_prelude_result_e7390;

enum recovered_geometry_object_packet_prelude_route_e7390 {
    RECOVERED_GEOMETRY_OBJECT_PACKET_MISMATCH = 0,
    RECOVERED_GEOMETRY_OBJECT_PACKET_EMITTER = 1,
    RECOVERED_GEOMETRY_OBJECT_PACKET_DIRECT = 2
};

recovered_geometry_object_packet_prelude_result_e7390
recovered_geometry_object_packet_prelude_e7390(recovered_u32 object_tag,
                                               recovered_u32 caller_tag,
                                               recovered_u32 queue_flag)
{
    recovered_geometry_object_packet_prelude_result_e7390 result;

    result.object_tag_byte = object_tag & 0xffU;
    result.caller_tag_byte = caller_tag & 0xffU;
    result.tags_match = result.object_tag_byte == result.caller_tag_byte;
    result.queue_flag = queue_flag;
    result.mismatch_target = 0x000e7560U;
    result.emitter_dispatch_target = 0x000e7340U;
    result.direct_packet_target = 0x000e7420U;
    if (!result.tags_match)
        result.route = RECOVERED_GEOMETRY_OBJECT_PACKET_MISMATCH;
    else if (queue_flag == 0U)
        result.route = RECOVERED_GEOMETRY_OBJECT_PACKET_EMITTER;
    else
        result.route = RECOVERED_GEOMETRY_OBJECT_PACKET_DIRECT;
    return result;
}
