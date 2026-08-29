/* Recovered host-to-SCSP command FIFO at i960 0x2a458-0x2a574. */

typedef unsigned int u32;
typedef unsigned char u8;

#define AUDIO_READ_INDEX  (*(volatile u32 *)0x0051aa70)
#define AUDIO_WRITE_INDEX (*(volatile u32 *)0x0051aa74)
#define AUDIO_QUEUE       ((volatile u8 *)0x0051aa80)
#define AUDIO_MODE        (*(volatile u32 *)0x005039f4)
#define BOARD_STATUS      (*(volatile u8 *)0x01d00022)
#define IRQ_CONTROL       (*(volatile u32 *)0x00501cd0)
#define IRQ_CONTROL_MMIO  (*(volatile u32 *)0x00e80004)

u32 recovered_audio_queue_has_space(u32 read_index, u32 write_index, u32 count)
{
    u32 available = (read_index - write_index - 1U) & 0x3fU;
    return available >= count;
}

void recovered_audio_queue_push(u32 byte_value)
{
    u32 write_index = AUDIO_WRITE_INDEX;
    AUDIO_QUEUE[write_index] = (u8)byte_value;
    AUDIO_WRITE_INDEX = (write_index + 1U) & 0x3fU;
}

static void recovered_audio_queue_kick(void)
{
    u32 control = IRQ_CONTROL | (1U << 10);
    IRQ_CONTROL = control;
    IRQ_CONTROL_MMIO = control;
}

void recovered_audio_send_u16(u32 value)
{
    value &= 0xffffU;
    if (value == 0x00ffU) {
        if (!recovered_audio_queue_has_space(
                AUDIO_READ_INDEX, AUDIO_WRITE_INDEX, 1U))
            return;
        recovered_audio_queue_push(value);
        recovered_audio_queue_kick();
        return;
    }

    if (AUDIO_MODE == 1U && BOARD_STATUS == 2U)
        return;
    if (!recovered_audio_queue_has_space(
            AUDIO_READ_INDEX, AUDIO_WRITE_INDEX, 3U))
        return;
    recovered_audio_queue_push(0xaeU);
    recovered_audio_queue_push(value >> 8);
    recovered_audio_queue_push(value);
    recovered_audio_queue_kick();
}
