/* Fixed scene setup and first object-loop contract from i960 0xe79f0-0xe7b14. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 address;
    recovered_u32 value;
} recovered_geometry_scene_write_e79f0;

typedef struct {
    recovered_u32 input_word;
    recovered_u32 tagged_input_word;
    recovered_geometry_scene_write_e79f0 setup[18];
    recovered_u32 setup_count;
    recovered_u32 fifo_prefix[6];
    recovered_u32 fifo_prefix_count;
    recovered_u32 scene_count_address;
    recovered_u32 record_table_address;
    int32_t first_record_index;
    recovered_u32 object_dispatch_target;
    recovered_u32 first_loop_target;
    recovered_u32 mode_address;
    recovered_u32 final_return_target;
} recovered_geometry_status_scene_prologue_result_e79f0;

recovered_geometry_status_scene_prologue_result_e79f0
recovered_geometry_status_scene_prologue_e79f0(recovered_u32 input_word)
{
    recovered_geometry_status_scene_prologue_result_e79f0 result;
    recovered_geometry_scene_write_e79f0 *w = result.setup;

    result.input_word = input_word;
    result.tagged_input_word = input_word | 0x80U;
    w[0] = (recovered_geometry_scene_write_e79f0){0x00800070U, 0x707U};
    w[1] = (recovered_geometry_scene_write_e79f0){0x00804000U, 3U};
    w[2] = (recovered_geometry_scene_write_e79f0){0x00800030U, 0x303U};
    w[3] = (recovered_geometry_scene_write_e79f0){0x00804000U, result.tagged_input_word};
    w[4] = (recovered_geometry_scene_write_e79f0){0x00804004U, 0x01f40204U};
    w[5] = (recovered_geometry_scene_write_e79f0){0x00804008U, 0x00f80140U};
    w[6] = (recovered_geometry_scene_write_e79f0){0x0080400cU, 0x00f80140U};
    w[7] = (recovered_geometry_scene_write_e79f0){0x00804000U, 0x00f80140U};
    w[8] = (recovered_geometry_scene_write_e79f0){0x00804000U, 0x00f80140U};
    w[9] = (recovered_geometry_scene_write_e79f0){0x00800090U, 0x909U};
    w[10] = (recovered_geometry_scene_write_e79f0){0x00804000U, 0x43000000U};
    w[11] = (recovered_geometry_scene_write_e79f0){0x00804004U, 0x43000000U};
    w[12] = (recovered_geometry_scene_write_e79f0){0x008000a0U, 0xa0aU};
    w[13] = (recovered_geometry_scene_write_e79f0){0x00804000U, 0U};
    w[14] = (recovered_geometry_scene_write_e79f0){0x00804004U, 0U};
    w[15] = (recovered_geometry_scene_write_e79f0){0x00804000U, RECOVERED_FLOAT_ONE};
    w[16] = (recovered_geometry_scene_write_e79f0){0x00800160U, 0x1616U};
    w[17] = (recovered_geometry_scene_write_e79f0){0x00804000U, RECOVERED_FLOAT_ONE};
    result.setup_count = 18U;
    result.fifo_prefix[0] = 8U;
    result.fifo_prefix[1] = 16U;
    result.fifo_prefix[2] = 18U;
    result.fifo_prefix[3] = 0U;
    result.fifo_prefix[4] = 0U;
    result.fifo_prefix[5] = 0x43000000U;
    result.fifo_prefix_count = 6U;
    result.scene_count_address = 0x005783c0U;
    result.record_table_address = 0x005784e4U;
    result.first_record_index = -5;
    result.object_dispatch_target = 0x000e7390U;
    result.first_loop_target = 0x000e7b14U;
    result.mode_address = 0x005783c4U;
    result.final_return_target = 0x000e9138U;
    return result;
}
