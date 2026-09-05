/* Upload state initializer recovered from i960 0x29d2c-0x29d48. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_upload_state_init_plan {
    u32 value_addr;
    u32 mode_addr;
    u32 counter_addr;
    u32 value_stored;
    u32 mode_stored;
    s32 counter_stored;
    s32 uploader_active;
};

void recovered_upload_state_init_plan(u32 link,
                                       struct recovered_upload_state_init_plan *plan)
{
    plan->value_addr = 0x0051a260U;
    plan->mode_addr = 0x0051a268U;
    plan->counter_addr = 0x0051a264U;
    /* The tail stores the caller link (g14) to the value and mode slots
     * and presets the counter to 4. */
    plan->value_stored = link;
    plan->mode_stored = link;
    plan->counter_stored = 4;
    /* The 0x29d50 guard needs a counter of at least 3, so the preset
     * leaves the uploader active on its first call. */
    plan->uploader_active = plan->counter_stored >= 3 ? 1 : 0;
}
