/* Cross-object request and signed-band prefix, i960 0x76590-0x76690.
 *
 * The routine's command-10 FIFO responses are supplied as inputs here.  The
 * listing proves the surrounding arithmetic: the first request uses
 * [related +0x10 - current +0x10, current +0x08 - related +0x08], and the
 * second reverses both differences.  Each returned word is subtracted from
 * the matching object's signed halfword at +0x184, stored as a low
 * halfword, and classified by the 0x73508 signed-band leaf.
 */

#include <stdint.h>

struct recovered_geometry_object_band_pair_76590 {
    uint32_t left_request_0;
    uint32_t left_request_1;
    uint32_t right_request_0;
    uint32_t right_request_1;
    uint16_t left_delta_low;
    uint16_t right_delta_low;
    uint32_t left_band;
    uint32_t right_band;
};

static uint32_t signed_band(uint32_t raw)
{
    int16_t value = (int16_t)(uint16_t)raw;

    if (value >= 0) {
        if (value <= 0x038d)
            return 0U;
        if (value <= 0x1554)
            return 1U;
        if (value <= 0x3fff)
            return 2U;
        if (value <= 0x5fff)
            return 3U;
        return 4U;
    }
    if (value < -0x6000)
        return 5U;
    if (value < -0x4000)
        return 6U;
    if (value < -0x1555)
        return 7U;
    if (value < -0x038e)
        return 8U;
    return 9U;
}

static uint16_t low_halfword(uint32_t value)
{
    return (uint16_t)value;
}

void recovered_geometry_object_band_pair_76590(
    uint16_t current_coord, uint16_t related_coord,
    uint32_t current_08, uint32_t current_10,
    uint32_t related_08, uint32_t related_10,
    uint32_t left_response, uint32_t right_response,
    struct recovered_geometry_object_band_pair_76590 *out)
{
    uint32_t left_delta = (uint32_t)current_coord - left_response;
    uint32_t right_delta = (uint32_t)related_coord - right_response;

    out->left_request_0 = related_10 - current_10;
    out->left_request_1 = current_08 - related_08;
    out->right_request_0 = current_10 - related_10;
    out->right_request_1 = related_08 - current_08;
    out->left_delta_low = low_halfword(left_delta);
    out->right_delta_low = low_halfword(right_delta);
    out->left_band = signed_band(left_delta);
    out->right_band = signed_band(right_delta);
}
