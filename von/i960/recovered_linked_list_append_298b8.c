/* Pure intrusive doubly-linked-list append from i960 0x298b8-0x298f0. */
#include <stdint.h>
struct recovered_link_append { uint32_t node_next, node_prev, old_next, new_tail; };
void recovered_linked_list_append_298b8(uint32_t node, uint32_t old_tail,
                                        uint32_t sentinel, struct recovered_link_append *out)
{
    out->node_next = sentinel;
    out->node_prev = old_tail;
    out->old_next = node;
    out->new_tail = node;
}
