#ifndef RECOVERED_GEOMETRY_VECTOR_SELECT_H
#define RECOVERED_GEOMETRY_VECTOR_SELECT_H

#include "recovered_common.h"

static void recovered_geometry_select_vector(
    int32_t selector,
    const recovered_u32 local[3],
    const recovered_u32 first_late[3],
    const recovered_u32 followup[3],
    recovered_u32 selected[3])
{
    const recovered_u32 *source = 0;

    if (selector == 0) {
        source = local;
    } else if (selector == 1) {
        source = first_late;
    } else if (selector == 2) {
        source = followup;
    }

    if (source != 0) {
        selected[0] = source[0];
        selected[1] = source[1];
        selected[2] = source[2];
    } else {
        selected[0] = 0U;
        selected[1] = 0U;
        selected[2] = 0U;
    }
}

#endif
