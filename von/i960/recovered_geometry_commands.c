/* Recovered from the command-window setup at i960 addresses 0x284b0-0x28534. */

typedef unsigned long u32;
typedef unsigned char u8;
typedef unsigned short u16;

#define GEO_COMMAND_WINDOW ((volatile u32 *)0x00800000)
#define GEO_COMMAND_TABLE  ((volatile const u8 *)0x00028470)
#define GEO_PROGRAM_PORT   ((volatile u32 *)0x00804000)
#define GEO_FRAME_STATUS   ((volatile u32 *)0x0098000c)
#define GEO_WRITE_START    ((volatile u32 *)0x00801008)
#define GEO_READ_START     ((volatile u32 *)0x00803008)
#define GEO_PHASE          ((volatile u32 *)0x00511ba0)

void recovered_geometry_frame_submission(void);

/* The first loop clears the +4 and +8 fields of 64 sixteen-byte slots. */
void recovered_geometry_command_window_clear(void)
{
    u32 slot;

    for (slot = 0; slot < 64; ++slot)
    {
        GEO_COMMAND_WINDOW[slot * 4 + 1] = 0;
        GEO_COMMAND_WINDOW[slot * 4 + 2] = 0;
    }
}

/* The second loop copies 64 inline table bytes into those same fields. */
void recovered_geometry_command_table_copy(void)
{
    u32 slot;

    for (slot = 0; slot < 32; ++slot)
    {
        GEO_COMMAND_WINDOW[slot * 4 + 1] = GEO_COMMAND_TABLE[slot * 2];
        GEO_COMMAND_WINDOW[slot * 4 + 2] = GEO_COMMAND_TABLE[slot * 2 + 1];
    }
}

/*
 * Recovered from 0x28e88. The source pointer, command word, and count map to
 * the host's g0, g1, and g2 registers respectively. The return-link register
 * g3 is an i960 calling convention detail and is not a C parameter.
 */
void recovered_geometry_function_command_submit(volatile const u16 *source,
                                                 u32 command,
                                                 u32 count)
{
    GEO_COMMAND_WINDOW[0x040 / 4] = 0x00000404U;
    *GEO_PROGRAM_PORT = (command & 0xffffU) | 0x00800000U;
    *GEO_PROGRAM_PORT = count;

    while (count-- != 0)
        *GEO_PROGRAM_PORT = (u32)(*source++ & 0xffffU);

    GEO_COMMAND_WINDOW[0x100 / 4] = 0x00001010U;
    *GEO_PROGRAM_PORT = 0;
}

/* Recovered from 0x28c00. This path streams 32-bit units, unlike 0x28e88. */
void recovered_geometry_batch_command_submit(volatile const u32 *source,
                                              u32 command,
                                              u32 count)
{
    GEO_COMMAND_WINDOW[0x140 / 4] = 0x00001414U;
    *GEO_PROGRAM_PORT = command & 0xffffU;
    *GEO_PROGRAM_PORT = count;

    while (count-- != 0)
        *GEO_PROGRAM_PORT = *source++;

    GEO_COMMAND_WINDOW[0x100 / 4] = 0x00001010U;
    *GEO_PROGRAM_PORT = 0;
}

/* Recovered from 0x28c80. The source argument is a byte-addressed host
 * pointer, matching the i960 register arithmetic and 32-bit loads. */
void recovered_geometry_command_batch_loop(volatile const u8 *source)
{
    volatile u32 *function_word = &GEO_COMMAND_WINDOW[0x0f0 / 4];
    u32 command_offset;
    u32 batch;

    command_offset = 0;
    batch = 0;
    recovered_geometry_frame_submission();
    do
    {
        recovered_geometry_batch_command_submit(
            (volatile const u32 *)source, command_offset << 2, 0x800U);
        *function_word = 0x00000f0fU;
        recovered_geometry_frame_submission();
        recovered_geometry_frame_submission();
        recovered_geometry_frame_submission();

        ++batch;
        source += 0x2000;
        command_offset += 0x800;
    } while (batch < 4);

    *function_word = 0x00000f0fU;
    recovered_geometry_frame_submission();
    *function_word = 0x00000f0fU;
    recovered_geometry_frame_submission();
}

/* Recovered from the frame/phase handoff at 0x28de8. */
void recovered_geometry_frame_submission(void)
{
    u32 phase;
    u32 expected;

    phase = *GEO_PHASE & 1U;
    *GEO_READ_START = phase ? 0x00010000U : 0;

    expected = *GEO_FRAME_STATUS & 4U;

    while ((*GEO_FRAME_STATUS & 4U) != expected)
        ;

    phase = (phase + 1U) & 1U;
    *GEO_PHASE = phase;
    *GEO_WRITE_START = phase ? 0x00010000U : 0;
}
