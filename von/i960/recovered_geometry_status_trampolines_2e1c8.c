/* ABI epilogue plan recovered from the paired 0x2e1c8/0x2e1e8 stubs. */

typedef unsigned int u32;

struct recovered_status_trampoline_plan {
    u32 entry;
    u32 link_load_address;
    u32 return_stub;
    u32 moves_link_to_g0;
    u32 clears_g14;
    u32 indirect_branch;
};

void recovered_geometry_status_trampoline_plan(
    u32 alternate, struct recovered_status_trampoline_plan *plan)
{
    plan->entry = alternate ? 0x0002e1e8U : 0x0002e1c8U;
    plan->link_load_address = alternate ? 0x0002e1e0U : 0x0002e1c0U;
    plan->return_stub = alternate ? 0x0002e1f4U : 0x0002e1d4U;
    plan->moves_link_to_g0 = 1U;
    plan->clears_g14 = 1U;
    plan->indirect_branch = 1U;
}
