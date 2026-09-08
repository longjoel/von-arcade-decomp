/* Bounded call-graph contract for the match/geometry route at 0x72c10. */

#include <stdint.h>

struct recovered_match_state_geometry_orchestrator_plan {
    uint32_t state_global;
    uint32_t mode_global;
    uint32_t divisor_global;
    uint32_t object_gate_offset;
    uint32_t modulo_base;
    uint32_t modulo_threshold;
    uint32_t call_targets[18];
    uint32_t call_count;
    uint32_t final_pair_address;
    uint32_t final_status_address;
    uint32_t continuation;
};

void recovered_match_state_geometry_orchestrator_plan(
    struct recovered_match_state_geometry_orchestrator_plan *plan)
{
    static const uint32_t calls[18] = {
        0x00076590U, 0x00077c40U, 0x000842d0U, 0x00074e60U,
        0x00082ae0U, 0x00085080U, 0x0007fca0U, 0x000807d0U,
        0x0007ea10U, 0x0007f4d0U, 0x000810d0U, 0x0007dcc0U,
        0x00086960U, 0x00075200U, 0x000735d0U, 0x00073498U,
        0x00076b00U, 0x00074860U
    };
    uint32_t index;

    plan->state_global = 0x00503a00U;
    plan->mode_global = 0x005039f4U;
    plan->divisor_global = 0x00504db4U;
    plan->object_gate_offset = 0x68U;
    plan->modulo_base = 30U;
    plan->modulo_threshold = 14U;
    plan->call_count = 18U;
    for (index = 0U; index < plan->call_count; ++index)
        plan->call_targets[index] = calls[index];
    plan->final_pair_address = 0x00504db0U;
    plan->final_status_address = 0x00504dacU;
    plan->continuation = 0x00072e94U;
}

uint32_t recovered_match_state_geometry_phase_bucket(uint32_t value)
{
    return value % 30U;
}
