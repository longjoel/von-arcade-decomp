/*
 * C reconstruction of the confirmed early vonj host path.
 *
 * This is intentionally separate from main.c, which remains the small
 * hardware smoke-test prototype.  The routines below preserve observed host
 * bus transfers; they do not claim to implement the SHARC or geometry
 * processors themselves.
 */

typedef unsigned long u32;
typedef unsigned short u16;

#define IO_REGISTERS ((volatile u16 *)0x01c00000)
#define SHARC_CONTROL ((volatile u32 *)0x00980000)
#define SHARC_FIFO ((volatile u16 *)0x00884000)
#define SHARC_SOURCE ((volatile const u16 *)0x0016b58c)
#define WORKRAM ((volatile u32 *)0x00500000)

#define SHARC_BOOT_WORDS 0x2b1eU

void recovered_geometry_program_upload(void);
void recovered_geometry_initial_handshake(void);
void recovered_geometry_command_window_clear(void);
void recovered_geometry_command_table_copy(void);
void recovered_geometry_register_clear(void);
void recovered_texture_initializer(void);
int recovered_texture_loader_profile_setup(void);

static u16 reconstructed_io_self_test(void)
{
    IO_REGISTERS[0x002 / 2] = 0x004dU;
    return IO_REGISTERS[0x002 / 2];
}

static void reconstructed_sharc_upload(void)
{
    u32 index;

    *SHARC_CONTROL = 0x80000000U;
    for (index = 0; index < SHARC_BOOT_WORDS; ++index)
        *SHARC_FIFO = SHARC_SOURCE[index];
    *SHARC_CONTROL = 0;
}

void i960_reconstructed_main(void)
{
    volatile u32 *const state = WORKRAM + 0x20;
    u16 io_result;

    state[0] = 0x52454330UL; /* REC0 */
    io_result = reconstructed_io_self_test();
    state[1] = io_result;

    reconstructed_sharc_upload();
    state[2] = SHARC_BOOT_WORDS;

    recovered_geometry_program_upload();
    state[3] = 0x47454f30UL; /* GEO0 */

    recovered_geometry_initial_handshake();
    recovered_geometry_command_window_clear();
    recovered_geometry_command_table_copy();
    recovered_geometry_register_clear();
    recovered_texture_initializer();
    state[6] = (u32)recovered_texture_loader_profile_setup();
    state[4] = 0x494e4954UL; /* INIT */

    for (;;)
        state[5] = state[5] + 1;
}
