/* Fixed continuation-message renderer plan recovered from i960 0x1fa00. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_continued_renderer_plan {
    u32 message;
    u32 text_helper;
    u32 column;
    u32 row;
    u32 writes_position;
};

void recovered_continued_renderer_plan(u32 caller_g14,
                                      struct recovered_continued_renderer_plan *plan)
{
    plan->message = 0x0001f9e0U;
    plan->text_helper = 0x0001da90U;
    plan->column = caller_g14;
    plan->row = 20U;
    plan->writes_position = 1U;
}
