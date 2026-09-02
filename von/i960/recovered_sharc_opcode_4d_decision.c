/* Proven terminal decision layer of SHARC opcode 0x4d at 0x20d02-0x20d4e. */
#include <math.h>

/* The result is written by the delayed output tails at 0x20d43/0x20d4d. */
unsigned int recovered_sharc_opcode_4d_decision(
    float dy, float radial, float refined_bound, float state3)
{
    /* The initial IF LT at 0x20d02 reaches the extra-input result-1 path. */
    if (dy < 0.0f)
        return 1U;

    /* 0x20d3d forms F1 = F9 + state[3]; IF LT is strict. */
    return radial < refined_bound + state3 ? 0U : 2U;
}
