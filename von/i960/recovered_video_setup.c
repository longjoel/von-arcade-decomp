/* Recovered video asset setup around i960 routine 0x000e2130. */

typedef unsigned int u32;

enum recovered_video_asset_bank {
    RECOVERED_VIDEO_BANK_A = 0,
    RECOVERED_VIDEO_BANK_B = 1,
};

struct recovered_video_asset {
    u32 tile;
    u32 source;
};

struct recovered_video_setup_plan {
    enum recovered_video_asset_bank bank;
    struct recovered_video_asset assets[14];
    u32 published_base;
    u32 published_offsets[5];
    u32 published_sentinel;
};

static int recovered_video_bank_a_selected(u32 palette_mode,
                                           u32 geometry_mode,
                                           u32 geometry_gate,
                                           u32 board_bit,
                                           u32 palette_delta)
{
    /* This is the exact branch condition leading to 0xe2180. */
    if (geometry_mode == 0)
        return 1;
    return geometry_mode == 2 && palette_mode == 1 && geometry_gate == 0 &&
           board_bit == palette_delta;
}

/*
 * 0x000e2130's deterministic work is represented as a descriptor plan.
 * The caller performs 0xe1e08 first, then invokes 0xe1f20 for each asset.
 * Asset source addresses are ROM pointers as seen by the original i960.
 */
void recovered_video_setup_plan(u32 palette_mode,
                                u32 geometry_mode,
                                u32 geometry_gate,
                                u32 board_bit,
                                u32 palette_delta,
                                struct recovered_video_setup_plan *plan)
{
    static const u32 shared_tiles[] = { 9, 11, 13, 15, 17, 19, 21, 25, 27, 29 };
    static const u32 shared_sources[] = {
        0x02fb7510, 0x02fb75d0, 0x02fb7690, 0x02fb7750, 0x02fb7810,
        0x02fb7990, 0x02fb6cd0, 0x02fb7e10, 0x02bfed8c, 0x02fb6fd0,
    };
    static const u32 bank_a_sources[] = {
        0x02fb3d90, 0x02fb3e50, 0x02fb4990, 0x02fb4a50,
    };
    static const u32 bank_b_sources[] = {
        0x02fb3f10, 0x02fb3fd0, 0x02fb4b10, 0x02fb4bd0,
    };
    const u32 *bank_sources = bank_a_sources;
    u32 index;

    plan->bank = RECOVERED_VIDEO_BANK_A;
    if (!recovered_video_bank_a_selected(palette_mode, geometry_mode,
                                         geometry_gate, board_bit,
                                         palette_delta)) {
        plan->bank = RECOVERED_VIDEO_BANK_B;
        bank_sources = bank_b_sources;
    }

    for (index = 0; index < 4; ++index) {
        plan->assets[index].tile = 1 + index * 2;
        plan->assets[index].source = bank_sources[index];
    }
    for (index = 0; index < 10; ++index) {
        plan->assets[index + 4].tile = shared_tiles[index];
        plan->assets[index + 4].source = shared_sources[index];
    }

    plan->published_base = 0x02f8d890;
    plan->published_offsets[0] = 0x60c0;
    plan->published_offsets[1] = 0xc180;
    plan->published_offsets[2] = 0x12240;
    plan->published_offsets[3] = 0x18300;
    plan->published_offsets[4] = 0x1e3c0;
    plan->published_sentinel = 0xff;
}
