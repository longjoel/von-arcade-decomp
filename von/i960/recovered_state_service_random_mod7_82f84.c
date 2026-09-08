/* Random remainder producer recovered from i960 0x82f84-0x82f8c. */

#include <stdint.h>

typedef uint32_t u32;

/* remi 7 produces the signed remainder used as the shared 0x82fac selector. */
int32_t recovered_state_service_random_mod7_82f84(int32_t random_value)
{
    return random_value % 7;
}

/* Keep the bit-pattern view available to callers that pass raw i960 words. */
u32 recovered_state_service_random_mod7_82f84_bits(u32 random_value)
{
    return (u32)recovered_state_service_random_mod7_82f84((int32_t)random_value);
}
