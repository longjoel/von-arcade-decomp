/*
 * Exact wrapper recovered from the original i960 slice at 0x3ae0.
 *
 * The two parser records live at 0x5024cc and 0x5024d0 in the original
 * image.  This wrapper invokes the already recovered 0x3a38 transition on
 * them in order, using status bits zero and one respectively.  The parser's
 * indirect return value is deliberately discarded, matching the listing.
 */
#include <stdint.h>

struct recovered_input_byte_parser_3a38_state {
    uint8_t first;
    uint8_t second;
    uint16_t count;
    uint32_t status_mask;
};

extern uint32_t recovered_input_byte_parser_3a38(
    struct recovered_input_byte_parser_3a38_state *state, uint32_t bit);

void recovered_input_byte_parser_wrapper_3ae0(
    struct recovered_input_byte_parser_3a38_state *first,
    struct recovered_input_byte_parser_3a38_state *second)
{
    (void)recovered_input_byte_parser_3a38(first, 0U);
    (void)recovered_input_byte_parser_3a38(second, 1U);
}
