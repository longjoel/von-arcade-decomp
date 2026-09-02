/* Host-side request framing shared by geometry result builders 0x9e050/0x9e250. */
typedef unsigned int u32;

u32 recovered_geometry_result_request38(const u32 values[3], u32 packet[4])
{
    packet[0] = 0x38U;
    packet[1] = values[0];
    packet[2] = values[1];
    packet[3] = values[2];
    return 4U;
}

u32 recovered_geometry_result_request31(const u32 references[3],
                                        const u32 scratch[3],
                                        u32 packet[7])
{
    packet[0] = 31U;
    packet[1] = references[0];
    packet[2] = references[1];
    packet[3] = references[2];
    packet[4] = scratch[0];
    packet[5] = scratch[1];
    packet[6] = scratch[2];
    return 7U;
}
