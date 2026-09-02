/* The 0x9e050/0x9e250 flag-set branch uses i960 SUBR:
 * object reference minus the first geometry response, modulo 32 bits. */
typedef unsigned int u32;
typedef unsigned short u16;

void recovered_geometry_result_reference_delta(const u32 references[3],
                                               const u32 responses[3],
                                               u32 delta[3])
{
    delta[0] = references[0] - responses[0];
    delta[1] = references[1] - responses[1];
    delta[2] = references[2] - responses[2];
}

/*
 * The two responses from the flag-set follow-up request are written with
 * i960 STOS, at paired-record byte offsets +0x06 and +0x08. Model the record
 * as halfwords so the low-16-bit, unaligned placement is explicit.
 */
void recovered_geometry_result_delta_response_copy(const u32 responses[2],
                                                   u16 paired_record[5])
{
    paired_record[0x06U / 2U] = (u16)responses[0];
    paired_record[0x08U / 2U] = (u16)responses[1];
}
