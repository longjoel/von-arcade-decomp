/* Secondary response publication gate recovered from i960 0x87e10-0x87e70. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_response_publication_gate_87e10 {
    u32 state_value;
    u32 frame_index_r29;
    u32 state_threshold;
    u32 flag_word_5024a4;
    u32 ready_value;
    u32 exception_word_5024f4;
    u32 response_value_51c9d0;
    u32 seed_value;
    u32 publication_reached;
    u32 response_one_store;
    u32 response_zero_store;
    u32 response_one_address;
    u32 response_zero_address;
    u32 publication_target;
    u32 return_target;
};

struct recovered_stage_secondary_response_publication_gate_87e10
recovered_stage_secondary_response_publication_gate_87e10(u32 state_value,
                                                          u32 frame_index_r29,
                                                          u32 flag_word_5024a4,
                                                          u32 ready_value,
                                                          u32 exception_word_5024f4,
                                                          u32 response_value_51c9d0,
                                                          u32 seed_value)
{
    struct recovered_stage_secondary_response_publication_gate_87e10 out;
    u32 threshold = 31U + frame_index_r29;
    u32 exception_selected = exception_word_5024f4 == 0x61U ||
                             exception_word_5024f4 == 0x63U ? 1U : 0U;
    u32 state_bypass = state_value > threshold ? 1U : 0U;
    u32 flag_bypass = ((flag_word_5024a4 >> 4U) & 1U) != 0U ? 1U : 0U;

    out.state_value = state_value;
    out.frame_index_r29 = frame_index_r29;
    out.state_threshold = threshold;
    out.flag_word_5024a4 = flag_word_5024a4;
    out.ready_value = ready_value;
    out.exception_word_5024f4 = exception_word_5024f4;
    out.response_value_51c9d0 = response_value_51c9d0;
    out.seed_value = seed_value;
    out.publication_reached = state_bypass != 0U || flag_bypass != 0U ||
                              (ready_value != 0U && exception_selected != 0U) ? 1U : 0U;
    out.response_one_store = out.publication_reached != 0U &&
                             response_value_51c9d0 == 1U ? 1U : 0U;
    out.response_zero_store = out.publication_reached != 0U &&
                              response_value_51c9d0 == 0U ? 1U : 0U;
    out.response_one_address = 0x00503ca2U;
    out.response_zero_address = 0x005042a2U;
    out.publication_target = 0x00087e50U;
    out.return_target = 0x00087f50U;
    return out;
}
