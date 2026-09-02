/* Record/dispatch contract recovered from i960 0x211f0-0x2123c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_weapon_record_dispatch {
    u32 record_address;
    u32 asset_pointer;
    u32 handler;
};

void recovered_weapon_record_dispatch_plan(u32 selector,
                                           struct recovered_weapon_record_dispatch *plan)
{
    static const u32 assets[10] = {
        0x02fe7554U, 0x02fe7dceU, 0x02fe4af2U, 0x02fe6cdaU,
        0x02fe536cU, 0x02fe5be6U, 0x02fe39feU, 0x02fe4278U,
        0x02fe6460U, 0x02fe8648U
    };
    static const u32 handlers[9] = {
        0x00021240U, 0x00021314U, 0x000214bcU, 0x00021784U,
        0x000213e8U, 0x000216a0U, 0x00021674U, 0x00021580U,
        0x000218a0U
    };

    u32 index = selector < 10U ? selector : 9U;
    plan->record_address = 0x00020b50U + index * 0x68U;
    plan->asset_pointer = assets[index];
    plan->handler = selector < 8U ? handlers[selector] : 0x000218a0U;
}
