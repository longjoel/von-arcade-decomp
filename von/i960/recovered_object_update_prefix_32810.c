/* Runnable object-update prefix, recovered from i960 0x32810-0x32924.
 *
 * Copies the related record's x/z into object+0xa4/+0xa8, emits the SHARC
 * opcode-31 packet (self x/z and related x/z) and stores the response at
 * object+0x7c, emits the opcode-10 delta packet and stores the signed
 * response at object+0x84, publishes the height delta at object+0x80, the
 * range flag at object+0x86 and 0xff at object+0x1fc. The mode==3 early-out
 * and the action dispatch that follow are handled by the caller.
 */

typedef unsigned int u32;
typedef unsigned short u16;

#define RECOVERED_OBJECT_UPDATE_PREFIX_FIFO (*(volatile u32 *)0x00884000U)

static float recovered_object_update_prefix_float_read(volatile unsigned char *object, u32 offset)
{
    union {
        u32 bits;
        float value;
    } value;

    value.bits = *(volatile u32 *)(object + offset);
    return value.value;
}

static u32 recovered_object_update_prefix_float_bits(float value)
{
    union {
        u32 bits;
        float value;
    } out;

    out.value = value;
    return out.bits;
}

/* Range flag from 0x328fc-0x32918: ((0x9ff + (s16)delta - (s16)facing) & 0xffff)
 * compared against 0x13fe; 1 when the masked value is greater. */
u32 recovered_object_update_prefix_32810_range(u32 delta_response, u32 facing)
{
    u32 value = (0x9ffU + (u32)(short)(u16)delta_response - (u32)(short)(u16)facing) & 0xffffU;

    return value > 0x13feU ? 1U : 0U;
}

void recovered_object_update_prefix_32810_run(volatile unsigned char *object)
{
    volatile unsigned char *related =
        (volatile unsigned char *)(unsigned long)*(volatile u32 *)(object + 0x74);
    u32 response;

    *(volatile u32 *)(object + 0xa4) = *(volatile u32 *)(related + 0x08);
    *(volatile u32 *)(object + 0xa8) = *(volatile u32 *)(related + 0x10);

    /* opcode 31: self x, related x, 0, 0, self z, related z. */
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = 31U;
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = *(volatile u32 *)(object + 0x08);
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = *(volatile u32 *)(related + 0x08);
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = 0U;
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = 0U;
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = *(volatile u32 *)(object + 0x10);
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = *(volatile u32 *)(related + 0x10);
    response = RECOVERED_OBJECT_UPDATE_PREFIX_FIFO;
    *(volatile u32 *)(object + 0x7c) = response;

    /* opcode 10: (related.z - self.z), (self.x - related.x), stored signed. */
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = 10U;
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = recovered_object_update_prefix_float_bits(
        recovered_object_update_prefix_float_read(related, 0x10)
        - recovered_object_update_prefix_float_read(object, 0x10));
    RECOVERED_OBJECT_UPDATE_PREFIX_FIFO = recovered_object_update_prefix_float_bits(
        recovered_object_update_prefix_float_read(object, 0x08)
        - recovered_object_update_prefix_float_read(related, 0x08));
    response = RECOVERED_OBJECT_UPDATE_PREFIX_FIFO;
    *(volatile u16 *)(object + 0x84) = (u16)response;

    *(volatile u32 *)(object + 0x80) = recovered_object_update_prefix_float_bits(
        recovered_object_update_prefix_float_read(object, 0x0c)
        - recovered_object_update_prefix_float_read(related, 0x0c));

    *(volatile u16 *)(object + 0x86) = (u16)recovered_object_update_prefix_32810_range(
        response, *(volatile u16 *)(object + 0x184));
    *(volatile u16 *)(object + 0x1fc) = 0xffU;
}
