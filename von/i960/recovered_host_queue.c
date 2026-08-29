/* Recovered host byte-queue initialization at i960 0x18488-0x184d4. */

typedef unsigned long u32;
typedef unsigned short u16;
typedef unsigned char u8;

#define QUEUE_BYTES       ((volatile u8 *)0x00504c60)
#define QUEUE_READ_INDEX  (*(volatile u32 *)0x00504c70)
#define QUEUE_WRITE_INDEX (*(volatile u32 *)0x00504c74)
#define QUEUE_SENTINEL    (*(volatile u16 *)0x00504c78)
#define HOST_SENTINEL     (*(volatile u16 *)0x00503312)

void recovered_host_queue_initialize(void)
{
    u32 index;

    for (index = 0; index < 16; ++index)
        QUEUE_BYTES[index] = 0xffU;
    QUEUE_WRITE_INDEX = 0;
    QUEUE_SENTINEL = 0x00ffU;
    QUEUE_READ_INDEX = 0;
    HOST_SENTINEL = 0x00ffU;
}
