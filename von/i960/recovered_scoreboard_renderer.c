/* Two-value scoreboard route recovered from i960 0x1fc30. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scoreboard_digit_plan {
    u32 source;
    u32 helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
    u32 table_index;
};

struct recovered_scoreboard_plan {
    u32 early_return;
    u32 normalized_first;
    u32 normalized_second;
    struct recovered_scoreboard_digit_plan first_tens;
    struct recovered_scoreboard_digit_plan first_units;
    struct recovered_scoreboard_digit_plan second_tens;
    struct recovered_scoreboard_digit_plan second_units;
    struct recovered_scoreboard_digit_plan first_separator;
    struct recovered_scoreboard_digit_plan second_suffix;
};

static u32 recovered_scoreboard_normalize(u32 value)
{
    return (value & 0x8000U) != 0U ? 0U : value;
}

static void recovered_scoreboard_digit(struct recovered_scoreboard_digit_plan *digit,
                                       u32 column, u32 row, u32 index,
                                       u32 helper)
{
    digit->source = 0x02ea1e50U + index * 4U;
    digit->helper = helper;
    digit->column = column;
    digit->row = row;
    digit->width = 2U;
    digit->height = 2U;
    digit->table_index = index;
}

void recovered_scoreboard_plan(u32 first, u32 second, u32 state, u32 mode,
                               struct recovered_scoreboard_plan *plan)
{
    u32 first_value = recovered_scoreboard_normalize(first);
    u32 second_value = recovered_scoreboard_normalize(second);
    u32 first_low = first_value & 0xffffU;
    u32 second_low = second_value & 0xffffU;

    plan->early_return = state == 0U && mode == 4U;
    plan->normalized_first = first_value;
    plan->normalized_second = second_value;

    recovered_scoreboard_digit(&plan->first_tens, 25U, 21U,
                               (first_low / 10U) & 15U, 0x1dc10U);
    recovered_scoreboard_digit(&plan->first_units, 27U, 21U,
                               first_low % 10U, 0x1dc90U);
    plan->first_separator = (struct recovered_scoreboard_digit_plan){
        0x02fe158aU, 0x1dc10U, 29U, 22U, 1U, 1U, 0U
    };
    recovered_scoreboard_digit(&plan->second_tens, 30U, 21U,
                               (second_low / 10U) & 15U, 0x1dc10U);
    recovered_scoreboard_digit(&plan->second_units, 32U, 21U,
                               second_low % 10U, 0x1dc90U);
    plan->second_suffix = (struct recovered_scoreboard_digit_plan){
        0x02fe157aU, 0x1dc10U, 34U, 21U, 4U, 2U, 0U
    };
}
