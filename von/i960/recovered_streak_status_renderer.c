/* Streak-status route recovered from i960 0x20060. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_streak_route {
    RECOVERED_STREAK_MESSAGE = 0,
    RECOVERED_STREAK_CLEAR = 1,
    RECOVERED_STREAK_DIGITS = 2,
};

struct recovered_streak_plan {
    u32 route;
    u32 initial_column;
    u32 initial_row;
    u32 initial_clear_width;
    u32 initial_clear_height;
    u32 message;
    u32 message_helper;
    u32 digit_helper;
    u32 first_tile_source;
    u32 first_tile_column_from_g14;
    u32 first_tile_width;
    u32 first_tile_height;
    u32 second_tile_source;
    u32 second_tile_column_from_g27;
    u32 second_tile_width;
    u32 second_tile_height;
};

void recovered_streak_plan(int32_t value, u32 caller_g11, u32 caller_g14,
                           u32 caller_g27, struct recovered_streak_plan *plan)
{
    plan->initial_column = caller_g11 + 31U;
    plan->initial_row = caller_g11 + 31U;
    plan->initial_clear_width = 22U;
    plan->initial_clear_height = 2U;
    plan->message = 0x00020040U;
    plan->message_helper = 0x0001d1f0U;
    plan->digit_helper = 0x0001ff50U;
    plan->first_tile_source = 0x02fdfc00U;
    plan->first_tile_column_from_g14 = caller_g14 + 31U;
    plan->first_tile_width = 13U;
    plan->first_tile_height = 2U;
    plan->second_tile_source = 0x02fdfbfcU;
    plan->second_tile_column_from_g27 = caller_g27 + 31U;
    plan->second_tile_width = 1U;
    plan->second_tile_height = 2U;

    if (value <= 99) {
        plan->route = RECOVERED_STREAK_MESSAGE;
    } else if (value <= 1) {
        plan->route = RECOVERED_STREAK_CLEAR;
    } else {
        plan->route = RECOVERED_STREAK_DIGITS;
    }
}
