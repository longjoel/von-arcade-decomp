/* Simple follow-up handlers recovered from i960 0x7dba8-0x7dc04. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_simple_handler_7dba8_plan {
    u32 writes_selector;
    u32 selector_value;
    u32 writes_status;
    u32 status_value;
    u32 recognized;
};

void recovered_state_followup_simple_handler_7dba8(
    u32 target, struct recovered_state_followup_simple_handler_7dba8_plan *plan)
{
    plan->writes_selector = 0U;
    plan->selector_value = 0U;
    plan->writes_status = 0U;
    plan->status_value = 0U;
    plan->recognized = 1U;

    switch (target) {
    case 0x0007dba8U:
    case 0x0007dbb8U:
        plan->writes_selector = 1U;
        plan->selector_value = 19U;
        break;
    case 0x0007dbc8U:
        plan->writes_selector = 1U;
        plan->selector_value = 20U;
        break;
    case 0x0007dbd8U:
        plan->writes_selector = 1U;
        plan->selector_value = 23U;
        plan->writes_status = 1U;
        plan->status_value = 28U;
        break;
    case 0x0007dbf4U:
        plan->writes_selector = 1U;
        plan->selector_value = 21U;
        break;
    default:
        plan->recognized = 0U;
        break;
    }
}
