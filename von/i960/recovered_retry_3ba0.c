/* Retry controller recovered from i960 0x3ba0-0x3c38. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_retry_plan {
    u32 outcome;
    u32 calls_copy;
    u32 copy_adjust;
    u32 service_arg;
    u32 calls_service;
};

void recovered_retry_plan(s32 counter, u32 limit, u32 mode_byte,
                          u32 flag_byte,
                          struct recovered_retry_plan *plan)
{
    u32 stepped = (u32)(counter + 1);
    u32 use_check;

    /* cmpobl compares literal-order unsigned: the check path runs when
     * the limit does not exceed the stepped counter. */
    if (limit > stepped) {
        /* A nonzero mode byte rejoins the check path; zero advances. */
        use_check = mode_byte != 0U ? 1U : 0U;
    } else {
        use_check = 1U;
    }
    if (use_check) {
        /* The check path returns early unless the mode byte is set and
         * the flag carries bit 4. */
        if (mode_byte == 0U || (flag_byte & 0x10U) == 0U) {
            plan->outcome = 0U;
            plan->calls_copy = 0U;
            plan->copy_adjust = 0U;
            plan->service_arg = 0U;
            plan->calls_service = 0U;
            return;
        }
    }
    plan->outcome = 1U;
    /* Only a zero mode byte rewinds the limit through 0x2330 first. */
    plan->calls_copy = mode_byte == 0U ? 1U : 0U;
    plan->copy_adjust = plan->calls_copy ? limit - stepped : 0U;
    plan->service_arg = 0x111cU;
    plan->calls_service = 1U;
}
