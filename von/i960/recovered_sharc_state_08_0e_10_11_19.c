/* SHARC state services: 08 init, 0e upload, 10 identity init,
 * 11 readback, 19 counter.
 *
 * Handler entries from the live dispatch table (DM 0x30000+opcode
 * snapshot): 08->PM 0x201bf, 0e->PM 0x20271, 10->PM 0x2028e,
 * 11->PM 0x2029e, 19->PM 0x20397 (listing file offsets 0x1bf, 0x271,
 * 0x28e, 0x29e, 0x397).
 *
 * - 08 (0x1bf): R0 = 0, DM(0x30100) = R0 (upload counter reset),
 *   then in the RTS delay slots R0 = 0x30200,
 *   DM(0x30101) = R0 (upload-record pointer reset). No FIFO payload,
 *   no response.
 * - 0e (0x271): reads four FIFO words into R0-R3 and stores them at
 *   absolute DM 0x30105-0x30108 in order (final two stores in RTS
 *   delay slots). Pinned live by the harness golden effects_exact
 *   for words 11111111/22222222/33333333/44444444.
 * - 10 (0x28e): writes the 12-word diagonal identity (1.0 at offsets
 *   0, 4, 8, else 0.0) through the record pointer DM(0x30101).
 *   Pinned live over garbage pokes by the harness golden.
 * - 11 (0x29e): streams the 12 pointed words to the output FIFO with
 *   FLAG1 flow control, plus the RTS delay-slot word (a 13th
 *   DM(I7,M1) read of the word following the record; observed 0x0
 *   after identity init). No DM writes of its own.
 * - 19 (0x397): emits DM(0x30100) to the output FIFO first (RTS delay
 *   slots), with no FIFO payload. Proved live by poking the counter
 *   to 5 and draining 00000005 back.
 *
 * All words move verbatim (no float interpretation), so both MAME
 * engines agree bit-for-bit here and plain integer copies model the
 * hardware exactly. Contract: the caller mirrors the SHARC DM
 * windows as host arrays.
 */

typedef unsigned int u32;

#define SHARC_COUNTER_ADDR 0x30100U
#define SHARC_RECORD_PTR_ADDR 0x30101U
#define SHARC_RECORD_BASE 0x30200U
#define SHARC_UPLOAD_BASE 0x30105U
#define SHARC_FLOAT_ONE_BITS 0x3f800000U
#define SHARC_STATE_WORDS 12U

/* Opcode 0x08: counter reset plus record-pointer reset. dm30100[0] is
 * DM(0x30100), dm30100[1] is DM(0x30101). */
void sharc_service_init_08(u32 *dm30100)
{
    dm30100[0] = 0U;
    dm30100[1] = SHARC_RECORD_BASE;
}

/* Opcode 0x0e: store four FIFO words at absolute DM 0x30105-0x30108.
 * dm30105[0] is DM(0x30105). */
void sharc_state_upload_0e(u32 *dm30105, const u32 words[4])
{
    int i;
    for (i = 0; i < 4; ++i)
        dm30105[i] = words[i];
}

/* Opcode 0x10: 12-word diagonal identity into the pointed record. */
void sharc_state_init_10(u32 *record)
{
    int i;
    for (i = 0; i < 12; ++i)
        record[i] = (i == 0 || i == 4 || i == 8) ? SHARC_FLOAT_ONE_BITS : 0U;
}

/* Opcode 0x11: stream the 12 record words plus the delay-slot word
 * (rec[12], the word following the record). */
void sharc_state_readback_11(const u32 *record, u32 *out)
{
    int i;
    for (i = 0; i < 12; ++i)
        out[i] = record[i];
    out[12] = record[12];
}

/* Opcode 0x19: emit the upload counter word. */
u32 sharc_state_counter_19(u32 counter)
{
    return counter;
}
