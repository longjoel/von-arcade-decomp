/* Command-record table writer at i960 0x9b288. */
#include "recovered_command_record_9b2xx.h"

typedef struct {
    uint16_t value_8;
    recovered_u32 value_10;
    recovered_u32 value_14;
    recovered_u32 value_18;
} recovered_command_record_input_9b288;

/* The index is first normalized to its low nibble and published back to the
 * cursor global before the selected 16-byte record is populated. */
void recovered_command_record_write_9b288(
    recovered_command_record_table_9b2xx *table,
    const recovered_command_record_input_9b288 *input)
{
    recovered_u32 slot = table->cursor & 0xfU;
    recovered_command_record_9b2xx *record = &table->record[slot];

    table->cursor = slot;
    record->active = 1U;
    record->reserved = 0U;
    record->value_2 = input->value_8;
    record->value_4 = input->value_10;
    record->value_8 = input->value_14;
    table->cursor = slot + 1U;
    record->value_c = input->value_18;
}
