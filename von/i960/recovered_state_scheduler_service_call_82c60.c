/* Scheduler service handoff recovered from i960 0x82c60-0x82c6c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_service_call_82c60 {
    u32 argument;
    u32 target;
    u32 tail_target;
};

struct recovered_state_scheduler_service_call_82c60
recovered_state_scheduler_service_call_82c60(u32 object_pointer)
{
    struct recovered_state_scheduler_service_call_82c60 out = {
        object_pointer, 0x000840b0U, 0x00082d74U
    };
    return out;
}
