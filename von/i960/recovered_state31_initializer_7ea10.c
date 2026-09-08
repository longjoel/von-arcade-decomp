/* State-31 initializer and threshold dispatch recovered from 0x7ea10. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_initializer_7ea10 {
    u32 accepted;
    u32 special_state31;
    u32 threshold_address;
    u32 status_504d9c;
    u32 value_504da0;
    u32 status_504d94;
    u32 status_504d98;
    u32 value_504db8;
};

/* Selector table at 0x7eab0: handler -> threshold word address. */
static const u32 threshold_addresses[8] = {
    0x504e3cU, 0x504e40U, 0x504e3cU, 0x504e3eU,
    0x504e40U, 0x504e3cU, 0x504e40U, 0x504e40U
};

struct recovered_state31_initializer_7ea10
recovered_state31_initializer_7ea10(
    int32_t state_counter_509b30, uint16_t related_172,
    u32 object_state, u32 related_state, u32 mode_504e48,
    u32 selector_504e4c, const uint16_t thresholds[3])
{
    struct recovered_state31_initializer_7ea10 out = {
        0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U
    };
    const u32 value = (u32)related_172;

    if (state_counter_509b30 <= 0x1f3)
        return out;
    if (related_172 == 31U) {
        if (object_state != 6U || related_state != 6U ||
            mode_504e48 != 3U)
            return out;
        out.accepted = 1U;
        out.special_state31 = 1U;
        out.status_504d9c = 3U;
        out.value_504da0 = 0x64U;
        out.status_504d94 = 1U;
        out.status_504d98 = 7U;
        out.value_504db8 = 30U;
        return out;
    }
    if (selector_504e4c >= 8U)
        return out;
    out.threshold_address = threshold_addresses[selector_504e4c];
    if (value > thresholds[selector_504e4c == 3U ? 2U :
                             (selector_504e4c == 1U ||
                              selector_504e4c == 4U ||
                              selector_504e4c == 6U ||
                              selector_504e4c == 7U ? 1U : 0U)])
        return out;
    out.accepted = 1U;
    return out;
}
