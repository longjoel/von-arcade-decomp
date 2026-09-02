/* Common three-word FIFO tail at i960 0x00070950. */
typedef unsigned int u32;

u32 recovered_geometry_packet_tail(u32 pending_g4, u32 pending_g5,
                                   u32 packet[3])
{
    packet[0] = pending_g4;
    packet[1] = pending_g5;
    packet[2] = 0U;
    return 3U;
}
