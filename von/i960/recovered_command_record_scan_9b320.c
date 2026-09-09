/* Stateful control prefix of the command-record scanner at i960 0x9b320. */
#include "recovered_command_record_9b2xx.h"

typedef struct {
    recovered_u32 selected_index[16];
    recovered_u32 fifo_prefix[16][7];
    recovered_u32 selected_count;
} recovered_command_scan_result_9b320;

/* Models the table scan and its record-state transition.  The packet/FPU and
 * MMIO payload emitted for each selected record is intentionally external. */
void recovered_command_record_scan_9b320(
    recovered_command_record_table_9b2xx *table,
    recovered_command_scan_result_9b320 *result)
{
    recovered_u32 index;
    result->selected_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        uint8_t active = table->record[index].active;
        if ((active & 0xffU) == 0U)
            continue;
        recovered_u32 selected = result->selected_count++;
        result->selected_index[selected] = index;
        result->fifo_prefix[selected][0] = 5U;
        result->fifo_prefix[selected][1] = 18U;
        result->fifo_prefix[selected][2] = table->record[index].value_4;
        result->fifo_prefix[selected][3] = table->record[index].value_8;
        result->fifo_prefix[selected][4] = table->record[index].value_c;
        result->fifo_prefix[selected][5] = 21U;
        result->fifo_prefix[selected][6] =
            ((recovered_u32)table->record[index].reserved |
             ((recovered_u32)(table->record[index].value_2 & 0xffU) << 8U)) &
            0xffffU;
        if ((active & 0xe0U) == 0U)
            table->record[index].active = 0U;
        else
            table->record[index].active = (uint8_t)(active + 1U);
    }
}
