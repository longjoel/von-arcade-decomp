/* Geometry-port word pump recovered from i960 0x292d8-0x2932c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_fifo_upload_plan {
    u32 select_address;
    u32 select_value;
    u32 port_address;
    u32 header_words[2];
    u32 pair_count;
    u32 words_per_pair;
    u32 words_total;
    u32 saves_return_link;
    u32 clears_g14;
};

struct recovered_geometry_profile_upload_plan {
    u32 prefix_address[13];
    u32 prefix_value[13];
    u32 prefix_count;
    u32 upload_header[2];
    u32 upload_pair_count;
    u32 upload_source;
    u32 post_select_address;
    u32 post_select_value;
    u32 post_port_value[4];
    u32 post_command_address;
    u32 post_command_value;
    u32 finish_helper;
};

/* Fixed caller prefix at 0x294b0, including its 0x292d8 call context. */
void recovered_geometry_profile_upload_plan(
    struct recovered_geometry_profile_upload_plan *plan)
{
    static const u32 addresses[13] = {
        0x00800160U, 0x00804000U, 0x00800070U, 0x00804000U,
        0x00800080U, 0x00804000U, 0x00800030U, 0x00804000U,
        0x00804004U, 0x00804008U, 0x0080400cU, 0x00804000U,
        0x00804000U
    };
    static const u32 values[13] = {
        0x1616U, 0x47800000U, 0x707U, 3U, 0x808U, 0x41004000U,
        0x303U, 0x80U, 0x1f40204U, 0xf80140U, 0xf80140U,
        0xf80140U, 0xf80140U
    };
    u32 index;

    for (index = 0U; index < 13U; ++index) {
        plan->prefix_address[index] = addresses[index];
        plan->prefix_value[index] = values[index];
    }
    plan->prefix_count = 13U;
    plan->upload_header[0] = 0U;
    plan->upload_header[1] = 32U;
    plan->upload_pair_count = 32U;
    plan->upload_source = 0x000293b0U;
    plan->post_select_address = 0x00800090U;
    plan->post_select_value = 0x909U;
    plan->post_port_value[0] = 0x44160000U;
    plan->post_port_value[1] = 0x44160000U;
    plan->post_port_value[2] = 0U;
    plan->post_port_value[3] = 0U;
    plan->post_command_address = 0x008000a0U;
    plan->post_command_value = 0xa0aU;
    plan->finish_helper = 0x00028d30U;
}

struct recovered_geometry_profile_upload_variant_plan {
    u32 write_address[17];
    u32 write_value[17];
    u32 write_count;
    u32 upload_header[2];
    u32 upload_pair_count;
    u32 upload_source;
    u32 finish_helper;
};

/* Fixed alternate caller stream at 0x295d0-0x296c0. */
void recovered_geometry_profile_upload_variant_plan(
    struct recovered_geometry_profile_upload_variant_plan *plan)
{
    static const u32 addresses[17] = {
        0x00800160U, 0x00804000U, 0x00800070U, 0x00804000U,
        0x00800080U, 0x00804000U, 0x00800030U, 0x00804000U,
        0x00804004U, 0x00804008U, 0x0080400cU, 0x00804000U,
        0x00804000U, 0x008000a0U, 0x00804000U, 0x00804004U,
        0x00804000U
    };
    static const u32 values[17] = {
        0x1616U, 0x46000000U, 0x707U, 3U, 0x808U, 0x41004000U,
        0x303U, 0x80U, 0x1f40204U, 0xf80140U, 0xf80140U,
        0xf80140U, 0xf80140U, 0xa0aU, 0x3f333333U,
        0xbf000000U, 0x3f000000U
    };
    u32 index;

    for (index = 0U; index < 17U; ++index) {
        plan->write_address[index] = addresses[index];
        plan->write_value[index] = values[index];
    }
    plan->write_count = 17U;
    plan->upload_header[0] = 0U;
    plan->upload_header[1] = 32U;
    plan->upload_pair_count = 32U;
    plan->upload_source = 0x000293b0U;
    plan->finish_helper = 0x00028d30U;
}

void recovered_fifo_upload_plan(u32 header_first, u32 pair_count,
                                struct recovered_fifo_upload_plan *plan)
{
    plan->select_address = 0x00800060U;
    plan->select_value = 0x606U;
    plan->port_address = 0x00804000U;
    plan->header_words[0] = header_first;
    plan->header_words[1] = pair_count;
    plan->pair_count = pair_count;
    /* One decrement per iteration with two word stores: the cmpi/bne pair
     * counts pairs while the FIFO port address never advances. */
    plan->words_per_pair = 2U;
    plan->words_total = pair_count * 2U;
    /* The entry saves the return link into g3 and clears g14 for the
     * body, returning through bx (g3) instead of the shared tail. */
    plan->saves_return_link = 1U;
    plan->clears_g14 = 1U;
}
