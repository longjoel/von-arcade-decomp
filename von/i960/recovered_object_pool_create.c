/* Recovered i960 object-pool creator at 0x000c5130. */

#include <stdint.h>

typedef struct {
    uint8_t type;
    uint8_t input_byte_01;
    uint8_t input_byte_02;
    uint8_t reserved_03;
    int16_t lookup_halfword;
    int16_t sequence;
    int16_t auxiliary_halfword;
    int16_t input_halfword_06;
    int16_t input_halfword_08;
    uint16_t source_handle;
    uint32_t value_10;
    uint32_t value_14;
    uint32_t value_18;
    uint32_t work_1c;
    uint32_t work_20;
    uint32_t work_24;
    uint32_t derived_value;
} recovered_object_pool_slot;

/*
 * The ROM scans offsets 0..0x3e8 in 0x2c-byte steps.  The two lookup tables
 * are passed in as decoded ROM views: mode_table is indexed by type*8+mode,
 * while class_table is indexed by type*8+mode and supplies the byte used to
 * select the signed halfword table.
 *
 * Returns the allocated slot number, or -1 when all 37 slots are occupied.
 * The call to 0xf5058 is an external bookkeeping/helper call; its preserved
 * caller context is represented here by auxiliary_halfword.
 */
int recovered_object_pool_create(
    recovered_object_pool_slot pool[37],
    const recovered_object_pool_slot *input,
    uint32_t mode,
    const uint32_t mode_table[256 * 8],
    const uint8_t class_table[256 * 8],
    const int16_t halfword_table[256],
    uint16_t *sequence_counter,
    int16_t auxiliary_halfword)
{
    uint32_t slot_index;
    uint8_t class_code;
    uint8_t halfword_index;
    recovered_object_pool_slot *slot;

    for (slot_index = 0; slot_index < 37; ++slot_index) {
        slot = &pool[slot_index];
        if (slot->lookup_halfword != 0)
            continue;

        slot->input_byte_01 = input->type;
        slot->input_byte_02 = input->input_byte_01;
        slot->value_10 = input->value_10;
        slot->value_14 = input->value_14;
        slot->value_18 = input->value_18;
        slot->derived_value = mode_table[(uint32_t)input->type * 8U + mode];

        class_code = class_table[(uint32_t)input->type * 8U + mode];
        halfword_index = (uint8_t)(class_code & input->type);
        slot->work_1c = 0;
        slot->work_20 = 0;
        slot->work_24 = 0;
        slot->type = class_code;
        slot->lookup_halfword = halfword_table[halfword_index];
        slot->auxiliary_halfword = auxiliary_halfword;
        slot->input_halfword_06 = input->input_halfword_06;
        slot->input_halfword_08 = input->input_halfword_08;
        slot->source_handle = (uint16_t)(uintptr_t)input;
        slot->sequence = *sequence_counter;
        *sequence_counter = (uint16_t)(*sequence_counter + 1U);
        return (int)slot_index;
    }

    return -1;
}

/*
 * The companion creator at 0xc5240 uses an already-selected byte (g2) and
 * already-computed word (g1).  It shares the pool scan and sequence commit,
 * but only writes the fields visible in that ROM path.
 */
int recovered_object_pool_create_constant(
    recovered_object_pool_slot pool[37],
    const recovered_object_pool_slot *input,
    uint32_t selector,
    uint32_t derived_value,
    const int16_t halfword_table[256],
    uint16_t *sequence_counter)
{
    uint32_t slot_index;
    recovered_object_pool_slot *slot;

    for (slot_index = 0; slot_index < 37; ++slot_index) {
        slot = &pool[slot_index];
        if (slot->lookup_halfword != 0)
            continue;

        slot->value_10 = input->value_10;
        slot->value_14 = input->value_14;
        slot->value_18 = input->value_18;
        slot->derived_value = derived_value;
        slot->work_1c = 0;
        slot->work_20 = 0;
        slot->work_24 = 0;
        slot->type = (uint8_t)selector;
        slot->lookup_halfword = halfword_table[selector & 0xffU];
        slot->input_halfword_08 = input->input_halfword_08;
        slot->source_handle = (uint16_t)(uintptr_t)input;
        slot->sequence = *sequence_counter;
        *sequence_counter = (uint16_t)(*sequence_counter + 1U);
        return (int)slot_index;
    }

    return -1;
}

/* The third creator at 0xc5310 swaps the input's trailing value words. */
int recovered_object_pool_create_rebased(
    recovered_object_pool_slot pool[37],
    const recovered_object_pool_slot *input,
    uint32_t mode,
    uint32_t selector,
    const uint32_t mode_table[256 * 8],
    const uint8_t class_table[256 * 8],
    const int16_t halfword_table[256],
    uint16_t *sequence_counter,
    int16_t auxiliary_halfword)
{
    uint32_t slot_index;
    uint8_t class_code;
    recovered_object_pool_slot *slot;

    for (slot_index = 0; slot_index < 37; ++slot_index) {
        slot = &pool[slot_index];
        if (slot->lookup_halfword != 0)
            continue;

        slot->value_10 = input->value_14;
        slot->value_14 = input->value_18;
        slot->value_18 = input->work_1c;
        slot->derived_value = mode_table[mode * 8U + selector];
        class_code = class_table[selector * 8U + mode];
        slot->work_1c = 0;
        slot->work_20 = 0;
        slot->work_24 = 0;
        slot->auxiliary_halfword = auxiliary_halfword;
        slot->input_halfword_06 = auxiliary_halfword;
        slot->input_halfword_08 = auxiliary_halfword;
        slot->type = class_code;
        slot->lookup_halfword = halfword_table[class_code];
        slot->source_handle = (uint16_t)input->work_1c;
        slot->sequence = *sequence_counter;
        *sequence_counter = (uint16_t)(*sequence_counter + 1U);
        return (int)slot_index;
    }

    return -1;
}

typedef void (*recovered_object_pool_handler)(recovered_object_pool_slot *slot);

/* Pool-wide dispatch loop at 0xc5530. */
uint32_t recovered_object_pool_dispatch(
    recovered_object_pool_slot pool[37],
    recovered_object_pool_handler handlers[256])
{
    uint32_t slot_index;
    uint32_t dispatched = 0;

    for (slot_index = 0; slot_index < 37; ++slot_index) {
        recovered_object_pool_slot *slot = &pool[slot_index];
        if (slot->lookup_halfword <= 0 || slot->type > 60U)
            continue;
        handlers[slot->type](slot);
        ++dispatched;
    }
    return dispatched;
}

/* Pool/side-table reset at 0xc55a8. */
void recovered_object_pool_reset(recovered_object_pool_slot pool[37],
                                 uint32_t side_table[8])
{
    uint32_t index;

    for (index = 0; index < 37; ++index) {
        pool[index].lookup_halfword = -1;
        pool[index].type = 0;
    }
    for (index = 0; index < 8; ++index)
        side_table[index] = UINT32_MAX;
}
