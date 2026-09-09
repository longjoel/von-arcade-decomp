/* Three runtime feature gates recovered from i960 0xeada0-eae58. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 variant;
    recovered_u32 entry_address;
    recovered_u32 flag_address;
    recovered_u32 fallback_address;
    recovered_u32 flag_bit_mask;
    recovered_u32 fallback_bit_mask;
    recovered_u32 flag_byte;
    recovered_u32 fallback_word;
    recovered_u32 accepted;
    recovered_u32 returned_value;
    recovered_u32 continuation_target;
} recovered_runtime_flag_gates_result_eada0;

recovered_runtime_flag_gates_result_eada0
recovered_runtime_flag_gates_eada0(recovered_u32 variant,
                                   recovered_u32 flag_byte,
                                   recovered_u32 fallback_word,
                                   recovered_u32 continuation_target)
{
    recovered_runtime_flag_gates_result_eada0 result;

    result.variant = variant;
    result.flag_byte = flag_byte & 0xffU;
    result.fallback_word = fallback_word;
    result.continuation_target = continuation_target;
    result.entry_address = 0U;
    result.flag_address = 0U;
    result.fallback_address = 0U;
    result.flag_bit_mask = 0U;
    result.fallback_bit_mask = 0U;
    switch (variant) {
    case 0U:
        result.entry_address = 0x000eada0U;
        result.flag_address = 0x005023f0U;
        result.fallback_address = 0x005024b4U;
        result.flag_bit_mask = 0x08U;
        result.fallback_bit_mask = 0x02U;
        break;
    case 1U:
        result.entry_address = 0x000eade0U;
        result.flag_address = 0x005023f0U;
        result.fallback_address = 0x005024b4U;
        result.flag_bit_mask = 0x04U;
        result.fallback_bit_mask = 0x01U;
        break;
    case 2U:
        result.entry_address = 0x000eae20U;
        result.flag_address = 0x00502480U;
        result.fallback_address = 0x005024b8U;
        result.flag_bit_mask = 0x04U;
        result.fallback_bit_mask = 0x01U;
        break;
    default:
        break;
    }
    result.accepted = ((result.flag_byte & result.flag_bit_mask) != 0U) ||
                      ((result.fallback_word & result.fallback_bit_mask) != 0U);
    result.returned_value = result.accepted;
    return result;
}
