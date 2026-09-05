/* Command-6 float-pair validator recovered from i960 0x6ede0-0x6eedc. */
#include <stdint.h>
#include <string.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_command6_pair_plan {
    u32 opcode;
    u32 table_base;
    u32 record_size;
    s32 trunc_x;
    s32 trunc_y;
    u32 valid;
    u32 index;
    u32 reject_value;
    u32 packet[8];
    u32 out_halfwords[2];
};

static float recovered_command6_pair_float(u32 bits)
{
    float value;

    memcpy(&value, &bits, sizeof(value));
    return value;
}

void recovered_command6_pair_plan(u32 x_bits, u32 y_bits,
                                  u32 rec_hw0, u32 rec_hw1,
                                  u32 rec_04, u32 rec_08,
                                  u32 rec_0c, u32 rec_10,
                                  struct recovered_command6_pair_plan *plan)
{
    s32 half_x;

    plan->opcode = 0x41U;
    plan->table_base = 0x0051bb28U;
    plan->record_size = 20U;
    plan->reject_value = 0x47c34f80U;
    /* movr/addrl/cvtzri promote each float and truncate toward zero. The
     * 0x40800000 load is dead: addrl adds g4, which is zero here. */
    plan->trunc_x = (s32)(double)recovered_command6_pair_float(x_bits);
    plan->trunc_y = (s32)(double)recovered_command6_pair_float(y_bits);
    /* Each truncated value is halved arithmetically and masked with
     * 0xfffffe00, so the pair is valid exactly for [0, 1023] inputs. */
    half_x = plan->trunc_x >> 1;
    plan->valid = (((u32)half_x & 0xfffffe00U) == 0U
        && (((u32)(plan->trunc_y >> 1) & 0xfffffe00U) == 0U)) ? 1U : 0U;
    /* Asymmetric index: the y truncation is unhalved, unlike 0x6ece0. */
    plan->index = plan->valid
        ? (u32)plan->trunc_y * 512U + (u32)half_x : 0U;
    plan->packet[0] = 53U;
    plan->packet[1] = rec_04;
    plan->packet[2] = x_bits;
    plan->packet[3] = rec_0c;
    plan->packet[4] = y_bits;
    /* notbit 31 flips only the top bit of the +0x08 record word. */
    plan->packet[5] = rec_08 ^ 0x80000000U;
    plan->packet[6] = rec_10;
    plan->packet[7] = rec_08;
    plan->out_halfwords[0] = rec_hw0;
    plan->out_halfwords[1] = rec_hw1;
}
