/* Deterministic command packet recovered from i960 0x6ff20-0x6fff8. */
typedef unsigned int u32;

/* packet contains the 18 words written to the geometry FIFO. */
u32 recovered_geometry_command_packet(u32 g0, u32 g1, u32 g2, u32 g3,
                                      u32 g4, u32 g6, u32 packet[18])
{
    packet[0] = 0U;
    packet[1] = g6;
    packet[2] = g4;
    packet[3] = g0;
    packet[4] = g1 - g3;
    packet[5] = g2;
    packet[6] = g0 - g3;
    packet[7] = g1;
    packet[8] = g2;
    packet[9] = 0x01540601U;
    packet[10] = 0x7f000000U;
    packet[11] = 0x3f800000U;
    packet[12] = g0 + g3;
    packet[13] = g1 + g3;
    packet[14] = g2;
    packet[15] = g0;
    packet[16] = g3;
    packet[17] = g2;
    return 18U;
}
