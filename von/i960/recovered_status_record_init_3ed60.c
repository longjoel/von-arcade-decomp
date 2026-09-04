/* Exact bounded slice of the original i960 routine at 0x3ed60. */
typedef unsigned int u32;
typedef unsigned short u16;

struct recovered_status_record_3ed60 {
    u32 selector;       /* record +0x00, caller g5 */
    u32 table_halfword; /* record +0x02 */
    u32 helper_value;   /* record +0x04, caller g14 */
    u32 caller_byte;    /* record +0x06, caller g3 */
    u32 arg0;           /* record +0x08 */
    u32 arg1;           /* record +0x0c */
    u32 arg2;           /* record +0x10 */
    u32 zero14;         /* record +0x14 */
    u32 zero18;         /* record +0x18 */
    u32 zero1c;         /* record +0x1c */
    u32 arg3;           /* record +0x20, caller g4 */
};

/* Returns the first selected slot, or 23 when the original scan found none. */
u32 recovered_status_record_init_3ed60(const u16 status_words[23],
                                       const u16 table_words[65536],
                                       u32 arg0, u32 arg1, u32 arg2,
                                       u32 caller_byte, u32 final_value,
                                       u32 selector,
                                       u32 helper_value,
                                       struct recovered_status_record_3ed60 *out)
{
    u32 slot;

    for (slot = 0U; slot < 23U; ++slot) {
        if ((status_words[slot] & 0x8000U) != 0U) {
            out->selector = selector;
            out->table_halfword = table_words[selector & 0xffffU];
            out->helper_value = helper_value;
            out->caller_byte = caller_byte & 0xffU;
            out->arg0 = arg0;
            out->arg1 = arg1;
            out->arg2 = arg2;
            out->zero14 = 0U;
            out->zero18 = 0U;
            out->zero1c = 0U;
            out->arg3 = final_value;
            return slot;
        }
    }
    return 23U;
}
