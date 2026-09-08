/*
 * Instruction-locked routing recovered from i960 0x79d60-0x7a218.
 *
 * This deliberately models only the parts that do not depend on the
 * unresolved state-arm predicates: the ten-entry jump table at 0x79d8c and
 * the common exits which publish transitions 13, 14, and 15.
 */
#include <stdint.h>

enum {
    RECOVERED_SECONDARY_NO_ROUTE = UINT32_MAX,
    RECOVERED_SECONDARY_STATE_TABLE = 0x00079d8c,
    RECOVERED_SECONDARY_EXIT_15 = 0x0007a1e4,
    RECOVERED_SECONDARY_EXIT_14 = 0x0007a11c,
    RECOVERED_SECONDARY_EXIT_13 = 0x0007a1f4,
    RECOVERED_SECONDARY_EXIT_13_DIRECT = 0x0007a204,
    RECOVERED_SECONDARY_RETURN = 0x0007a214,
};

uint32_t recovered_secondary_dispatch_target_79d60(uint32_t object_state)
{
    static const uint32_t targets[10] = {
        0x00079db4, 0x00079e10, 0x00079e8c, 0x00079ef4,
        0x00079f5c, 0x00079ff4, 0x0007a098, 0x0007a150,
        0x0007a204, 0x0007a214,
    };

    return object_state < 10U ? targets[object_state]
                              : RECOVERED_SECONDARY_NO_ROUTE;
}

uint32_t recovered_secondary_shared_transition_79d60(uint32_t exit_address)
{
    switch (exit_address) {
    case RECOVERED_SECONDARY_EXIT_15:
        return 15U;
    case RECOVERED_SECONDARY_EXIT_14:
        return 14U;
    case RECOVERED_SECONDARY_EXIT_13:
    case RECOVERED_SECONDARY_EXIT_13_DIRECT:
        return 13U;
    default:
        return RECOVERED_SECONDARY_NO_ROUTE;
    }
}

uint32_t recovered_secondary_dispatch_table_address_79d60(void)
{
    return RECOVERED_SECONDARY_STATE_TABLE;
}
