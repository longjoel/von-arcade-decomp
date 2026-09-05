/* Fixed init schedule recovered from i960 0x34c0-0x3534. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_init_op_kind {
    RECOVERED_INIT_STORE8 = 1U,
    RECOVERED_INIT_STORE16 = 2U,
    RECOVERED_INIT_STORE32 = 4U,
    RECOVERED_INIT_CALL = 0U
};

struct recovered_init_op {
    u32 kind;
    u32 address;
};

static const struct recovered_init_op recovered_init_ops[] = {
    { RECOVERED_INIT_STORE8, 0x005024cdU },
    { RECOVERED_INIT_STORE8, 0x005024ccU },
    { RECOVERED_INIT_STORE16, 0x005024ceU },
    { RECOVERED_INIT_STORE8, 0x005024d1U },
    { RECOVERED_INIT_STORE8, 0x005024d0U },
    { RECOVERED_INIT_STORE16, 0x005024d2U },
    { RECOVERED_INIT_STORE16, 0x005024c0U },
    { RECOVERED_INIT_STORE16, 0x005024c2U },
    { RECOVERED_INIT_CALL, 0x000022f0U },
    { RECOVERED_INIT_CALL, 0x00002330U },
    { RECOVERED_INIT_STORE16, 0x005023f2U },
    { RECOVERED_INIT_STORE16, 0x005024c4U },
    { RECOVERED_INIT_STORE16, 0x005024c6U },
    { RECOVERED_INIT_STORE16, 0x005024c8U },
    { RECOVERED_INIT_STORE32, 0x005023e4U }
};

u32 recovered_init_op_count(void)
{
    return (u32)(sizeof(recovered_init_ops)
        / sizeof(recovered_init_ops[0]));
}

void recovered_init_op_at(u32 index, struct recovered_init_op *op)
{
    if (index < recovered_init_op_count())
        *op = recovered_init_ops[index];
    else {
        op->kind = 0U;
        op->address = 0U;
    }
}
