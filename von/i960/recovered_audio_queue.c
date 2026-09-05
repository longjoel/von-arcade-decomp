/* Recovered host-to-SCSP command FIFO at i960 0x2a458-0x2a574. */

typedef unsigned int u32;
typedef signed int s32;
typedef unsigned char u8;

/* Pure descriptors for the unresolved 0x29a80/0x29ae8 setup helpers. */
u32 recovered_audio_device_copy_plan(u32 index, u32 *source,
                                     u32 *destination, u32 *bytes,
                                     u32 *count_source)
{
    if (index == 0U) {
        *source = 0x000f48d0U;
        *destination = 0x01800000U;
        *bytes = 4U;
        *count_source = 0U;
        return 1U;
    }
    if (index == 1U) {
        *source = 0x000f48d2U;
        *destination = 0x01802000U;
        *bytes = 0U;
        *count_source = 0x000f48d0U;
        return 1U;
    }
    return 0U;
}

u32 recovered_audio_device_table_clear_plan(u32 index, u32 *address,
                                             u32 *value)
{
    if (index >= 52U)
        return 0U;
    *address = 0x0051a0c0U + (index << 3);
    *value = 0U;
    return 1U;
}

u32 recovered_audio_service_table_reset_plan(u32 index, u32 *address,
                                             u32 *value)
{
    if (index >= 24U)
        return 0U;
    *address = 0x00504c30U + (index << 1);
    *value = 0xffffU;
    return 1U;
}

u32 recovered_audio_device_record_plan(u32 index, u32 *source_record,
                                       u32 *destination)
{
    if (index >= 23U)
        return 0U;
    *source_record = 0x02bf83c8U + (index << 3);
    *destination = 0x01802010U + (index << 1);
    return 1U;
}

/* The 0x29b20 index calculation before its unresolved table read. */
u32 recovered_audio_device_record_index(u32 selector, u32 exponent,
                                        u32 mask)
{
    return (selector << (exponent & 0xffffU)) & (mask & 0xffffU);
}

/* Pure 0x29ca0 copy: 96 rows, 64 words per row, 0x200-byte row stride. */
void recovered_audio_device_buffer_copy(u32 *destination,
                                        const u32 *source)
{
    u32 row;
    u32 word;

    for (row = 0U; row < 96U; ++row)
        for (word = 0U; word < 64U; ++word)
            destination[row * 128U + word] = source[row * 128U + word];
}
typedef unsigned short u16;

#define AUDIO_READ_INDEX  (*(volatile u32 *)0x0051aa70)
#define AUDIO_WRITE_INDEX (*(volatile u32 *)0x0051aa74)
#define AUDIO_QUEUE       ((volatile u8 *)0x0051aa80)
#define AUDIO_MODE        (*(volatile u32 *)0x005039f4)
#define BOARD_STATUS      (*(volatile u8 *)0x01d00022)
#define IRQ_CONTROL       (*(volatile u32 *)0x00501cd0)
#define IRQ_CONTROL_MMIO  (*(volatile u32 *)0x00e80004)
#define SCSP_STATUS       (*(volatile u8 *)0x009c0004)
#define SCSP_CONTROL      (*(volatile u16 *)0x009c0004)
#define SCSP_COMMAND      (*(volatile u16 *)0x009c0000)
#define AUDIO_SERVICE_BIT (1U << 10)
#define AUDIO_STAGE       (*(volatile u32 *)0x005000b0)
#define AUDIO_DIRECT_COUNT (*(volatile u32 *)0x005000b4)

void recovered_host_interrupt_mask_update(u32 mask);

u32 recovered_audio_queue_has_space(u32 read_index, u32 write_index, u32 count)
{
    u32 available = (read_index - write_index - 1U) & 0x3fU;
    return available >= count;
}

/* Recovered 0x2a430 timing leaf: four iterations of a volatile countdown. */
u32 recovered_audio_short_delay_iterations(void)
{
    return 4U;
}

void recovered_audio_short_delay(void)
{
    volatile u32 count = recovered_audio_short_delay_iterations();

    while (count != 0U)
        --count;
}

void recovered_audio_queue_push(u32 byte_value)
{
    u32 write_index = AUDIO_WRITE_INDEX;
    AUDIO_QUEUE[write_index] = (u8)byte_value;
    AUDIO_WRITE_INDEX = (write_index + 1U) & 0x3fU;
}

/* Core of the 0x16dc audio interrupt branch, expressed as state inputs. */
u32 recovered_audio_queue_consume(u32 read_index, u32 write_index,
                                  u32 sound_status,
                                  volatile const u8 *queue,
                                  u32 *next_read, u32 *value)
{
    if (read_index == write_index || (sound_status & 1U) == 0U)
        return 0U;
    *value = queue[read_index & 0x3fU];
    *next_read = (read_index + 1U) & 0x3fU;
    return 1U;
}

/* Poll the reconstructed control mirror and service one pending audio byte. */
void recovered_audio_service_pending(void)
{
    u32 control = IRQ_CONTROL;
    u32 next_read;
    u32 value;

    if ((control & AUDIO_SERVICE_BIT) == 0U)
        return;
    recovered_host_interrupt_mask_update(AUDIO_SERVICE_BIT);
    if (!recovered_audio_queue_consume(
            AUDIO_READ_INDEX, AUDIO_WRITE_INDEX, SCSP_STATUS,
            AUDIO_QUEUE, &next_read, &value))
        return;
    AUDIO_READ_INDEX = next_read;
    SCSP_COMMAND = (u16)value;
}

/* Recovered host service request at i960 0x00001348-0x00001370. */
void recovered_host_service_request(void)
{
    u32 control = IRQ_CONTROL | AUDIO_SERVICE_BIT;
    IRQ_CONTROL = control;
    IRQ_CONTROL_MMIO = control;
}

/* Encode the producer-side command framing without touching host MMIO. */
u32 recovered_audio_command_bytes_for_status(u32 value, u32 mode,
                                             u32 board_status,
                                             u32 suppressed_status,
                                             u8 *output)
{
    value &= 0xffffU;
    if (value == 0x00ffU) {
        output[0] = (u8)value;
        return 1U;
    }
    if (mode == 1U && (board_status & 0xffU) == (suppressed_status & 0xffU))
        return 0U;
    output[0] = 0xaeU;
    output[1] = (u8)(value >> 8);
    output[2] = (u8)value;
    return 3U;
}

u32 recovered_audio_command_bytes(u32 value, u32 mode, u32 board_status,
                                  u8 *output)
{
    return recovered_audio_command_bytes_for_status(
        value, mode, board_status, 2U, output);
}

u32 recovered_audio_frame_bytes(u32 value, u32 selector, u8 *output)
{
    output[0] = 0xa0U;
    output[1] = (u8)selector;
    output[2] = (u8)value;
    return 3U;
}

static void recovered_audio_send_frame(const u8 *frame, u32 count)
{
    u32 index;

    if (!recovered_audio_queue_has_space(
            AUDIO_READ_INDEX, AUDIO_WRITE_INDEX, count))
        return;
    for (index = 0; index < count; ++index)
        recovered_audio_queue_push(frame[index]);
    recovered_host_service_request();
}

/* Development-target bridge: vonjdev has the host UART mapped at 0x9c0000,
 * while the recovered interrupt vector still enters original ROM code.  Send
 * the same framed bytes through that mapped endpoint without raising the
 * unresolved bit-10 interrupt.  The exact producer above remains available
 * for original-path comparison and unit tests. */
void recovered_audio_send_u16_direct(u32 value)
{
    u8 encoded[3];
    u32 count;
    u32 index;

    count = recovered_audio_command_bytes(
        value, AUDIO_MODE, BOARD_STATUS, encoded);
    for (index = 0; index < count; ++index)
        SCSP_COMMAND = (u16)encoded[index];
    AUDIO_DIRECT_COUNT += count;
}

void recovered_audio_send_u16(u32 value)
{
    u8 encoded[3];
    u32 count;
    u32 index;

    value &= 0xffffU;
    count = recovered_audio_command_bytes(
        value, AUDIO_MODE, BOARD_STATUS, encoded);
    if (count == 0U)
        return;
    if (!recovered_audio_queue_has_space(
            AUDIO_READ_INDEX, AUDIO_WRITE_INDEX, count))
        return;
    AUDIO_STAGE = 31U;
    for (index = 0; index < count; ++index)
        recovered_audio_queue_push(encoded[index]);
    AUDIO_STAGE = 32U;
    recovered_host_service_request();
    AUDIO_STAGE = 33U;
}

/* The sibling 0x2a5f0 sender suppresses status 0 instead of status 2. */
void recovered_audio_send_u16_when_idle(u32 value)
{
    u8 encoded[3];
    u32 count;

    count = recovered_audio_command_bytes_for_status(
        value, AUDIO_MODE, BOARD_STATUS, 0U, encoded);
    if (count != 0U)
        recovered_audio_send_frame(encoded, count);
}

u32 recovered_audio_clamp_level(s32 value)
{
    if (value > 127)
        return 127U;
    if (value <= 0)
        return 1U;
    return (u32)value;
}

void recovered_audio_send_clamped_level(s32 value)
{
    u8 frame[3];

    recovered_audio_frame_bytes(recovered_audio_clamp_level(value), 1U, frame);
    recovered_audio_send_frame(frame, 3U);
}

/* Recovered 0x2a870 sender: opcode 0xa0, selector 0, low byte of value. */
void recovered_audio_send_value_selector_zero(u32 value)
{
    u8 frame[3];

    recovered_audio_frame_bytes(value, 0U, frame);
    recovered_audio_send_frame(frame, 3U);
}

u32 recovered_audio_queue_init_fill_value(void)
{
    return 0x99U;
}

u32 recovered_audio_init_status_value(u32 index)
{
    if (index < 3U)
        return 0U;
    if (index == 3U)
        return 0x40U;
    if (index == 4U)
        return 0x4eU;
    if (index == 5U)
        return 0x37U;
    return 0U;
}

/* Recovered 0x2a8a0 SCSP/FIFO startup sequence. */
void recovered_audio_initialize_scsp(void)
{
    u32 index;

    AUDIO_STAGE = 1U;
    AUDIO_WRITE_INDEX = 0U;
    AUDIO_READ_INDEX = 0U;
    for (index = 0; index < 0x40U; ++index)
        AUDIO_QUEUE[index] = (u8)recovered_audio_queue_init_fill_value();

    AUDIO_STAGE = 2U;
    SCSP_CONTROL = (u16)recovered_audio_init_status_value(0U);
    recovered_audio_short_delay();
    SCSP_CONTROL = (u16)recovered_audio_init_status_value(1U);
    recovered_audio_short_delay();
    SCSP_CONTROL = (u16)recovered_audio_init_status_value(2U);
    recovered_audio_short_delay();
    SCSP_CONTROL = (u16)recovered_audio_init_status_value(3U);
    recovered_audio_short_delay();
    SCSP_CONTROL = (u16)recovered_audio_init_status_value(4U);
    recovered_audio_short_delay();
    SCSP_CONTROL = (u16)recovered_audio_init_status_value(5U);
    AUDIO_STAGE = 3U;
    recovered_audio_send_u16_direct(0xffU);
    AUDIO_STAGE = 4U;
}
