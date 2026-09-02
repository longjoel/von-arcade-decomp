/*
 * Recovered from i960 routine 0x0006f600.
 *
 * This is the sibling of 0x6ece0: it performs the same coordinate quantizing
 * and 0x41 lookup, but emits the six-word 0x35 continuation directly instead
 * of writing the two halfword fields used by the coordinate submitter.
 */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_35_record_6f600 {
    u32 unused_word0;
    u32 packet_word1;
    u32 packet_word2;
    u32 packet_word3;
    u32 packet_word4;
};

typedef u32 (*recovered_geometry_35_fifo_read)(void *opaque);
typedef void (*recovered_geometry_35_fifo_write)(void *opaque, u32 value);

#define RECOVERED_GEOMETRY_35_REJECT 0x47c34f80U

static int recovered_geometry_35_truncate_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = bits;
    return (int)raw.value;
}

u32 recovered_geometry_35_producer_6f600(
    u32 x_bits, u32 y_bits,
    const struct recovered_geometry_35_record_6f600 *table,
    recovered_geometry_35_fifo_read fifo_read,
    recovered_geometry_35_fifo_write fifo_write,
    void *opaque)
{
    int x = recovered_geometry_35_truncate_float(x_bits);
    int y = recovered_geometry_35_truncate_float(y_bits);
    u32 index;
    u32 returned_index;
    const struct recovered_geometry_35_record_6f600 *record;

    if (x < 0 || x >= 1024 || y < 0 || y >= 1024)
        return RECOVERED_GEOMETRY_35_REJECT;

    index = (((u32)y >> 1) << 9) + ((u32)x >> 1);
    fifo_write(opaque, 0x41U);
    fifo_write(opaque, index);
    returned_index = fifo_read(opaque);
    record = &table[returned_index];

    fifo_write(opaque, record->packet_word1);
    fifo_write(opaque, x_bits);
    fifo_write(opaque, record->packet_word3);
    fifo_write(opaque, y_bits);
    fifo_write(opaque, record->packet_word4);
    fifo_write(opaque, ~record->packet_word2);
    return fifo_read(opaque);
}
