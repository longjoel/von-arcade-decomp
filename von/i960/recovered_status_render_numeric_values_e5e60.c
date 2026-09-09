/* Numeric status-render arithmetic recovered from i960 0xe5e60-0xe5ebc. */
#include <stdint.h>

typedef uint32_t recovered_u32;

typedef struct {
    int32_t record_value;
    int32_t first_value;
    int32_t second_remainder;
    int32_t third_value;
    recovered_u32 first_divisor;
    recovered_u32 second_divisor;
    recovered_u32 third_scale;
    recovered_u32 first_formatter;
    recovered_u32 second_formatter;
    recovered_u32 third_formatter;
    recovered_u32 separator_asset;
    recovered_u32 suffix_asset;
} recovered_status_render_numeric_values_result_e5e60;

/*
 * divo/remo are signed operations here.  The source first divides the record
 * by 0xb40, then reduces record/48 modulo 60, and finally computes
 * (record modulo 48 * 33) / 48 before each call to 0xe3a10.
 */
recovered_status_render_numeric_values_result_e5e60
recovered_status_render_numeric_values_e5e60(int32_t record_value)
{
    recovered_status_render_numeric_values_result_e5e60 result;
    int32_t quotient = record_value / 48;

    result.record_value = record_value;
    result.first_value = record_value / 0xb40;
    result.second_remainder = quotient % 60;
    result.third_value = (record_value % 48 * 33) / 48;
    result.first_divisor = 0xb40U;
    result.second_divisor = 48U;
    result.third_scale = 33U;
    result.first_formatter = 0x000e3a10U;
    result.second_formatter = 0x000e3a10U;
    result.third_formatter = 0x000e3a10U;
    result.separator_asset = 0x000e3b5aU;
    result.suffix_asset = 0x000e3b5cU;
    return result;
}
