/* Ratio-duel predicate recovered from i960 0x7a438 and 0x7a4a8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_ratio_duel_plan {
    float obj_ratio;
    float peer_ratio;
    u32 flag_live;
    u32 wins;
    u32 win_mode;
    u32 win_callee;
};

void recovered_ratio_duel_plan(int halfwords[4], u32 flag, u32 win_mode,
                               u32 win_callee,
                               struct recovered_ratio_duel_plan *plan)
{
    /* Both arms sign-extend the four halfwords (obj +0x1d0/+0x1d8, then
     * peer +0x1d0/+0x1d8), convert with cvtir, and divide src2/src1, so
     * each side is first/second. cmpr/bge skips the win unless the
     * object ratio is strictly below the peer ratio. */
    plan->obj_ratio = (float)halfwords[0] / (float)halfwords[1];
    plan->peer_ratio = (float)halfwords[2] / (float)halfwords[3];
    plan->flag_live = flag == 1U ? 1U : 0U;
    plan->wins = (plan->flag_live
        && plan->obj_ratio < plan->peer_ratio) ? 1U : 0U;
    plan->win_mode = win_mode;
    plan->win_callee = win_callee;
}
