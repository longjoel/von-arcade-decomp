/* State/timing dispatcher recovered from i960 0x83ac0-0x83cb8. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_dispatch_83ac0_route {
    RECOVERED_83AC0_EARLY_RETURN = 0,
    RECOVERED_83AC0_CALL_82800 = 1,
    RECOVERED_83AC0_STATE18 = 2,
    RECOVERED_83AC0_CALL_79D60 = 3,
    RECOVERED_83AC0_STATE28 = 4,
    RECOVERED_83AC0_STATE26 = 5,
    RECOVERED_83AC0_STATE21 = 6,
    RECOVERED_83AC0_STATE28_MODE = 7,
    RECOVERED_83AC0_STATE21_DEFAULT = 8,
    RECOVERED_83AC0_STATE5_TABLE_REJECT = 9
};

struct recovered_state_scheduler_dispatch_83ac0 {
    enum recovered_state_scheduler_dispatch_83ac0_route route;
    u32 terminal;
    u32 write_504d80;
    u32 value_504d80;
    u32 write_504d98;
    u32 value_504d98;
    u32 write_504e1c;
    u32 value_504d8c;
    u32 value_504d90;
};

struct recovered_state_scheduler_dispatch_83ac0
recovered_state_scheduler_dispatch_83ac0(int32_t value_504dc0,
                                         int32_t related_state,
                                         u32 state_504d7c,
                                         int32_t current_timing,
                                         int32_t converted_504df8,
                                         int32_t random_value,
                                         u32 mode_504e30,
                                         u32 caller_g14)
{
    struct recovered_state_scheduler_dispatch_83ac0 out = {
        RECOVERED_83AC0_EARLY_RETURN, 0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U
    };
    int32_t remainder;

    if (value_504dc0 <= 149
        && (related_state == 19 || related_state == 20)) {
        out.terminal = 1U;
        out.write_504d98 = 1U;
        out.value_504d98 = caller_g14;
        return out;
    }
    out.write_504e1c = 1U;
    if (current_timing < converted_504df8) {
        out.route = RECOVERED_83AC0_CALL_82800;
        out.write_504d80 = 1U;
        return out;
    }
    if (current_timing < 0) {
        out.route = RECOVERED_83AC0_STATE18;
        out.write_504d80 = 1U;
        out.value_504d80 = 18U;
        return out;
    }
    if (state_504d7c == 5U) {
        remainder = random_value % 6;
        if (remainder < 0 || remainder > 5) {
            out.route = RECOVERED_83AC0_STATE5_TABLE_REJECT;
            return out;
        }
        if (remainder <= 1) {
            out.route = RECOVERED_83AC0_CALL_79D60;
        } else if (remainder == 2 || remainder == 3) {
            out.route = RECOVERED_83AC0_STATE28;
            out.write_504d80 = 1U;
            out.value_504d80 = 28U;
        } else if (remainder == 4) {
            out.route = RECOVERED_83AC0_STATE26;
            out.write_504d80 = 1U;
            out.value_504d80 = 26U;
        } else {
            out.route = RECOVERED_83AC0_STATE21;
            out.write_504d80 = 1U;
            out.value_504d80 = 21U;
        }
        return out;
    }
    remainder = random_value % 7;
    /* cmpibge 4,g0 branches only for signed remainders >= 4; all lower
     * results, including negative remi-7 values, call 0x79d60. */
    if (remainder <= 4 && remainder != 4) {
        out.route = RECOVERED_83AC0_CALL_79D60;
    } else if (remainder == 4 && (mode_504e30 & 0x2U) != 0U) {
        out.route = RECOVERED_83AC0_STATE26;
        out.write_504d80 = 1U;
        out.value_504d80 = 26U;
    } else if (remainder > 0 && (mode_504e30 & 0x4U) != 0U) {
        out.route = RECOVERED_83AC0_STATE28_MODE;
        out.write_504d80 = 1U;
        out.value_504d80 = 28U;
    } else {
        out.route = RECOVERED_83AC0_STATE21_DEFAULT;
        out.write_504d80 = 1U;
        out.value_504d80 = 21U;
    }
    out.value_504d8c = caller_g14;
    out.value_504d90 = 15U;
    return out;
}
