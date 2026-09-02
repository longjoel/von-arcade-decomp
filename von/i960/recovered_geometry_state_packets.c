/*
 * Concrete host-side packet chain observed at i960 0xcaf08 and its
 * neighboring emitters. The packet contents are recovered; the geometric
 * meaning of the three services remains provisional.
 */
typedef unsigned int u32;

/* Emit the observed 0x23 -> 0x12 -> 0x0a state-update chain. */
u32 recovered_geometry_state_update_chain(const u32 update[3],
                                          const u32 tail[3],
                                          const u32 scalar[2],
                                          u32 packet[11])
{
    packet[0] = 0x23U;
    packet[1] = update[0];
    packet[2] = update[1];
    packet[3] = update[2];
    packet[4] = 0x12U;
    packet[5] = tail[0];
    packet[6] = tail[1];
    packet[7] = tail[2];
    packet[8] = 0x0aU;
    packet[9] = scalar[0];
    packet[10] = scalar[1];
    return 11U;
}
