#ifndef VON_RECOVERED_COMMON_H
#define VON_RECOVERED_COMMON_H

#include <stdint.h>

typedef uint32_t recovered_u32;

static inline int32_t recovered_sign_extend_16(uint32_t value)
{
    return (int32_t)(int16_t)(value & 0xffffU);
}

/* Shared memory and helper addresses appearing in recovered contracts. */
#define RECOVERED_FIFO_ADDRESS       0x00884000U
#define RECOVERED_FRAME_POINTER      0x00801008U
#define RECOVERED_FRAME_PUBLISH      0x00804000U
#define RECOVERED_GEOMETRY_CONTROL   0x00800010U
#define RECOVERED_GEOMETRY_CONTROL_VALUE 0x101U
#define RECOVERED_POINTER_OFFSET     0x34U
#define RECOVERED_HELPER_TRANSFER    0x0001dc10U
#define RECOVERED_HELPER_CLEAR       0x0001df00U
#define RECOVERED_FLOAT_ONE          0x3f800000U
#define RECOVERED_FRAME_CONSTANT     0x084553fU

/* The recovered upload wrappers all expose these identically named fields. */
#define RECOVERED_SET_UPLOAD_PLAN(plan_, destination_, rows_) do { \
    (plan_)->source = 0x01004000U; \
    (plan_)->destination = (destination_); \
    (plan_)->flags = 0x40U; \
    (plan_)->halfwords_per_row = 0x40U; \
    (plan_)->rows = (rows_); \
    (plan_)->helper = 0x0001bc90U; \
} while (0)

#define RECOVERED_SET_SOURCE_OR_CLEAR(plan_, present_, source_, transfer_, clear_) do { \
    (plan_)->source = (present_) ? (source_) : 0U; \
    (plan_)->source_helper = (present_) ? (transfer_) : 0U; \
    (plan_)->fill_helper = (present_) ? 0U : (clear_); \
} while (0)

/* Common text-plane setup used by the weapon marker handlers. */
#define RECOVERED_SET_MARKER_TEXT_PLAN(plan_, mode_, column_, height_) do { \
    (plan_)->text_helper = (mode_) == 0U ? 0x0001dd80U : RECOVERED_HELPER_TRANSFER; \
    (plan_)->text_plane = (mode_) == 0U ? 0x01002000U : 0x01000000U; \
    (plan_)->text_column = (column_); \
    (plan_)->text_row = 8U; \
    (plan_)->text_width = 31U; \
    (plan_)->text_height = (height_); \
} while (0)

#define RECOVERED_SET_CLIP_PLAN_COMMON(plan_) do { \
    (plan_)->clip_dispatch = 0x000701a0U; \
    (plan_)->frame_constants[0] = RECOVERED_FRAME_CONSTANT; \
    (plan_)->frame_constants[1] = 1U; \
    (plan_)->control_address = RECOVERED_GEOMETRY_CONTROL; \
    (plan_)->control_value = RECOVERED_GEOMETRY_CONTROL_VALUE; \
    (plan_)->frame_publish_address = RECOVERED_FRAME_PUBLISH; \
    (plan_)->call_count = 4U; \
} while (0)

static inline void recovered_fill_nine_word_geometry_packet(recovered_u32 packet[9],
                                                              recovered_u32 derived_word)
{
    packet[0] = 19U;
    packet[1] = derived_word;
    packet[2] = 0x40a00000U;
    packet[3] = RECOVERED_FLOAT_ONE;
    packet[4] = 18U;
    packet[5] = RECOVERED_FLOAT_ONE;
    packet[6] = 0U;
    packet[7] = 0U;
    packet[8] = 58U;
}

static inline void recovered_fill_thirteen_word_geometry_packet(
    recovered_u32 packet[13], recovered_u32 state_parameter,
    recovered_u32 derived_word)
{
    packet[0] = 29U;
    packet[1] = state_parameter;
    packet[2] = 0x40400000U;
    packet[3] = 19U;
    packet[4] = derived_word;
    packet[5] = 0x42200000U;
    packet[6] = derived_word;
    packet[7] = RECOVERED_FLOAT_ONE;
    packet[8] = 18U;
    packet[9] = RECOVERED_FLOAT_ONE;
    packet[10] = 0U;
    packet[11] = 0U;
    packet[12] = 58U;
}

static inline recovered_u32 recovered_tile_address(recovered_u32 plane,
                                                   recovered_u32 table_offset,
                                                   recovered_u32 column,
                                                   recovered_u32 row)
{
    return plane + table_offset + ((row << 6) + column) * 2U;
}

static inline recovered_u32 recovered_pattern_tile_address(
    recovered_u32 base, recovered_u32 column, recovered_u32 row,
    recovered_u32 index, recovered_u32 width, recovered_u32 row_mask)
{
    recovered_u32 tile_row = row + index / width;
    if (row_mask != 0U)
        tile_row &= row_mask;
    return base + ((tile_row << 6) + column + index % width) * 2U;
}

#endif
