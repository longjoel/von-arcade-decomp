/* ABI-visible continuation thunk recovered from i960 0x18910-0x18928. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_return_thunk_18918 {
    u32 continuation;
    u32 return_value;
    u32 g14_cleared;
};

void recovered_startup_return_thunk_18918(
    u32 caller_continuation,
    struct recovered_startup_return_thunk_18918 *out)
{
    /* The thunk moves its private g14 continuation through g1, clears g14,
     * and returns zero through the caller's continuation. */
    out->continuation = caller_continuation;
    out->return_value = 0U;
    out->g14_cleared = 1U;
}
