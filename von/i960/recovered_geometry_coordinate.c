/*
 * Recovered from i960 routine 0x0006ece0.
 *
 * The real routine talks to the SHARC FIFO at 0x884000.  The callback keeps
 * that device boundary explicit while making the coordinate quantization,
 * lookup record layout, output writes, and packet order testable on the host.
 */

typedef unsigned int u32;
typedef unsigned short u16;

typedef struct recovered_geometry_coordinate_record {
    u16 output_x;
    u16 output_y;
    u32 packet_1;
    u32 packet_2;
    u32 packet_3;
    u32 packet_4;
} recovered_geometry_coordinate_record;

typedef u32 (*recovered_geometry_fifo_read)(void *opaque);
typedef void (*recovered_geometry_fifo_write)(void *opaque, u32 value);

/* The i960 routine returns the IEEE-754 bit pattern for 99999.0 on reject. */
#define RECOVERED_GEOMETRY_COORDINATE_REJECT 0x47c34f80U

static int recovered_geometry_truncate_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return (int)input.value;
}

/*
 * 0x6ece0: quantize two float coordinates, look up a 20-byte record, write
 * the two halfwords at g2/g3, and submit the six-word 0x35 continuation.
 * Returns the final FIFO read, or 99999.0f's raw bits when out of range.
 */
u32 recovered_geometry_coordinate_submit(
    u32 x_bits,
    u32 y_bits,
    u16 *output_x,
    u16 *output_y,
    const recovered_geometry_coordinate_record *table,
    recovered_geometry_fifo_read fifo_read,
    recovered_geometry_fifo_write fifo_write,
    void *opaque)
{
    int x = recovered_geometry_truncate_float(x_bits);
    int y = recovered_geometry_truncate_float(y_bits);
    u32 x_half;
    u32 y_half;
    u32 index;
    u32 returned_index;
    const recovered_geometry_coordinate_record *record;

    /* The original unsigned shift/mask admits exactly 0..1023. */
    if (x < 0 || x >= 1024 || y < 0 || y >= 1024)
        return RECOVERED_GEOMETRY_COORDINATE_REJECT;

    x_half = (u32)x >> 1;
    y_half = (u32)y >> 1;
    index = (y_half << 9) + x_half;

    fifo_write(opaque, 0x41U);
    fifo_write(opaque, index);
    returned_index = fifo_read(opaque);
    record = &table[returned_index];

    *output_x = record->output_x;
    *output_y = record->output_y;

    fifo_write(opaque, 53U);
    fifo_write(opaque, record->packet_1);
    fifo_write(opaque, x_bits);
    fifo_write(opaque, record->packet_3);
    fifo_write(opaque, y_bits);
    fifo_write(opaque, record->packet_4);
    fifo_write(opaque, record->packet_4);
    fifo_write(opaque, record->packet_2 ^ 0x80000000U);
    return fifo_read(opaque);
}
