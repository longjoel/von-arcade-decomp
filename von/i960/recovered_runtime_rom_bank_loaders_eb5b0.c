/* Runtime ROM-bank loader family recovered from i960 0xeb5b0-eb824. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 loader_index;
    recovered_u32 loader_address;
    recovered_u32 source_base;
    recovered_u32 source_word_count_immediate;
    recovered_u32 copied_halfword_count;
    recovered_u32 copied_byte_count;
    recovered_u32 source_publication_address;
    recovered_u32 destination_address;
    recovered_u32 selected_source_address;
    recovered_u32 reset_copy_helper;
    recovered_u32 return_target;
} recovered_runtime_rom_bank_loader_result_eb5b0;

int
recovered_runtime_rom_bank_loader_eb5b0(recovered_u32 loader_index,
                                        recovered_runtime_rom_bank_loader_result_eb5b0 *result)
{
    static const recovered_u32 loader_address[8] = {
        0x000eb5b0U, 0x000eb600U, 0x000eb650U, 0x000eb6a0U,
        0x000eb6f0U, 0x000eb740U, 0x000eb790U, 0x000eb7e0U
    };
    static const recovered_u32 source_base[8] = {
        0x005e0000U, 0x005c0000U, 0x005a0000U, 0x00580000U,
        0x00560000U, 0x00540000U, 0x00520000U, 0x00502000U
    };
    static const recovered_u32 source_word_count_immediate[8] = {
        0xffffU, 0xffffU, 0xffffU, 0xffffU,
        0xffffU, 0xffffU, 0xffffU, 0xefffU
    };
    recovered_runtime_rom_bank_loader_result_eb5b0 local;

    if (loader_index >= 8U)
        return 0;
    local.loader_index = loader_index;
    local.loader_address = loader_address[loader_index];
    local.source_base = source_base[loader_index];
    local.source_word_count_immediate = source_word_count_immediate[loader_index];
    local.copied_halfword_count = local.source_word_count_immediate + 1U;
    local.copied_byte_count = local.copied_halfword_count << 1U;
    local.source_publication_address = 0x00501cc0U;
    local.destination_address = 0x00501cc4U;
    local.selected_source_address = 0x00501cc4U;
    local.reset_copy_helper = 0x000eb510U;
    local.return_target = loader_index == 0U ? 0x000eb5f4U :
        loader_address[loader_index] + 0x44U;
    if (result != (recovered_runtime_rom_bank_loader_result_eb5b0 *)0)
        *result = local;
    return 1;
}
