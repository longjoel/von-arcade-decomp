/* Exact bounded pure portion of the original i960 service at 0x3f550. */
typedef unsigned int u32;
typedef unsigned short u16;

struct recovered_status_record_3f550 {
    u32 selector;       /* record +0x00, caller flag selects 17 or 18 */
    u32 table_halfword; /* record +0x02, selector-masked 0x3eca0 lookup */
    u32 arg0;           /* record +0x08, caller g0 */
    u32 arg1;           /* record +0x0c, caller g1 */
    u32 arg2;           /* record +0x10, caller g2 */
    u32 zero14;         /* record +0x14 */
    u32 zero18;         /* record +0x18 */
    u32 arg3;           /* record +0x1c, caller g3 */
    u32 arg4;           /* record +0x20, caller g4 */
};

/*
 * The original walks the 23 records at 0x51ad10 in 0x24-byte steps.  The
 * signed status halfword at offset two is negative when a slot is available.
 * The service fills the first available slot, choosing selector 18 when the
 * caller flag is nonzero and selector 17 otherwise.  Its g13 allocation
 * counter advances by nine for occupied slots and is bounded by 0xcf; the
 * pure contract exposes that counter through allocation_units.  The
 * continuation, pool writes, and external helper effects are intentionally
 * outside this host-testable contract.
 *
 * Returns the selected slot, or 23 when no slot was selected before the
 * bounded walk ended.
 */
u32 recovered_status_record_fill_3f550(const u16 status_words[23],
                                       const u16 table_words[65536],
                                       u32 caller_flag,
                                       u32 arg0, u32 arg1, u32 arg2,
                                       u32 arg3, u32 arg4,
                                       struct recovered_status_record_3f550 *out,
                                       u32 *allocation_units)
{
    u32 slot;
    u32 units = 0U;

    for (slot = 0U; slot < 23U; ++slot) {
        if ((status_words[slot] & 0x8000U) != 0U) {
            const u32 selector = caller_flag != 0U ? 18U : 17U;
            out->selector = selector;
            out->table_halfword = table_words[selector];
            out->arg0 = arg0;
            out->arg1 = arg1;
            out->arg2 = arg2;
            out->zero14 = 0U;
            out->zero18 = 0U;
            out->arg3 = arg3;
            out->arg4 = arg4;
            if (allocation_units != 0) {
                *allocation_units = units;
            }
            return slot;
        }
        units += 9U;
        if (units > 0xcfU) {
            break;
        }
    }
    if (allocation_units != 0) {
        *allocation_units = units;
    }
    return 23U;
}
