/* Deterministic sibling packet recovered from i960 0x70000-0x700d8. */
typedef unsigned int u32;

u32 recovered_geometry_command_packet_variant(u32 g0, u32 g1, u32 g2, u32 g3,
                                              u32 g4, u32 g6, u32 packet[18])
{
    packet[0] = 0U;
    packet[1] = g4;
    packet[2] = g0;
    packet[3] = g1 + g3;
    packet[4] = g2;
    packet[5] = g0;
    packet[6] = g1 + g3;
    packet[7] = g2;
    packet[8] = 0x01540601U;
    packet[9] = 0x7f000000U;
    packet[10] = 0x3f800000U;
    packet[11] = g0 - g3;
    packet[12] = g1 - g3;
    packet[13] = g2;
    packet[14] = g0 + g3;
    packet[15] = g1 - g3;
    packet[16] = g2;
    packet[17] = 0U;
    (void)g6;
    return 18U;
}
