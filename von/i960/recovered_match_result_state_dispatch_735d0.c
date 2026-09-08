/* Selector routing recovered from i960 routine 0x735d0. */
#include <stdint.h>

typedef uint32_t u32;

#define MATCH_RESULT_EXTERNAL_ROUTE 0x000853c8U
#define MATCH_RESULT_DEFAULT_ROUTE  0x00074848U

u32 recovered_match_result_state_dispatch_735d0(u32 status_flag,
                                                  u32 status_index)
{
    static const u32 targets[34] = {
        0x00074848U, 0x000736a0U, 0x000737c8U, 0x00073900U,
        0x00073a34U, 0x00073b68U, 0x00073c98U, 0x00073dccU,
        0x00074148U, 0x000744ecU, 0x00073fdcU, 0x00073ffcU,
        0x0007402cU, 0x0007408cU, 0x000740ecU, 0x000740f8U,
        0x00074104U, 0x00074110U, 0x0007411cU, 0x00074138U,
        0x0007415cU, 0x00074178U, 0x00074194U, 0x000745bcU,
        0x00074848U, 0x000745e4U, 0x0007460cU, 0x00074634U,
        0x00074674U, 0x000746f4U, 0x00074754U, 0x0007479cU,
        0x000747e4U, 0x00074848U
    };

    if (status_flag != 0U)
        return MATCH_RESULT_EXTERNAL_ROUTE;
    if (status_index > 33U)
        return MATCH_RESULT_DEFAULT_ROUTE;
    return targets[status_index];
}
