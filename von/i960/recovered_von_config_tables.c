/* Per-kind object config tables carried in the generated image.
 *
 * The original per-mech config blocks live at low ROM addresses (kind 0 at
 * 0x57d0, referenced through the table at 0x19360), but the generated image
 * now spans 0..~0xb250 and overwrites them. These reconstructions therefore
 * carry the config values in the generated image and the object initializer
 * points each object's +0x6c config pointer at the matching table below.
 *
 * Only the offsets consumed by the implemented routines are populated; all
 * other fields read as zero. Values were extracted from the original vonj
 * maincpu image.
 */

typedef unsigned int u32;

const u32 recovered_von_config_kind0[0x200] = {
    [0x528 / 4] = 0x00000a00U,
    [0x52c / 4] = 0x00000800U,
    [0x56c / 4] = 0x40600000U, /* 3.5f  walk default */
    [0x570 / 4] = 0x404ccccdU, /* 3.2f  walk +0x176==0 */
    [0x574 / 4] = 0x40000000U, /* 2.0f  walk +0x176==1 */
    [0x578 / 4] = 0x402ccccdU, /* 2.7f */
    [0x57c / 4] = 0x402f5c29U, /* 2.74f */
    [0x580 / 4] = 0x3fe66666U, /* 1.8f */
    [0x584 / 4] = 0x40200000U, /* 2.5f */
    [0x588 / 4] = 0x402ccccdU, /* 2.7f */
    [0x58c / 4] = 0x3fe66666U, /* 1.8f */
    [0x590 / 4] = 0x40133333U, /* 2.3f */
    [0x594 / 4] = 0x40200000U, /* 2.5f */
    [0x598 / 4] = 0x3fd9999aU, /* 1.7f */
};
