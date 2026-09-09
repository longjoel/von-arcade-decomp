/* Exact signature check recovered from the original i960 slice at 0x2040. */

#include <stdint.h>

struct recovered_rom_signature_probe_plan_2040 {
    uint32_t first_source;
    uint32_t second_source;
    uint32_t probe_bytes;
    uint32_t first_result;
    uint32_t second_result;
    uint32_t second_probe_performed;
    uint32_t accepted;
    uint32_t return_value;
    uint32_t continuation;
};

uint32_t recovered_rom_signature_probe_plan_2040(
    uint32_t first_result, uint32_t second_result,
    struct recovered_rom_signature_probe_plan_2040 *plan)
{
    struct recovered_rom_signature_probe_plan_2040 local;

    local.first_source = 0x00002030U;
    local.second_source = 0x00002038U;
    local.probe_bytes = 4U;
    local.first_result = first_result;
    local.second_result = second_result;
    local.second_probe_performed = first_result != 0U ? 1U : 0U;
    local.accepted = first_result == 0U || second_result == 0U ? 1U : 0U;
    local.return_value = local.accepted;
    local.continuation = local.accepted != 0U ? 0x00002070U : 0x00002078U;
    if (plan != (void *)0)
        *plan = local;
    return 1U;
}

/* Return one when the four-byte candidate is either accepted ROM signature. */
uint32_t recovered_rom_signature_compare_2040(const uint8_t candidate[4])
{
    static const uint8_t sega[4] = { 'S', 'E', 'G', 'A' };
    static const uint8_t s32a[4] = { 'S', '3', '2', 'A' };
    uint32_t sega_match = 1U;
    uint32_t s32a_match = 1U;
    uint32_t i;

    for (i = 0U; i < 4U; ++i) {
        sega_match &= (candidate[i] == sega[i]);
        s32a_match &= (candidate[i] == s32a[i]);
    }
    return sega_match | s32a_match;
}
