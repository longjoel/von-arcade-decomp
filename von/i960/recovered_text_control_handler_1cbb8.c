/* TAB/LF control handler recovered from i960 0x1cbb8-0x1cc38. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_text_control_state_1cbb8 {
    u32 column;
    u32 row;
    u32 state_changed;
};

void recovered_text_control_handler_1cbb8(
    u32 character, u32 origin_column, u32 column, u32 row,
    struct recovered_text_control_state_1cbb8 *out)
{
    out->column = column;
    out->row = row;
    out->state_changed = 0U;
    if (character == 9U) {
        out->column = (column + 8U) & ~7U;
        if (out->column > 61U) {
            out->column = 0U;
            if (row <= 46U)
                out->row = row + 1U;
        }
        out->state_changed = 1U;
    } else if (character == 10U) {
        out->column = origin_column;
        if (row <= 46U)
            out->row = row + 1U;
        out->state_changed = 1U;
    }
}
