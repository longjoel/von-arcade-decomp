/* Recovered from the command-window setup at i960 addresses 0x284b0-0x28534. */

#include "recovered_geometry_pipeline.h"

typedef unsigned long u32;
typedef unsigned char u8;
typedef unsigned short u16;

#include "recovered_geometry_select_frame.inc"

u32 recovered_geometry_object_packet_prefix(const u32 base[3],
                                            u32 parameter_16,
                                            u32 parameter_15,
                                            u32 parameter_14,
                                            u32 packet[10]);
u32 recovered_geometry_object_profile_submission(const u32 base[3],
                                                 const u32 profile_vector[3],
                                                 u32 length_response,
                                                 u32 angle_response,
                                                 u32 packet[29]);
u32 recovered_geometry_polygon_object_submission(u32 tpa, u32 tha, u32 oba,
                                                 u32 count, u32 packet[4]);
u32 recovered_geometry_matrix_submission(const u32 matrix[12], u32 packet[13]);

#define GEO_COMMAND_WINDOW ((volatile u32 *)0x00800000)
#define GEO_COMMAND_TABLE  ((volatile const u8 *)0x00028470)
#define GEO_PROGRAM_PORT   ((volatile u32 *)0x00804000)
#define GEO_DISPLAY_BUFFER ((volatile u32 *)0x00900000)
#define GEO_CONTROL        ((volatile u32 *)0x00980008)
#define GEO_FRAME_STATUS   ((volatile u32 *)0x0098000c)
#define GEO_WRITE_START    ((volatile u32 *)0x00801008)
#define GEO_READ_START     ((volatile u32 *)0x00803008)
#define GEO_PHASE          ((volatile u32 *)0x00511ba0)
#define GEOMETRY_BUFFER    ((volatile u32 *)0x00509ba0)
#define GEOMETRY_STATE     ((volatile u16 *)0x0181c000)
#define GEO_FIXED_REGISTER ((volatile u32 *)0x10000000)
#define GEOMETRY_STATE_A   ((volatile u32 *)0x005039f4)
#define GEOMETRY_STATE_B   ((volatile u32 *)0x00503a00)

/* The first loop clears the +4 and +8 fields of 64 sixteen-byte slots. */
void recovered_geometry_command_window_clear_slots(volatile u32 *window,
                                                   u32 slots)
{
    u32 slot;

    for (slot = 0; slot < slots; ++slot)
    {
        window[slot * 4 + 1] = 0;
        window[slot * 4 + 2] = 0;
    }
}

void recovered_geometry_command_window_clear(void)
{
    recovered_geometry_command_window_clear_slots(GEO_COMMAND_WINDOW, 64);
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
void recovered_geometry_batch_command_header(u32 command, u32 count,
                                             u32 output[2])
{
    output[0] = command & 0xffffU;
    output[1] = count;
}

void recovered_geometry_batch_command_submit(volatile const u32 *source,
                                              u32 command,
                                              u32 count)
{
    u32 header[2];

    GEO_COMMAND_WINDOW[0x140 / 4] = 0x00001414U;
    recovered_geometry_batch_command_header(command, count, header);
    *GEO_PROGRAM_PORT = header[0];
    *GEO_PROGRAM_PORT = header[1];

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

/* Confirmed host-side buffer generation and submission chain. */
void recovered_geometry_buffer_and_batch_chain(void)
{
    recovered_geometry_buffer_prepare(GEOMETRY_BUFFER);
    recovered_geometry_command_batch_loop((volatile const u8 *)GEOMETRY_BUFFER);
}

/* Recovered caller sequence at 0x28d80. The mode value is saved in r4 by the
 * ROM and gates the two conditional setup groups. */
u32 recovered_geometry_pipeline_startup_plan(u32 mode, u32 steps[11])
{
    u32 count = 0U;

    steps[count++] = 1U; /* profile setup */
    if (mode == 0U) {
        steps[count++] = 2U; /* SHARC bootstrap upload */
        steps[count++] = 3U; /* geometry program upload */
    }
    steps[count++] = 4U; /* fixed-register clear */
    steps[count++] = 5U; /* texture tables */
    steps[count++] = 6U; /* command-window clear */
    steps[count++] = 7U; /* command-table copy */
    steps[count++] = 8U; /* initial handshake */
    if (mode == 0U)
        steps[count++] = 9U; /* auxiliary submit */
    steps[count++] = 10U; /* geometry buffer and batch chain */
    steps[count++] = 11U; /* publish ready state */
    return count;
}

void recovered_geometry_pipeline_startup(u32 mode)
{
    recovered_geometry_profile_setup();

    if (mode == 0) {
        recovered_sharc_bootstrap_upload();
        recovered_geometry_program_upload();
    }

    recovered_geometry_register_clear();
    recovered_texture_initializer();
    recovered_geometry_command_window_clear();
    recovered_geometry_command_table_copy();
    recovered_geometry_initial_handshake();

    if (mode == 0) {
        /* vonjdev has no mapped backing for the recovered texture streams.
         * The loader remains available as a standalone recovered routine;
         * this development startup proceeds to the host-side command chain. */
        recovered_geometry_auxiliary_submit_select();
    }

    recovered_geometry_buffer_and_batch_chain();
    *GEOMETRY_STATE = 0xffffU;
}

/* Development boundary used until the bulk display-list grammar and board
 * upload contract is validated. Both source windows are now ROM-backed and
 * the SHARC FIFO transport is fixed-address; probe the geometry stream after
 * that prerequisite. */
void recovered_geometry_pipeline_startup_development(void)
{
    recovered_geometry_profile_setup();
    recovered_sharc_bootstrap_upload();
    recovered_geometry_program_upload();
    recovered_geometry_register_clear();
    recovered_texture_initializer();
    recovered_geometry_command_window_clear();
    recovered_geometry_command_table_copy();
    recovered_geometry_initial_handshake();
    *GEOMETRY_STATE = 0xffffU;
}

/* Parser-observed setup stream preceding the first matrix/object batch. */
u32 recovered_geometry_display_preamble(volatile u32 output[28])
{
    static const u32 words[28] = {
        0x0b001616U, 0x47800000U, 0x03800707U, 3U,
        0x04000808U, 0x41004000U,
        0x01800303U, 0x00000080U, 0x01f40204U,
        0x00f80140U, 0x00f80140U, 0x00f80140U, 0x00f80140U,
        0x03000606U, 0U, 0U,
        0x04800909U, 0x44160000U, 0x44160000U,
        0x05000a0aU, 0U, 0U, 0x3f800000U,
        0x02000404U, 0x00800000U, 0U,
        0x08001010U, 0U
    };
    u32 index;

    for (index = 0U; index < 28U; ++index)
        output[index] = words[index];
    return 28U;
}

/* Recovered from the startup handshake at 0x28418. */
void recovered_geometry_initial_handshake_plan(volatile u32 *control,
                                               volatile u32 *write_start,
                                               volatile u32 *command_window,
                                               volatile u32 *read_start,
                                               volatile u32 *phase)
{
    *control = 0;
    *write_start = 0;
    command_window[0x0f0 / 4] = 0x00000f0fU;
    *write_start = 0x00010000U;
    command_window[0x0f0 / 4] = 0x00000f0fU;
    *read_start = 0x00010000U;
    *phase = 0;
}

void recovered_geometry_initial_handshake(void)
{
    recovered_geometry_initial_handshake_plan(
        GEO_CONTROL, GEO_WRITE_START, GEO_COMMAND_WINDOW,
        GEO_READ_START, GEO_PHASE);
}

/* Recovered from the small helper at 0x28d08. */
void recovered_geometry_register_clear_value(volatile u32 *fixed_register)
{
    *fixed_register = 0x00004004U;
}

void recovered_geometry_register_clear(void)
{
    recovered_geometry_register_clear_value(GEO_FIXED_REGISTER);
}

/* Recovered from 0x28d30. */
void recovered_geometry_auxiliary_submit_plan(u32 state_a, u32 state_b,
                                              u32 *source_address,
                                              u32 *word_count)
{
    if (state_a == 4U && state_b == 32U)
    {
        *source_address = 0x001687a4U;
        *word_count = 0x4e4U;
    }
    else
    {
        *source_address = 0x001686e4U;
        *word_count = 0x60U;
    }
}

void recovered_geometry_auxiliary_submit_select(void)
{
    u32 source_address;
    u32 word_count;

    recovered_geometry_auxiliary_submit_plan(
        *GEOMETRY_STATE_A, *GEOMETRY_STATE_B,
        &source_address, &word_count);
    recovered_geometry_function_command_submit(
        (volatile const u16 *)(unsigned long)source_address, 0, word_count);
}

/* Recovered from the frame/phase handoff at 0x28de8. */
void recovered_geometry_frame_submission(void)
{
    u32 phase;
    u32 expected;
    u32 spins;


    phase = *GEO_PHASE & 1U;
    *GEO_READ_START = phase ? 0x00010000U : 0;

    expected = *GEO_FRAME_STATUS & 4U;

    /* 0x28e34/0x28e3c branches back while bit 2 is unchanged. */
    spins = 0;
    while ((*GEO_FRAME_STATUS & 4U) == expected) {
        /* The development MAME driver has no geometry completion device.
         * Keep the hardware poll intact, but do not strand the reconstructed
         * attract scheduler when that optional device is absent. */
        if (++spins == 0x00001000U)
            break;
    }


    phase = (phase + 1U) & 1U;
    *GEO_PHASE = phase;
    *GEO_WRITE_START = phase ? 0x00010000U : 0;
}

/* First captured match display-list prefix at the 0x2b430 -> geometry
 * command boundary. The returned words are the matrix, legal polygon opcode,
 * and first eight ordered object records from one original frame. */
u32 recovered_geometry_match_object_batch(u32 output[45])
{
    static const u32 matrix_packet[12] = {
        0x3e23d70aU, 0x00000000U, 0x00000000U,
        0x00000000U, 0x3db11111U, 0x00000000U,
        0x00000000U, 0x00000000U, 0x3f800000U,
        0xc2d00000U, 0xc1e00000U, 0x3f800000U
    };
    static const u32 object_records[8][4] = {
        { 0x00000000U, 0x0040000cU, 0x0084553fU, 1U },
        { 0x004a0c3cU, 0x004a0c44U, 0x0091af12U, 0U },
        { 0x0049c858U, 0x0049c918U, 0x0091433fU, 0U },
        { 0x004a0c48U, 0x004a0c50U, 0x0091af23U, 0U },
        { 0x004a2d96U, 0x004a456eU, 0x0091e76cU, 0U },
        { 0x0049cd74U, 0x0049cd9cU, 0x0091577dU, 0U },
        { 0x0009b7e4U, 0x0009b9dcU, 0x009e410dU, 0U },
        { 0x0009b6c8U, 0x0009b7d4U, 0x009e3f80U, 0U }
    };
    u32 index;
    for (index = 0U; index < 12U; ++index)
        output[index] = matrix_packet[index];
    output[12] = 0x00800101U;
    for (index = 0U; index < 8U; ++index)
        recovered_geometry_polygon_object_submission(
            object_records[index][0], object_records[index][1],
            object_records[index][2], object_records[index][3],
            output + 13U + index * 4U);
    return 45U;
}

void recovered_geometry_match_object_seed(void)
{
    u32 matrix_packet[13];
    u32 packet[4];
    u32 matrix_index;
    u32 record_index;
    u32 index;
    u32 write_index = 0x10000U / 4U;
    static u32 animation_frame;

    /* vonjdev maps the geometry buffer as ordinary host RAM. Populate the
     * published page directly so the development renderer sees the same
     * display-list words the hardware FIFO would have committed. The setup
     * preamble follows the original parser trace: LOD, mode, z-sort, window,
     * texture parameters, focal distance, light, texture data, and dummy. */
    write_index += recovered_geometry_display_preamble(
        GEO_DISPLAY_BUFFER + write_index);
    record_index = 0U;
    for (matrix_index = 0U; matrix_index < 37U; ++matrix_index) {
        recovered_geometry_matrix_submission(
            (animation_frame & 1U) != 0U
                ? select_matrices_frame1[matrix_index]
                : select_matrices[matrix_index], matrix_packet);
        for (index = 0U; index < 13U; ++index)
            GEO_DISPLAY_BUFFER[write_index++] = matrix_packet[index];
        while (record_index < 40U &&
               select_object_matrix[record_index] == matrix_index) {
            GEO_DISPLAY_BUFFER[write_index++] = 0x00800101U;
            recovered_geometry_polygon_object_submission(
                select_objects[record_index][0], select_objects[record_index][1],
                select_objects[record_index][2], select_objects[record_index][3],
                packet);
            for (index = 0U; index < 4U; ++index)
                GEO_DISPLAY_BUFFER[write_index++] = packet[index];
            ++record_index;
        }
    }
    ++animation_frame;
    /* Terminate the published display list. Without the GEO end opcode the
     * parser falls through into the cleared buffer and repeatedly interprets
     * the startup sentinel (0x07800f0f), diverging from the original stream's
     * bounded command sequence. */
    GEO_DISPLAY_BUFFER[write_index++] = 0x07800f0fU;
    *GEO_READ_START = 0x00010000U;
    *GEO_WRITE_START = (write_index * 4U) & 0x1ffffU;
}

/* Integrate the recovered host object-packet emitter without submitting its
 * still-unvalidated payload to the display-list parser. The command window is
 * an observable scratch boundary in vonjdev and provides a safe handoff for
 * the next packet/parser comparison fixture. */
void recovered_geometry_object_packet_probe(void)
{
    static const u32 base[3] = { 0x0000b6d0U, 0x00004c4cU, 0x0000bb8bU };
    static const u32 profile_vector[3] = {
        0xbeddb3e1U, 0xbf5db3d0U, 0xbe800000U
    };
    u32 packet[29];
    u32 packet_words;
    u32 index;

    packet_words = recovered_geometry_object_profile_submission(
        base, profile_vector, 0x3f000004U, 0xbf5db3d0U, packet);
    for (index = 0U; index < packet_words; ++index)
        GEO_COMMAND_WINDOW[0x180U / 4U + index] = packet[index];
}
