/* Bounded entry prefix for match geometry range update at 0x75200. */

#include <stdint.h>

struct recovered_match_geometry_range_update_plan {
    uint32_t object_pointer_preserved_register;
    uint32_t object_link_offset;
    uint32_t frame_base_offset;
    uint32_t geometry_helper;
    uint32_t linked_record_offset;
    uint32_t classifier;
    uint32_t first_result_register;
    uint32_t zero_return;
    uint32_t nonzero_continuation;
};

void recovered_match_geometry_range_update_75200_plan(
    struct recovered_match_geometry_range_update_plan *plan)
{
    plan->object_pointer_preserved_register = 6U; /* r6 */
    plan->object_link_offset = 0x74U;
    plan->frame_base_offset = 0x40U;
    plan->geometry_helper = 0x00077470U;
    plan->linked_record_offset = 0x184U;
    plan->classifier = 0x00073508U;
    plan->first_result_register = 5U; /* r5 */
    plan->zero_return = 0x0007522cU;
    plan->nonzero_continuation = 0x00075230U;
}

uint32_t recovered_match_geometry_range_zero_result(uint32_t first_result)
{
    return first_result == 0U ? 1U : 0U;
}
