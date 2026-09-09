/* Workspace initialization recovered from i960 0xde670-0xde710. */
#include "recovered_common.h"

struct recovered_startup_geometry_workspace_init_de670_input {
    recovered_u32 callback_marker;
    recovered_u32 status_halfword;
    recovered_u32 table_word;
};

struct recovered_startup_geometry_workspace_init_de670_plan {
    recovered_u32 field_504b90;
    recovered_u32 field_504b94;
    recovered_u32 field_504ba4;
    recovered_u32 field_504ba8;
    recovered_u32 field_504baa;
    recovered_u32 field_504bac;
    recovered_u32 field_504bae;
    recovered_u32 field_504bb0;
    recovered_u32 field_504bcc;
    recovered_u32 field_504bd0;
    recovered_u32 field_504bd4;
    recovered_u32 field_504bd8;
    recovered_u32 field_504bda;
};

void recovered_startup_geometry_workspace_init_de670(
    const struct recovered_startup_geometry_workspace_init_de670_input *input,
    struct recovered_startup_geometry_workspace_init_de670_plan *plan)
{
    recovered_u32 marker_halfword = input->callback_marker & 0xffffU;

    plan->field_504b90 = 0x000de630U;
    plan->field_504b94 = marker_halfword;
    plan->field_504ba4 = 0U;
    plan->field_504ba8 = 3U << 9;
    plan->field_504baa = input->status_halfword & 0xffffU;
    plan->field_504bac = marker_halfword;
    plan->field_504bae = 3U << 9;
    plan->field_504bb0 = marker_halfword;
    plan->field_504bcc = 0x41d00000U;
    plan->field_504bd0 = 0x41d00000U;
    plan->field_504bd4 = input->table_word;
    plan->field_504bd8 = 0U;
    plan->field_504bda = 0U;
}
