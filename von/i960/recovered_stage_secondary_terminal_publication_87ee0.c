/* Secondary terminal publication recovered from i960 0x87ee0-0x87f50. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_terminal_publication_87ee0 {
    u32 status_503aa4;
    u32 status_marker_address;
    u32 status_marker_value;
    u32 progress_address;
    u32 progress_value;
    u32 value_503a70;
    u32 value_503a78;
    u32 command_address;
    u32 command_value;
    u32 state_address;
    u32 state_value;
    u32 state_seed;
    u32 progress_one_value;
    u32 progress_alternate_value;
    u32 command_low_value;
    u32 command_high_value;
    u32 return_target;
};

struct recovered_stage_secondary_terminal_publication_87ee0
recovered_stage_secondary_terminal_publication_87ee0(u32 status_503aa4,
                                                     u32 value_503a70,
                                                     u32 value_503a78,
                                                     u32 state_seed)
{
    struct recovered_stage_secondary_terminal_publication_87ee0 out;

    out.status_503aa4 = status_503aa4;
    out.status_marker_address = 0x00503a60U;
    out.status_marker_value = 1U;
    out.progress_address = 0x00503a04U;
    out.progress_one_value = 1U;
    out.progress_alternate_value = 0xb4U;
    out.progress_value = status_503aa4 == 0U || status_503aa4 == 1U ?
                         out.progress_one_value : out.progress_alternate_value;
    out.value_503a70 = value_503a70;
    out.value_503a78 = value_503a78;
    out.command_address = 0x005032f4U;
    out.command_low_value = 0x61U;
    out.command_high_value = 0x63U;
    out.command_value = value_503a70 <= value_503a78 ? out.command_low_value :
                        out.command_high_value;
    out.state_address = 0x0051d5e0U;
    out.state_value = state_seed;
    out.state_seed = state_seed;
    out.return_target = 0x00087f50U;
    return out;
}
