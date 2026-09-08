/* Action-30 publication and threshold gate recovered from 0x7e834-0x7e864. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_geometry_action30_publication_7e834_plan {
    u32 classifier_index;
    u32 result_table;
    u32 result_value;
    u32 status_destination;
    u32 action_destination;
    u32 action_value;
    u32 global_509b34;
    u32 threshold;
    u32 enters_7e864;
    u32 continues_7e9f4;
};

void recovered_state_geometry_action30_publication_7e834(
    u32 classifier_index, u32 result_value, u32 global_509b34,
    struct recovered_state_geometry_action30_publication_7e834_plan *plan)
{
    plan->classifier_index = classifier_index;
    plan->result_table = 0x00072660U;
    plan->result_value = result_value;
    plan->status_destination = 0x00504d94U;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->global_509b34 = global_509b34;
    plan->threshold = 0x5dcU;
    plan->enters_7e864 = global_509b34 > plan->threshold ? 1U : 0U;
    plan->continues_7e9f4 = plan->enters_7e864 ? 0U : 1U;
}
