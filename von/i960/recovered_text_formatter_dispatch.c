/* Exact 0xf5190 formatter dispatch table recovered from i960 0xf5210. */
#include <stdint.h>

enum {
    RECOVERED_FORMATTER_FALLBACK = 0x000f5bf4U,
    RECOVERED_FORMATTER_TABLE_COUNT = 121U,
};

uint32_t recovered_text_formatter_dispatch_target(uint32_t index)
{
    if (index >= RECOVERED_FORMATTER_TABLE_COUNT)
        return RECOVERED_FORMATTER_FALLBACK;

    switch (index) {
    case 0U: return 0x000f51bcU;
    case 32U: return 0x000f53f4U;
    case 35U: return 0x000f5408U;
    case 37U: return 0x000f5608U;
    case 42U: return 0x000f5410U;
    case 43U: return 0x000f5474U;
    case 45U: return 0x000f546cU;
    case 46U: return 0x000f547cU;
    case 48U: return 0x000f5544U;
    case 49U: case 50U: case 51U: case 52U: case 53U:
    case 54U: case 55U: case 56U: case 57U:
        return 0x000f554cU;
    case 68U: return 0x000f561cU;
    case 69U: case 71U: case 101U: case 102U: case 103U:
        return 0x000f5688U;
    case 76U: return 0x000f5588U;
    case 79U: return 0x000f5800U;
    case 85U: return 0x000f5954U;
    case 117U: return 0x000f5958U;
    case 88U: return 0x000f59b4U;
    case 99U: return 0x000f55a0U;
    case 100U: case 105U: return 0x000f5620U;
    case 104U: return 0x000f5590U;
    case 108U: return 0x000f5598U;
    case 110U: return 0x000f5790U;
    case 111U: return 0x000f5804U;
    case 112U: return 0x000f5860U;
    case 115U: return 0x000f58bcU;
    case 120U: return 0x000f59bcU;
    default: return RECOVERED_FORMATTER_FALLBACK;
    }
}
