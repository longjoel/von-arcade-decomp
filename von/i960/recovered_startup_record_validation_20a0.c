/* Startup record validation/copy control recovered from i960 0x20a0-0x2248. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_record_validation_plan {
    u32 input_initializer_called;
    u32 primary_signature_checked;
    u32 alternate_crc_checked;
    u32 alternate_signature_checked;
    u32 record_pair_compare_called;
    u32 failure_latch_cleared;
    u32 record_fragments_copied;
    u32 primary_crc_recomputed;
    u32 input_post_service_called;
    u32 returned_latch;
    u32 copy_fragment_count;
    u32 copy_lengths[4];
    u32 copy_destinations[4];
    u32 copy_sources[4];
};

/* Helper results are supplied by the caller so CRC, signature, and mapped
 * memory behavior remain explicit.  Nonzero means the corresponding compare
 * passed, matching cmpibne/cmpibe control in the ROM. */
void recovered_startup_record_validation_plan(
    u32 primary_crc_match, u32 primary_signature_match,
    u32 alternate_crc_match, u32 alternate_signature_match,
    struct recovered_startup_record_validation_plan *plan)
{
    plan->input_initializer_called = 1U;
    plan->primary_signature_checked = primary_crc_match != 0U ? 1U : 0U;
    plan->alternate_crc_checked =
        primary_crc_match == 0U || primary_signature_match == 0U;
    plan->alternate_signature_checked =
        plan->alternate_crc_checked != 0U && alternate_crc_match != 0U;
    plan->record_pair_compare_called =
        plan->alternate_signature_checked != 0U &&
        alternate_signature_match != 0U ? 1U : 0U;
    plan->failure_latch_cleared =
        plan->alternate_crc_checked != 0U &&
        (alternate_crc_match == 0U || alternate_signature_match == 0U) ? 1U : 0U;
    plan->record_fragments_copied = plan->failure_latch_cleared == 0U ? 1U : 0U;
    plan->primary_crc_recomputed = plan->record_fragments_copied;
    plan->input_post_service_called = plan->record_fragments_copied;
    plan->returned_latch = 1U;

    plan->copy_fragment_count = plan->record_fragments_copied != 0U ? 4U : 0U;
    plan->copy_lengths[0] = 4U;
    plan->copy_lengths[1] = 4U;
    plan->copy_lengths[2] = 20U;
    plan->copy_lengths[3] = 14U;
    plan->copy_destinations[0] = 0x00502400U;
    plan->copy_destinations[1] = 0x00502404U;
    plan->copy_destinations[2] = 0x00502410U;
    plan->copy_destinations[3] = 0x00502424U;
    plan->copy_sources[0] = 0x00002030U;
    plan->copy_sources[1] = 0x00002098U;
    plan->copy_sources[2] = 0x01d00016U;
    plan->copy_sources[3] = 0x01d0002aU;
}

struct recovered_startup_record_retry_plan {
    u32 input_initializer_called;
    u32 primary_signature_checked;
    u32 alternate_crc_checked;
    u32 alternate_signature_checked;
    u32 record_pair_compare_called;
    u32 returned_latch;
};

void recovered_startup_record_retry_plan(
    u32 primary_crc_match, u32 primary_signature_match,
    u32 alternate_crc_match, u32 alternate_signature_match,
    struct recovered_startup_record_retry_plan *plan)
{
    plan->input_initializer_called = 1U;
    plan->primary_signature_checked = primary_crc_match != 0U ? 1U : 0U;
    plan->alternate_crc_checked =
        primary_crc_match == 0U || primary_signature_match == 0U;
    plan->alternate_signature_checked =
        plan->alternate_crc_checked != 0U && alternate_crc_match != 0U ? 1U : 0U;
    plan->record_pair_compare_called =
        plan->alternate_signature_checked != 0U &&
        alternate_signature_match != 0U ? 1U : 0U;
    plan->returned_latch =
        (primary_crc_match != 0U && primary_signature_match != 0U) ||
        plan->record_pair_compare_called;
}
