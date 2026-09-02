/* Response-vector selection recovered from i960 0xdf0cc-0xdf120. */
#include <stdint.h>

typedef uint32_t u32;

/*
 * selector is the sign-extended halfword at related-object +0x02.
 * The three source vectors correspond to the local, first-late, and
 * follow-up triplets selected by the three explicit branches in the ROM.
 */
void recovered_geometry_object_select_response_vector(
    int32_t selector,
    const u32 local[3],
    const u32 first_late[3],
    const u32 followup[3],
    u32 selected[3])
{
    const u32 *source = 0;

    if (selector == 0) {
        source = local;
    } else if (selector == 1) {
        source = first_late;
    } else if (selector == 2) {
        source = followup;
    }

    if (source) {
        selected[0] = source[0];
        selected[1] = source[1];
        selected[2] = source[2];
    } else {
        selected[0] = 0U;
        selected[1] = 0U;
        selected[2] = 0U;
    }
}
