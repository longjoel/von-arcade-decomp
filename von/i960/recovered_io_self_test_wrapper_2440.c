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
    /* 0x2478 is reached when the primary CRC fails or its signature compare
     * returns zero; this is the alternate-record fallback. */
    plan->second_record_signature_checked =
        (first_crc_match == 0U || first_signature_match == 0U) &&
        second_crc_match != 0U ? 1U : 0U;
    plan->failure_latch_cleared =
        (first_crc_match == 0U || first_signature_match == 0U) &&
        (second_crc_match == 0U || second_signature_match == 0U) ? 1U : 0U;
    plan->record_copy_called =
        (first_crc_match == 0U || first_signature_match == 0U) &&
        second_crc_match != 0U && second_signature_match != 0U ? 1U : 0U;
    plan->device_ready =
        first_crc_match != 0U && first_signature_match != 0U &&
        second_crc_match != 0U && second_signature_match != 0U ? 1U : 0U;
}

struct recovered_io_wrapper_detailed_plan {
    u32 input_initializer_called;
    u32 initial_primary_signature_checked;
    u32 initial_alternate_crc_checked;
    u32 initial_alternate_signature_checked;
    u32 initial_pair_compare_called;
    u32 failure_latch_cleared;
    u32 post_primary_crc_checked;
    u32 post_primary_byte_compare_checked;
    u32 post_alternate_crc_checked;
    u32 post_alternate_byte_compare_checked;
    u32 post_pair_compare_called;
    u32 record_copy_called;
    u32 first_table_validation_passed;
    u32 second_table_validation_passed;
    u32 reverse_table_copy_called;
    u32 table_recovery_initializer_called;
    u32 table_success_initializer_called;
    u32 table_copy_called;
    u32 startup_validation_fallback_called;
    u32 final_service_called;
};

/* Detailed caller plan for 0x2440-0x26dc. Every argument is a normalized
 * result from one ROM helper: nonzero means that compare passed. */
void recovered_io_self_test_wrapper_detailed_plan(
    u32 initial_primary_crc_match, u32 initial_primary_signature_match,
    u32 initial_alternate_crc_match, u32 initial_alternate_signature_match,
    u32 post_primary_crc_match, u32 post_primary_byte_match,
    u32 post_alternate_crc_match, u32 post_alternate_byte_match,
    u32 first_table_compare_match, u32 first_table_length_match,
    u32 first_table_crc_match, u32 second_table_compare_match,
    u32 second_table_length_match, u32 second_table_crc_match,
    struct recovered_io_wrapper_detailed_plan *plan)
{
    u32 initial_alt_path = initial_primary_crc_match == 0U ||
                           initial_primary_signature_match == 0U;
    u32 initial_alt_passed = initial_alt_path &&
                             initial_alternate_crc_match != 0U &&
                             initial_alternate_signature_match != 0U;
    u32 post_primary_passed = post_primary_crc_match != 0U &&
                              post_primary_byte_match != 0U;
    u32 post_alternate_path = post_primary_passed == 0U;
    u32 post_alternate_passed = post_alternate_path &&
                                post_alternate_crc_match != 0U &&
                                post_alternate_byte_match != 0U;

    plan->input_initializer_called = 1U;
    plan->initial_primary_signature_checked =
        initial_primary_crc_match != 0U ? 1U : 0U;
    plan->initial_alternate_crc_checked = initial_alt_path;
    plan->initial_alternate_signature_checked = initial_alt_path &&
                                                initial_alternate_crc_match != 0U;
    plan->initial_pair_compare_called = initial_alt_passed;
    plan->failure_latch_cleared = initial_alt_path && !initial_alt_passed;

    plan->post_primary_crc_checked = 1U;
    plan->post_primary_byte_compare_checked = post_primary_crc_match != 0U;
    plan->post_alternate_crc_checked = post_alternate_path;
    plan->post_alternate_byte_compare_checked = post_alternate_path &&
                                                post_alternate_crc_match != 0U;
    plan->post_pair_compare_called = post_alternate_passed;
    plan->record_copy_called = post_alternate_passed;

    plan->first_table_validation_passed = first_table_compare_match != 0U &&
                                          first_table_length_match != 0U &&
                                          first_table_crc_match != 0U;
    plan->second_table_validation_passed = second_table_compare_match != 0U &&
                                           second_table_length_match != 0U &&
                                           second_table_crc_match != 0U;
    plan->reverse_table_copy_called = plan->first_table_validation_passed == 0U;
    plan->table_recovery_initializer_called = plan->second_table_validation_passed == 0U;
    plan->table_success_initializer_called = plan->second_table_validation_passed != 0U;
    plan->table_copy_called = 1U;
    plan->startup_validation_fallback_called = post_alternate_passed == 0U;
    plan->final_service_called = 1U;
}
