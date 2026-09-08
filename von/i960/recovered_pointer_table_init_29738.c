/* Pure linked-list initialization from i960 0x29738/0x29778. */
#include <stdint.h>

struct recovered_pointer_service_init_plan {
    uint32_t store_address[6];
    uint32_t store_value[6];
    uint32_t store_count;
    uint32_t first_helper;
    uint32_t first_head;
    uint32_t first_stride;
    uint32_t second_helper;
    uint32_t second_head;
    uint32_t second_stride;
};

/* Caller setup at 0x296d0 for the two linked-list helper calls. */
void recovered_pointer_service_init_plan(
    struct recovered_pointer_service_init_plan *plan)
{
    static const uint32_t addresses[6] = {
        0x00515098U, 0x0051509cU, 0x005150a8U,
        0x005150acU, 0x005150b0U, 0x005150b4U
    };
    static const uint32_t values[6] = {
        0U, 0U, 0x00515090U, 0U, 0x005150c0U, 0x005190c0U
    };
    uint32_t index;

    for (index = 0U; index < 6U; ++index) {
        plan->store_address[index] = addresses[index];
        plan->store_value[index] = values[index];
    }
    plan->store_count = 6U;
    plan->first_helper = 0x00029778U;
    plan->first_head = 0x005150c0U;
    plan->first_stride = 0x100U;
    plan->second_helper = 0x00029738U;
    plan->second_head = 0x005190c0U;
    plan->second_stride = 0x40U;
}

/* Build the 64-entry next-pointer schedule; the terminal link is NULL. */
void recovered_pointer_table_init_29738(uint32_t head, uint32_t stride,
                                        uint32_t links[64])
{
    uint32_t i;
    for (i = 0; i < 63; ++i)
        links[i] = head + (i + 1U) * stride;
    links[63] = 0;
}
