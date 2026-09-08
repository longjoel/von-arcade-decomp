/* Control/dataflow plan recovered from i960 0x2440-0x26dc. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_io_wrapper_plan {
    u32 input_initializer_called;
    u32 first_record_signature_checked;
    u32 second_record_signature_checked;
    u32 failure_latch_cleared;
    u32 record_copy_called;
    u32 device_ready;
};

/* The arguments are the already-masked results of the helper calls. The
 * wrapper's mapped reads and device writes stay outside this pure plan. */
void recovered_io_self_test_wrapper_plan(
    u32 first_crc_match, u32 first_signature_match,
    u32 second_crc_match, u32 second_signature_match,
    struct recovered_io_wrapper_plan *plan)
{
    plan->input_initializer_called = 1U;
    plan->first_record_signature_checked = first_crc_match != 0U ? 1U : 0U;
    /* 0x2478 is reached only when the first record's signature compare
     * returns zero; this is the alternate-record fallback, not an
     * unconditional second check. */
    plan->second_record_signature_checked =
        first_crc_match != 0U && first_signature_match == 0U ? 1U : 0U;
    plan->failure_latch_cleared =
        first_crc_match != 0U && first_signature_match == 0U &&
        second_crc_match != 0U && second_signature_match == 0U ? 1U : 0U;
    plan->record_copy_called =
        first_crc_match != 0U && first_signature_match == 0U &&
        second_crc_match != 0U && second_signature_match != 0U ? 1U : 0U;
    plan->device_ready =
        first_crc_match != 0U && first_signature_match != 0U &&
        second_crc_match != 0U && second_signature_match != 0U ? 1U : 0U;
}
