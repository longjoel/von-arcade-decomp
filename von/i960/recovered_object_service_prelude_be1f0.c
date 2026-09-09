/* Deterministic paired-service prelude recovered from i960 0xbe1f0-0xbe304. */
#include "recovered_common.h"

typedef struct {
    uint8_t active[2][32];
    uint16_t record_halfword[2][32];
    recovered_u32 status_48[2];
    recovered_u32 status_callback_result[2];
} recovered_object_service_prelude_input_be1f0;

typedef struct {
    recovered_u32 service_object[128];
    recovered_u32 service_index[128];
    recovered_u32 service_selector[128];
    recovered_u32 service_call_count;
    recovered_u32 status_call_object[2];
    recovered_u32 status_call_count;
    recovered_u32 status_publication[2];
} recovered_object_service_prelude_result_be1f0;

/*
 * The first object is scanned before the linked object, each with a 0x20
 * byte stride. Once set by the bit-8 arm, g1 remains 7 for the low-bit arm,
 * so every c5130 request in this prefix carries selector 7. The c5310
 * status service is requested after both scans for each nonzero +0x48 byte.
 */
void recovered_object_service_prelude_be1f0(
    const recovered_object_service_prelude_input_be1f0 *input,
    recovered_object_service_prelude_result_be1f0 *result)
{
    recovered_u32 object;
    recovered_u32 index;

    result->service_call_count = 0U;
    result->status_call_count = 0U;
    for (object = 0U; object < 2U; ++object) {
        for (index = 0U; index < 32U; ++index) {
            recovered_u32 halfword = input->record_halfword[object][index];
            if (input->active[object][index] == 0U)
                continue;
            if ((halfword & 0x08U) != 0U) {
                recovered_u32 call = result->service_call_count++;
                result->service_object[call] = object;
                result->service_index[call] = index;
                result->service_selector[call] = 7U;
            }
            if ((halfword & 0x07U) != 0U) {
                recovered_u32 call = result->service_call_count++;
                result->service_object[call] = object;
                result->service_index[call] = index;
                result->service_selector[call] = 7U;
            }
        }
        if (input->status_48[object] != 0U) {
            recovered_u32 call = result->status_call_count++;
            result->status_call_object[call] = object;
            result->status_publication[object] =
                input->status_callback_result[object];
        } else {
            result->status_publication[object] = 0U;
        }
    }
}
