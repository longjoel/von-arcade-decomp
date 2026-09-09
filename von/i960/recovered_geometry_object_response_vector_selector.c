/* Response-vector selection recovered from i960 0xdf0cc-0xdf120. */
#include "recovered_geometry_vector_select.h"

/*
 * selector is the sign-extended halfword at related-object +0x02.
 * The three source vectors correspond to the local, first-late, and
 * follow-up triplets selected by the three explicit branches in the ROM.
 */
void recovered_geometry_object_select_response_vector(
    int32_t selector,
    const recovered_u32 local[3],
    const recovered_u32 first_late[3],
    const recovered_u32 followup[3],
    recovered_u32 selected[3])
{
    recovered_geometry_select_vector(selector, local, first_late, followup, selected);
}
