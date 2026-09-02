/* Profile upload plus status-panel wrappers recovered from 0x203d0-0x20458. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_profile_upload_panel_plan {
    u32 upload_source;
    u32 upload_destination;
    u32 upload_flags;
    u32 upload_halfwords_per_row;
    u32 upload_rows;
    u32 upload_helper;
    u32 panel_source_present;
    u32 panel_helper;
    u32 panel_column;
    u32 panel_row;
    u32 panel_width;
    u32 panel_height;
};

void recovered_profile_upload_panel_plan(u32 profile, u32 panel_value,
                                        u32 caller_g17, u32 caller_g9,
                                        struct recovered_profile_upload_panel_plan *plan)
{
    plan->upload_source = 0x01004000U;
    plan->upload_destination = profile == 0U ? 0x01fcfd20U
        : profile == 1U ? 0x01fd49d0U : 0x01fd1520U;
    plan->upload_flags = 0x40U;
    plan->upload_halfwords_per_row = 0x40U;
    plan->upload_rows = caller_g17 + 31U;
    plan->upload_helper = 0x0001bc90U;
    plan->panel_source_present = panel_value;
    plan->panel_helper = panel_value != 0U ? 0x0001dc90U : 0x0001df00U;
    plan->panel_column = 11U;
    plan->panel_row = 21U;
    plan->panel_width = caller_g9 + 31U;
    plan->panel_height = 8U;
}
