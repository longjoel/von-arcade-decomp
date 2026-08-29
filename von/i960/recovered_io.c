/* Recovered board I/O self-test core at i960 0x00002730-0x00002768. */

typedef unsigned long u32;
typedef unsigned short u16;

#define IO_SELF_TEST_REGISTER ((volatile u16 *)0x01c00202)
#define IO_FAILURE_STATE      ((volatile u32 *)0x005023e0)

u32 recovered_io_self_test(void)
{
    const u16 expected = 0x004dU;
    u16 observed;
    u32 failed;

    *IO_SELF_TEST_REGISTER = expected;
    observed = *IO_SELF_TEST_REGISTER & 0x00ffU;
    failed = observed == expected ? 0U : 1U;
    *IO_FAILURE_STATE = failed;
    return failed;
}
