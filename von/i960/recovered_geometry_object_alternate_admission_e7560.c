/* Alternate object packet admission recovered from i960 0xe7560-0xe758c. */
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
} recovered_geometry_object_alternate_admission_result_e7560;

enum recovered_geometry_object_alternate_admission_route_e7560 {
    RECOVERED_GEOMETRY_OBJECT_ALTERNATE_REJECT = 0,
    RECOVERED_GEOMETRY_OBJECT_ALTERNATE_ACCEPT = 1
};

recovered_geometry_object_alternate_admission_result_e7560
recovered_geometry_object_alternate_admission_e7560(recovered_u32 object_tag,
                                                    recovered_u32 caller_tag)
{
    recovered_geometry_object_alternate_admission_result_e7560 result;

    result.object_tag_byte = object_tag & 0xffU;
    result.caller_tag_byte = caller_tag & 0xffU;
    result.tags_match = result.object_tag_byte == result.caller_tag_byte;
    result.special_caller_tag = 60U;
    result.special_match = result.caller_tag_byte == 60U;
    result.helper_target = 0x000f50c8U;
    result.route = (result.tags_match || result.special_match) ?
        RECOVERED_GEOMETRY_OBJECT_ALTERNATE_ACCEPT :
        RECOVERED_GEOMETRY_OBJECT_ALTERNATE_REJECT;
    result.accepted_target = 0x000e758cU;
    result.rejected_target = 0x000e76d0U;
    return result;
}
