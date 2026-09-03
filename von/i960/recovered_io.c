/* Recovered board I/O self-test core at i960 0x00002730-0x00002768. */

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

#define IO_SELF_TEST_REGISTER ((volatile u16 *)0x01c00202)
#define IO_FAILURE_STATE      ((volatile u32 *)0x005023e0)
#define IO_INPUT_CONTROL      (*(volatile u8 *)0x01c00000)
#define IO_INPUT_TABLE_FIRST  ((volatile u16 *)0x00502400)
#define IO_INPUT_TABLE_SECOND ((volatile u16 *)0x00502440)
#define IO_CONTROLLER         ((volatile u16 *)0x01c00000)
#define IO_RUNTIME_BYTES      ((volatile u8 *)0x00502490)
#define IO_RUNTIME_STATUS     (*(volatile u32 *)0x0050249c)

static const u8 io_setup_first[21] = {
    0x11, 0x11, 0x51, 0xd1, 0x71, 0xf1, 0x51,
    0xd1, 0x51, 0xd1, 0x71, 0xf1, 0x51, 0xd1,
    0x51, 0xd1, 0x51, 0xd1, 0x51, 0xd1, 0x51,
};

static const u8 io_setup_second[9] = {
    0x01, 0x01, 0x41, 0xc1, 0x61, 0xe1, 0x61, 0xe1, 0x41,
};

static const u8 io_setup_final[21] = {
    0x11, 0x11, 0x51, 0xd1, 0x71, 0xf1, 0x51,
    0xd1, 0x51, 0xd1, 0x51, 0xd1, 0x51, 0xd1,
    0x51, 0xd1, 0x51, 0xd1, 0x51, 0xd1, 0x51,
};

/* Inline command prefix at 0x00002aa0, consumed by 0x2ab0. */
static const u8 io_command_prefix[9] = {
    0x11, 0x11, 0x51, 0xd1, 0x71, 0xf1, 0x51, 0xd1, 0x71,
};

struct recovered_io_sample {
    u8 status_3f0;
    u8 status_480;
    u8 status_481;
    u8 status_482;
    u16 latched_value;
};

struct recovered_io_packed_state {
    u32 status_49c;
    u8 status_498;
    u8 status_499;
    u8 status_49a;
    u32 work_a0;
    u32 work_a4;
    u32 work_a8;
    u32 work_ac;
    u32 work_b0;
    u32 work_b4;
    u32 work_b8;
    u32 work_bc;
};

/* Pure packed-status tail from 0x00002df0-0x00002ef4. */
void recovered_io_pack_controller_state(
    u32 prior_49c, u32 prior_a4, u32 prior_a8, u32 prior_ac,
    u32 prior_b4, u32 prior_b8, u32 prior_bc,
    u16 port_2, u16 port_4, u16 port_6, u16 port_c,
    struct recovered_io_packed_state *result)
{
    u32 packed = ((u32)(port_6 & 0xffU) << 16)
               | ((u32)(port_4 & 0xffU) << 8)
               | (u32)(port_2 & 0xffU);
    u32 first_mask = prior_49c & packed;
    u32 second_mask = ~((u32)((port_2 >> 6) & 3U));

    (void)prior_a4;
    (void)prior_a8;
    (void)prior_b4;
    (void)prior_b8;
    result->status_49c = ~packed;
    result->status_498 = (u8)port_c;
    result->status_499 = (u8)port_c;
    result->status_49a = (u8)port_c;
    result->work_a0 = prior_49c;
    result->work_a4 = first_mask;
    result->work_a8 = first_mask;
    result->work_ac = second_mask;
    result->work_b0 = prior_ac;
    result->work_b4 = prior_ac & ~second_mask;
    result->work_b8 = second_mask & ~prior_ac;
    result->work_bc = prior_bc;
}

/* First loop of 0x00002da0: average eight persistent bytes with the sampled
 * low controller byte. The surrounding control-port writes are separate. */
void recovered_io_average_controller_bytes(volatile u8 *state,
                                           u16 controller_word)
{
    u8 sampled = (u8)controller_word;
    u32 index;

    for (index = 0; index < 8; ++index)
        state[index] = (u8)(((u32)state[index] + sampled) >> 1);
}

/* Pure command construction from 0x00002ab0. */
u32 recovered_io_command_plan(u16 input_index, u16 table_value, u8 output[34])
{
    u32 count = 0;
    u32 bit;

    for (bit = 0; bit < sizeof(io_command_prefix); ++bit)
        output[count++] = io_command_prefix[bit];
    for (bit = 0; bit < 5; ++bit) {
        output[count++] = (input_index & (1U << (5U + bit))) ? 0x71 : 0x51;
        output[count++] = (input_index & (1U << (5U + bit))) ? 0xf1 : 0xd1;
    }
    for (bit = 0; bit < 5; ++bit) {
        output[count++] = (table_value & (1U << (15U - bit))) ? 0x71 : 0x51;
        output[count++] = (table_value & (1U << (15U - bit))) ? 0xf1 : 0xd1;
    }
    output[count++] = 0x01;
    output[count++] = 0x01;
    output[count++] = 0x51;
    output[count++] = 0xd1;
    output[count++] = 0x51;
    return count;
}

/* Pure schedule from 0x00002c10.  Each of the two 30-entry banks sends the
 * 21-byte controller setup sequence followed by the 34-byte indexed command. */
u32 recovered_io_normal_input_plan(const u16 table[30], u8 *output,
                                   u32 capacity)
{
    u32 count = 0;
    u32 bank;
    u32 index;
    u32 byte;
    u8 command[34];

    for (bank = 0; bank < 2; ++bank)
        for (index = 0; index < 30; ++index) {
            for (byte = 0; byte < sizeof(io_setup_first); ++byte) {
                if (count < capacity)
                    output[count] = io_setup_first[byte];
                ++count;
            }
            recovered_io_command_plan((u16)(index + bank * 30), table[index], command);
            for (byte = 0; byte < sizeof(command); ++byte) {
                if (count < capacity)
                    output[count] = command[byte];
                ++count;
            }
        }
    for (byte = 0; byte < sizeof(io_setup_final); ++byte) {
        if (count < capacity)
            output[count] = io_setup_final[byte];
        ++count;
    }
    return count;
}

/* Pure state transform from the failure-mode sampler at 0x00002cf8. */
void recovered_io_sample_input(u8 input_byte, u16 port_word, u16 latched_value,
                               struct recovered_io_sample *result)
{
    u8 port_low = (u8)port_word;

    result->status_3f0 = (u8)(input_byte & port_low);
    result->status_480 = port_low;
    result->status_481 = input_byte;
    result->status_482 = (u8)~port_low;
    result->latched_value = latched_value;
}

/* 0x2bb0's deterministic index-table portion. */
void recovered_io_fill_input_indices(volatile u16 *first,
                                     volatile u16 *second)
{
    u16 index;

    for (index = 0; index < 30; ++index) {
        first[index] = index;
        second[index] = (u16)(index + 30);
    }
}

/* Return the exact byte plan emitted by 0x2850/0x2990 from 0x2bb0. */
u32 recovered_io_setup_plan(u8 *output, u32 capacity)
{
    u32 count = 0;
    u32 index;
    u32 byte;

    for (index = 0; index < 30; ++index)
        for (byte = 0; byte < sizeof(io_setup_first); ++byte) {
            if (count < capacity)
                output[count] = io_setup_first[byte];
            ++count;
        }
    for (index = 0; index < 60; ++index)
        for (byte = 0; byte < sizeof(io_setup_second); ++byte) {
            if (count < capacity)
                output[count] = io_setup_second[byte];
            ++count;
        }
    return count;
}

/* Mapped execution of the fixed port writes and index-table setup. */
void recovered_io_input_initialize(void)
{
    u32 index;
    u32 byte;

    for (index = 0; index < 30; ++index)
        for (byte = 0; byte < sizeof(io_setup_first); ++byte)
            IO_INPUT_CONTROL = io_setup_first[byte];
    for (index = 0; index < 60; ++index)
        for (byte = 0; byte < sizeof(io_setup_second); ++byte)
            IO_INPUT_CONTROL = io_setup_second[byte];
    recovered_io_fill_input_indices(IO_INPUT_TABLE_FIRST, IO_INPUT_TABLE_SECOND);
}

/* Per-frame sampler recovered from i960 0x00002d60 -> 0x00002da0. */
void recovered_io_service(void)
{
    struct recovered_io_packed_state result;
    u16 controller_word;
    u16 port_2;
    u16 port_4;
    u16 port_6;
    u16 port_c;
    u32 prior_49c = IO_RUNTIME_STATUS;
    u32 prior_a4 = *(volatile u32 *)0x005024a4;
    u32 prior_a8 = *(volatile u32 *)0x005024a8;
    u32 prior_ac = *(volatile u32 *)0x005024ac;
    u32 prior_b4 = *(volatile u32 *)0x005024b4;
    u32 prior_b8 = *(volatile u32 *)0x005024b8;
    u32 prior_bc = *(volatile u32 *)0x005024bc;
    u32 index;

    IO_CONTROLLER[0x1e / 2] = 0U;
    controller_word = IO_CONTROLLER[0x1e / 2];
    for (index = 0U; index < 8U; ++index)
        IO_RUNTIME_BYTES[index] = (u8)(((u32)IO_RUNTIME_BYTES[index] +
                                        (controller_word & 0xffU)) >> 1);

    IO_CONTROLLER[0x10 / 2] = 0x4fU;
    IO_CONTROLLER[0] = 0U;
    port_2 = IO_CONTROLLER[0x2 / 2];
    port_4 = IO_CONTROLLER[0x4 / 2];
    port_6 = IO_CONTROLLER[0x6 / 2];
    port_c = IO_CONTROLLER[0xc / 2];
    recovered_io_pack_controller_state(
        prior_49c, prior_a4, prior_a8, prior_ac,
        prior_b4, prior_b8, prior_bc,
        port_2, port_4, port_6, port_c, &result);
    IO_RUNTIME_STATUS = result.status_49c;
    *(volatile u8 *)0x00502498 = result.status_498;
    *(volatile u8 *)0x00502499 = result.status_499;
    *(volatile u8 *)0x0050249a = result.status_49a;
    *(volatile u32 *)0x005024a0 = result.work_a0;
    *(volatile u32 *)0x005024a4 = result.work_a4;
    *(volatile u32 *)0x005024a8 = result.work_a8;
    *(volatile u32 *)0x005024ac = result.work_ac;
    *(volatile u32 *)0x005024b0 = result.work_b0;
    *(volatile u32 *)0x005024b4 = result.work_b4;
    *(volatile u32 *)0x005024b8 = result.work_b8;
    *(volatile u32 *)0x005024bc = result.work_bc;
}

/* Deterministic stores at 0x00002700-0x00002728. */
void recovered_io_failure_reset(volatile u8 *byte_480,
                                volatile u8 *byte_3f0,
                                volatile u8 *byte_481,
                                volatile u8 *byte_482,
                                volatile u16 *halfword_484)
{
    *byte_480 = 0;
    *byte_3f0 = 0;
    *byte_481 = 0;
    *byte_482 = 0;
    *halfword_484 = 0;
}

/* Mapped wrapper for the stores before the 0x2bb0 initializer call. */
void recovered_io_failure_prepare(void)
{
    recovered_io_failure_reset((volatile u8 *)0x00502480,
                               (volatile u8 *)0x005023f0,
                               (volatile u8 *)0x00502481,
                               (volatile u8 *)0x00502482,
                               (volatile u16 *)0x00502484);
}

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
