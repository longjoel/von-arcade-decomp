/* Random-residue caller-role selector from i960 0x79664-0x796ec. */
typedef unsigned int u32;

/*
 * The caller invokes 0xf5058 first, so random_value is the resulting
 * nonnegative 31-bit state. The ROM rounds it down to an 8-value bucket and
 * uses the low residue as an index into the following role table.
 */
u32 recovered_object_state_random_selector(u32 random_value, u32 *role_value)
{
    static const u32 roles[8] = {1U, 1U, 2U, 2U, 3U, 3U, 5U, 6U};

    *role_value = roles[random_value & 7U];
    return 1U;
}
