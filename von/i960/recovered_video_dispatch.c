/* Recovered dispatcher prefix at i960 0x000e2330-0x000e23b0. */

typedef unsigned int u32;

enum recovered_video_dispatch_path {
    RECOVERED_VIDEO_DISPATCH_NOOP = 0,
    RECOVERED_VIDEO_DISPATCH_TABLE = 1,
    RECOVERED_VIDEO_DISPATCH_DEFAULT = 2,
};

struct recovered_video_dispatch_plan {
    enum recovered_video_dispatch_path path;
    u32 bank_a;
    u32 table_index;
};

struct recovered_video_tile_plan {
    u32 tile[6];
    u32 source[6];
    u32 count;
};

struct recovered_video_plain_tile_plan {
    u32 tile[9];
    u32 source[9];
    u32 count;
};

struct recovered_video_exit_tile_plan {
    u32 tile[3];
    u32 source[3];
    u32 count;
    u32 exit_address;
};

struct recovered_video_conditional_plain_plan {
    u32 tile[6];
    u32 source[6];
    u32 count;
    u32 exit_address;
};

struct recovered_video_helper_tile_plan {
    u32 tile[6];
    u32 source[6];
    u32 helper;
    u32 count;
    u32 exit_address;
};

struct recovered_video_large_helper_tile_plan {
    u32 tile[9];
    u32 source[9];
    u32 helper;
    u32 count;
    u32 exit_address;
};

struct recovered_video_mixed_tile_plan {
    u32 tile[8];
    u32 source[8];
    u32 helper[8];
    u32 count;
    u32 exit_address;
};

struct recovered_video_post_dispatch_plan {
    u32 sentinel_match;
    u32 tile[2];
    u32 source[2];
    u32 helper[2];
    u32 count;
    u32 continuation;
};

enum recovered_video_post_route {
    RECOVERED_VIDEO_POST_LOWER = 0,
    RECOVERED_VIDEO_POST_21F = 1,
    RECOVERED_VIDEO_POST_MIDDLE = 2,
    RECOVERED_VIDEO_POST_HIGH = 3,
    RECOVERED_VIDEO_POST_DONE = 4,
};

struct recovered_video_exit_tile_plan {
    u32 tile[3];
    u32 source[3];
    u32 count;
    u32 exit_address;
};

static u32 recovered_video_bank_a_flag(u32 geometry_mode,
                                       u32 palette_mode,
                                       u32 geometry_gate,
                                       u32 board_bit,
                                       u32 palette_delta)
{
    if (geometry_mode == 0)
        return 1;
    return geometry_mode == 2 && palette_mode == 1 && geometry_gate == 0 &&
           board_bit == palette_delta;
}

/*
 * The jump-table arms begin at 0xe25bc. This function deliberately stops at
 * the exact common gate preceding those arms and does not model their bodies.
 */
void recovered_video_dispatch_plan(u32 geometry_mode,
                                   u32 palette_mode,
                                   u32 geometry_gate,
                                   u32 board_bit,
                                   u32 palette_delta,
                                   u32 dispatch_state,
                                   struct recovered_video_dispatch_plan *plan)
{
    plan->bank_a = recovered_video_bank_a_flag(
        geometry_mode, palette_mode, geometry_gate, board_bit, palette_delta);
    plan->table_index = dispatch_state;

    if (dispatch_state == 0xffU) {
        plan->path = RECOVERED_VIDEO_DISPATCH_NOOP;
        return;
    }
    if (dispatch_state > 0x81U) {
        plan->path = RECOVERED_VIDEO_DISPATCH_DEFAULT;
        return;
    }
    plan->path = RECOVERED_VIDEO_DISPATCH_TABLE;
}

/* Jump-table entry 0 at 0xe25bc: four mirrored tile expansions. */
void recovered_video_dispatch_arm0(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 21;
    plan->source[1] = 0x02fb5b90;
    plan->tile[2] = 23;
    plan->source[2] = 0x02fb5c50;
    plan->tile[3] = 25;
    plan->source[3] = 0x02fb5d10;
    plan->count = 4;
}

/* Jump-table entry 1 at 0xe2600: six mirrored tile expansions. */
void recovered_video_dispatch_arm1(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 21;
    plan->source[1] = 0x02fb5dd0;
    plan->tile[2] = 23;
    plan->source[2] = 0x02fb5e90;
    plan->tile[3] = 25;
    plan->source[3] = 0x02fb5f50;
    plan->tile[4] = 27;
    plan->source[4] = 0x02fb6010;
    plan->tile[5] = 29;
    plan->source[5] = 0x02fb60d0;
    plan->count = 6;
}

/* Jump-table entry 2 at 0xe2664: five mirrored tile expansions. */
void recovered_video_dispatch_arm2(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 23;
    plan->source[1] = 0x02fb6190;
    plan->tile[2] = 25;
    plan->source[2] = 0x02fb6250;
    plan->tile[3] = 27;
    plan->source[3] = 0x02fb6310;
    plan->tile[4] = 29;
    plan->source[4] = 0x02fb63d0;
    plan->count = 5;
}

/* Jump-table entry 3 at 0xe26c8: five mirrored tile expansions. */
void recovered_video_dispatch_arm3(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 23;
    plan->source[1] = 0x02fb6550;
    plan->tile[2] = 25;
    plan->source[2] = 0x02fb6610;
    plan->tile[3] = 27;
    plan->source[3] = 0x02fb66d0;
    plan->tile[4] = 29;
    plan->source[4] = 0x02fb6790;
    plan->count = 5;
}

/* Jump-table entry 4 at 0xe271c: five mirrored tile expansions. */
void recovered_video_dispatch_arm4(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 23;
    plan->source[1] = 0x02fb6850;
    plan->tile[2] = 25;
    plan->source[2] = 0x02fb6910;
    plan->tile[3] = 27;
    plan->source[3] = 0x02fb69d0;
    plan->tile[4] = 29;
    plan->source[4] = 0x02fb6a90;
    plan->count = 5;
}

/* Jump-table entry 5 at 0xe2770: three mirrored tile expansions. */
void recovered_video_dispatch_arm5(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 27;
    plan->source[1] = 0x02fb6b50;
    plan->tile[2] = 29;
    plan->source[2] = 0x02fb6c10;
    plan->count = 3;
}

/* Jump-table entry 6 at 0xe27a4: six mirrored tile expansions. */
void recovered_video_dispatch_arm6(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 21;
    plan->source[1] = 0x02fb6cd0;
    plan->tile[2] = 23;
    plan->source[2] = 0x02fb6d90;
    plan->tile[3] = 25;
    plan->source[3] = 0x02fb6e50;
    plan->tile[4] = 27;
    plan->source[4] = 0x02fb6f10;
    plan->count = 5;
}

/* Jump-table entry 7 at 0xe27f8: one mirrored tile expansion. */
void recovered_video_dispatch_arm7(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->count = 1;
}

/* Jump-table entry 8 at 0xe280c: two mirrored tile expansions. */
void recovered_video_dispatch_arm8(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 29;
    plan->source[1] = 0x02fb7450;
    plan->count = 2;
}

/* Jump-table arm at 0xe2830: four mirrored tile expansions. */
void recovered_video_dispatch_arm9(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 21;
    plan->source[0] = 0x02fb6cd0;
    plan->tile[1] = 25;
    plan->source[1] = 0x02fb7e10;
    plan->tile[2] = 27;
    plan->source[2] = 0x02bfed8c;
    plan->tile[3] = 29;
    plan->source[3] = 0x02fb6fd0;
    plan->count = 4;
}

/* Plain e1f20 arm at 0xe2874: nine non-mirrored tile expansions. */
void recovered_video_dispatch_arm10(struct recovered_video_plain_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->tile[1] = 1;
    plan->source[1] = 0x02fb7a50;
    plan->tile[2] = 3;
    plan->source[2] = 0x02fb7b10;
    plan->tile[3] = 5;
    plan->source[3] = 0x02fb7bd0;
    plan->tile[4] = 7;
    plan->source[4] = 0x02fb7c90;
    plan->tile[5] = 21;
    plan->source[5] = 0x02fb6cd0;
    plan->tile[6] = 25;
    plan->source[6] = 0x02fb7e10;
    plan->tile[7] = 27;
    plan->source[7] = 0x02bfed8c;
    plan->tile[8] = 29;
    plan->source[8] = 0x02fb6fd0;
    plan->count = 9;
}

/* Plain e1f20 arm at 0xe2908: one non-mirrored tile expansion. */
void recovered_video_dispatch_arm11(struct recovered_video_plain_tile_plan *plan)
{
    plan->tile[0] = 11;
    plan->source[0] = 0x02fb75d0;
    plan->count = 1;
}

/* Plain e1f20 arm at 0xe29a4, including its e2a30 shared tail. */
void recovered_video_dispatch_arm14(struct recovered_video_plain_tile_plan *plan)
{
    plan->tile[0] = 1;
    plan->source[0] = 0x02fb7a50;
    plan->tile[1] = 3;
    plan->source[1] = 0x02fb7b10;
    plan->tile[2] = 5;
    plan->source[2] = 0x02fb4090;
    plan->tile[3] = 7;
    plan->source[3] = 0x02fb4150;
    plan->tile[4] = 9;
    plan->source[4] = 0x02fb7bd0;
    plan->tile[5] = 11;
    plan->source[5] = 0x02fb7c90;
    plan->count = 6;
}

/* Plain e1f20 arm at 0xe29fc, including its e2a30 shared tail. */
void recovered_video_dispatch_arm15(struct recovered_video_plain_tile_plan *plan)
{
    plan->tile[0] = 1;
    plan->source[0] = 0x02fb7a50;
    plan->tile[1] = 3;
    plan->source[1] = 0x02fb7b10;
    plan->tile[2] = 5;
    plan->source[2] = 0x02fb7bd0;
    plan->tile[3] = 7;
    plan->source[3] = 0x02fb7c90;
    plan->count = 4;
}

/* Bank-select gate at 0xe2a40: two plain expansions, then a shared tail. */
void recovered_video_dispatch_arm16(u32 bank_a,
                                    struct recovered_video_plain_tile_plan *plan)
{
    plan->tile[0] = 5;
    plan->tile[1] = 7;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb4990;
        plan->source[1] = 0x02fb4a50;
    } else {
        plan->source[0] = 0x02fb4b10;
        plan->source[1] = 0x02fb4bd0;
    }
    plan->count = 2;
}

/* Bank-dependent plain arm at 0xe2a48: four expansions. */
void recovered_video_dispatch_arm17(u32 bank_a,
                                    struct recovered_video_plain_tile_plan *plan)
{
    plan->tile[0] = 9;
    plan->tile[1] = 11;
    plan->tile[2] = 1;
    plan->tile[3] = 3;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb5290;
        plan->source[1] = 0x02fb5350;
        plan->source[2] = 0x02fb3d90;
        plan->source[3] = 0x02fb3e50;
    } else {
        plan->source[0] = 0x02fb5410;
        plan->source[1] = 0x02fb54d0;
        plan->source[2] = 0x02fb3f10;
        plan->source[3] = 0x02fb3fd0;
    }
    plan->count = 4;
}

/* Conditional plain family at 0xe2ad4: six expansions per bank. */
void recovered_video_dispatch_arm18(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    static const u32 bank_a_sources[6] = {
        0x02fb3d90, 0x02fb3e50, 0x02fb4990,
        0x02fb4a50, 0x02fb4c90, 0x02fb5350,
    };
    static const u32 bank_b_sources[6] = {
        0x02fb3f10, 0x02fb3fd0, 0x02fb4b10,
        0x02fb4bd0, 0x02fb4e10, 0x02fb4ed0,
    };
    const u32 *sources = bank_a != 0 ? bank_a_sources : bank_b_sources;
    u32 index;

    for (index = 0; index < 6; ++index) {
        plan->tile[index] = 1 + index * 2;
        plan->source[index] = sources[index];
    }
    plan->count = 6;
    plan->exit_address = bank_a != 0 ? 0x000e30a8 : 0x000e30cc;
}

/* Conditional plain family at 0xe2b88: four expansions per bank. */
void recovered_video_dispatch_arm19(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    static const u32 bank_a_sources[4] = {
        0x02fb4990, 0x02fb4a50, 0x02fb4c90, 0x02fb4d50,
    };
    static const u32 bank_b_sources[4] = {
        0x02fb4b10, 0x02fb4bd0, 0x02fb4e10, 0x02fb4ed0,
    };
    const u32 *sources = bank_a != 0 ? bank_a_sources : bank_b_sources;
    u32 index;

    for (index = 0; index < 4; ++index) {
        plan->tile[index] = 5 + index * 2;
        plan->source[index] = sources[index];
    }
    plan->count = 4;
    plan->exit_address = bank_a != 0 ? 0x000e2f24 : 0x000e2f48;
}

/* Conditional plain family at 0xe2c14: four expansions per bank. */
void recovered_video_dispatch_arm20(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    static const u32 bank_a_sources[4] = {
        0x02fb4c90, 0x02fb4d50, 0x02fb4390, 0x02fb4450,
    };
    static const u32 bank_b_sources[4] = {
        0x02fb4e10, 0x02fb4ed0, 0x02fb4510, 0x02fb45d0,
    };
    const u32 *sources = bank_a != 0 ? bank_a_sources : bank_b_sources;
    u32 index;

    plan->tile[0] = 9;
    plan->tile[1] = 11;
    plan->tile[2] = 1;
    plan->tile[3] = 3;
    for (index = 0; index < 4; ++index)
        plan->source[index] = sources[index];
    plan->count = 4;
    plan->exit_address = bank_a != 0 ? 0x000e2f70 : 0x000e2f94;
}

/* Conditional plain family at 0xe2ca0: four expansions per bank. */
void recovered_video_dispatch_arm21(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    static const u32 bank_a_sources[4] = {
        0x02fb4390, 0x02fb4450, 0x02fb4090, 0x02fb4150,
    };
    static const u32 bank_b_sources[4] = {
        0x02fb4510, 0x02fb45d0, 0x02fb4210, 0x02fb42d0,
    };
    const u32 *sources = bank_a != 0 ? bank_a_sources : bank_b_sources;
    u32 index;

    for (index = 0; index < 4; ++index) {
        plan->tile[index] = 1 + index * 2;
        plan->source[index] = sources[index];
    }
    plan->count = 4;
    plan->exit_address = bank_a != 0 ? 0x000e2fbc : 0x000e2fe0;
}

/* Conditional plain family at 0xe2d2c: six expansions per bank. */
void recovered_video_dispatch_arm22(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    static const u32 bank_a_sources[6] = {
        0x02fb4090, 0x02fb4150, 0x02fb5290,
        0x02fb5350, 0x02fb4f90, 0x02fb5050,
    };
    static const u32 bank_b_sources[6] = {
        0x02fb4210, 0x02fb42d0, 0x02fb5410,
        0x02fb54d0, 0x02fb5110, 0x02fb51d0,
    };
    const u32 *sources = bank_a != 0 ? bank_a_sources : bank_b_sources;
    u32 index;

    for (index = 0; index < 6; ++index) {
        plan->tile[index] = 5 + index * 2;
        plan->source[index] = sources[index];
    }
    plan->count = 6;
    plan->exit_address = 0x000e33f4;
}

/* Conditional plain family at 0xe2df8: two expansions per bank. */
void recovered_video_dispatch_arm23(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    plan->tile[0] = 9;
    plan->tile[1] = 11;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb5290;
        plan->source[1] = 0x02fb5350;
        plan->exit_address = 0x000e3008;
    } else {
        plan->source[0] = 0x02fb5410;
        plan->source[1] = 0x02fb54d0;
        plan->exit_address = 0x000e304c;
    }
    plan->count = 2;
}

/* Bank gate at 0xe2e44: no tile writes, only a continuation choice. */
u32 recovered_video_dispatch_arm24(u32 bank_a)
{
    return bank_a != 0 ? 0x000e3008 : 0x000e304c;
}

/* Conditional plain family at 0xe2eec: two expansions per bank. */
void recovered_video_dispatch_arm27(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    plan->tile[0] = 9;
    plan->tile[1] = 11;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb4c90;
        plan->source[1] = 0x02fb4d50;
    } else {
        plan->source[0] = 0x02fb4e10;
        plan->source[1] = 0x02fb4ed0;
    }
    plan->count = 2;
    plan->exit_address = bank_a != 0 ? 0x000e30a8 : 0x000e30cc;
}

/* Downstream bank gate at 0xe3004: four plain expansions per bank. */
void recovered_video_dispatch_arm28(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    plan->tile[0] = 1;
    plan->tile[1] = 3;
    plan->tile[2] = 5;
    plan->tile[3] = 7;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb4f90;
        plan->source[1] = 0x02fb5050;
        plan->source[2] = 0x02fb4690;
        plan->source[3] = 0x02fb4750;
    } else {
        plan->source[0] = 0x02fb5110;
        plan->source[1] = 0x02fb51d0;
        plan->source[2] = 0x02fb4810;
        plan->source[3] = 0x02fb48d0;
    }
    plan->count = 4;
    plan->exit_address = 0x000e33f4;
}

/* Downstream bank gate at 0xe3090: two plain expansions per bank. */
void recovered_video_dispatch_arm29(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    plan->tile[0] = 1;
    plan->tile[1] = 3;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb4c90;
        plan->source[1] = 0x02fb4d50;
    } else {
        plan->source[0] = 0x02fb4e10;
        plan->source[1] = 0x02fb4ed0;
    }
    plan->count = 2;
    plan->exit_address = 0x000e33f4;
}

/* Mirrored pointer-table arm at 0xe30dc. */
void recovered_video_dispatch_arm30(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 21;
    plan->source[0] = 0x00577598;
    plan->tile[1] = 23;
    plan->source[1] = 0x0057759c;
    plan->tile[2] = 25;
    plan->source[2] = 0x005775a0;
    plan->tile[3] = 27;
    plan->source[3] = 0x005775a4;
    plan->tile[4] = 29;
    plan->source[4] = 0x005775a8;
    plan->count = 5;
}

/* e3130 uses an immediate branch; the following mov 7 is unreachable. */
void recovered_video_dispatch_arm32(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 3;
    plan->source[0] = 0x02fb7d50;
    plan->count = 1;
}

/* Bank split at 0xe3248: eight e1fb0 expansions per path. */
void recovered_video_dispatch_arm33(
    u32 bank_a, struct recovered_video_large_helper_tile_plan *plan)
{
    plan->tile[0] = 1;
    plan->tile[1] = 3;
    plan->tile[2] = 5;
    plan->tile[3] = 7;
    plan->tile[4] = 21;
    plan->tile[5] = 25;
    plan->tile[6] = 27;
    plan->tile[7] = 29;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb3d90;
        plan->source[1] = 0x02fb3e50;
        plan->source[2] = 0x02fb4990;
        plan->source[3] = 0x02fb4a50;
    } else {
        plan->source[0] = 0x02fb3f10;
        plan->source[1] = 0x02fb3fd0;
        plan->source[2] = 0x02fb4b10;
        plan->source[3] = 0x02fb4bd0;
    }
    plan->source[4] = 0x02fb6cd0;
    plan->source[5] = 0x02fb7e10;
    plan->source[6] = 0x02bfed8c;
    plan->source[7] = 0x02fb6fd0;
    plan->helper = 0x000e1fb0;
    plan->count = 8;
    plan->exit_address = 0x000e33f4;
}

/* Selector-driven e1fb0 arm at 0xe319c. */
void recovered_video_dispatch_arm34(
    u32 bank_a, u32 selector, struct recovered_video_helper_tile_plan *plan)
{
    const u32 table = 0x00142f34;
    const u32 index = selector << 2;

    if (bank_a != 0) {
        plan->tile[0] = 1;
        plan->source[0] = table + selector * 16;
        plan->tile[1] = 3;
        plan->source[1] = table + (index | 1) * 4;
    } else if (selector == 5) {
        plan->tile[0] = 5;
        plan->source[0] = 0x00142f8c;
        plan->tile[1] = 7;
        plan->source[1] = table + (index | 3) * 4;
    } else {
        plan->tile[0] = 1;
        plan->source[0] = table + (index | 1) * 4;
        plan->tile[1] = 3;
        plan->source[1] = table + (index | 3) * 4;
    }
    plan->helper = 0x000e1fb0;
    plan->count = 2;
    plan->exit_address = 0x000e33f4;
}

/* Mixed e1fb0/e2040 arm at 0xe3314. */
void recovered_video_dispatch_arm35(
    u32 bank_a, u32 selector, struct recovered_video_mixed_tile_plan *plan)
{
    const u32 bank_a_table = 0x00142e94;
    const u32 bank_b_table = 0x00142f34;
    const u32 index = selector << 2;
    const u32 table = bank_a != 0 ? bank_a_table : bank_b_table;

    if (bank_a != 0) {
        plan->tile[0] = 1;
        plan->source[0] = table + selector * 16;
        plan->tile[1] = 3;
        plan->source[1] = table + (index | 1) * 4;
    } else if (selector == 5) {
        plan->tile[0] = 5;
        plan->source[0] = 0x00142f8c;
        plan->tile[1] = 7;
        plan->source[1] = table + (index | 3) * 4;
    } else {
        plan->tile[0] = 1;
        plan->source[0] = table + (index | 1) * 4;
        plan->tile[1] = 3;
        plan->source[1] = table + (index | 3) * 4;
    }
    plan->helper[0] = 0x000e1fb0;
    plan->helper[1] = 0x000e1fb0;
    plan->tile[2] = 25;
    plan->source[2] = 0x00143704;
    plan->helper[2] = 0x000e2040;
    plan->tile[3] = 27;
    plan->source[3] = 0x001437c4;
    plan->helper[3] = 0x000e2040;
    plan->tile[4] = 29;
    plan->source[4] = 0x02fb8590;
    plan->helper[4] = 0x000e2040;
    plan->count = 5;
    plan->exit_address = 0x000e33f4;
}

/* e33f4 sentinel gate, restricted to its complete 0x200 subpath. */
void recovered_video_dispatch_arm36(
    u32 sentinel, u32 bank_a, struct recovered_video_post_dispatch_plan *plan)
{
    plan->sentinel_match = sentinel == 0x00000200;
    plan->helper[0] = 0x000e2040;
    plan->helper[1] = 0x000e2040;
    plan->source[0] = 0x02fb5890;
    plan->source[1] = 0x02fb5950;
    plan->count = 0;
    plan->continuation = 0x000e3444;
    if (plan->sentinel_match != 0) {
        if (bank_a != 0) {
            plan->tile[0] = 5;
            plan->tile[1] = 7;
        } else {
            plan->tile[0] = 1;
            plan->tile[1] = 3;
        }
        plan->count = 2;
        plan->continuation = 0x000e35a0;
    }
}

/* Sentinel-0x21f payload at e349c, reached from the e3444 family. */
void recovered_video_dispatch_arm37(
    u32 bank_a, struct recovered_video_post_dispatch_plan *plan)
{
    plan->sentinel_match = 1;
    plan->helper[0] = 0x000e2040;
    plan->helper[1] = 0x000e2040;
    plan->source[0] = 0x02fb5a10;
    plan->source[1] = 0x02fb5ad0;
    if (bank_a != 0) {
        plan->tile[0] = 5;
        plan->tile[1] = 7;
    } else {
        plan->tile[0] = 1;
        plan->tile[1] = 3;
    }
    plan->count = 2;
    plan->continuation = 0x000e35a0;
}

/* Sentinel-indexed e2040 pair at e34e4, reached from the e3444 range gates. */
void recovered_video_dispatch_arm38(
    u32 sentinel, u32 bank_a, struct recovered_video_post_dispatch_plan *plan)
{
    const u32 offset = sentinel * 4;

    plan->sentinel_match = 1;
    plan->source[0] = 0x02bfd544 + offset;
    plan->source[1] = 0x02bfd5c4 + offset;
    plan->helper[0] = 0x000e2040;
    plan->helper[1] = 0x000e2040;
    if (bank_a != 0) {
        plan->tile[0] = 5;
        plan->tile[1] = 7;
    } else {
        plan->tile[0] = 1;
        plan->tile[1] = 3;
    }
    plan->count = 2;
    plan->continuation = 0x000e35a0;
}

/* Higher-range sentinel-indexed e2040 pair at e353c. */
void recovered_video_dispatch_arm39(
    u32 sentinel, u32 bank_a, struct recovered_video_post_dispatch_plan *plan)
{
    const u32 offset = sentinel * 4;

    plan->sentinel_match = 1;
    plan->source[0] = 0x02bfd5c4 + offset;
    plan->source[1] = 0x02bfd644 + offset;
    plan->helper[0] = 0x000e2040;
    plan->helper[1] = 0x000e2040;
    if (bank_a != 0) {
        plan->tile[0] = 5;
        plan->tile[1] = 7;
    } else {
        plan->tile[0] = 1;
        plan->tile[1] = 3;
    }
    plan->count = 2;
    plan->continuation = 0x000e35a0;
}

/* Terminal e35a0 side effect: release the dispatch sentinel. */
u32 recovered_video_dispatch_terminal_reset(void)
{
    return 0x000000ff;
}

/* Unsigned sentinel range partition beginning at e3444. */
enum recovered_video_post_route recovered_video_dispatch_post_route(u32 sentinel)
{
    u32 lower_delta = sentinel - 0x00000200;

    if (lower_delta <= 29)
        return RECOVERED_VIDEO_POST_LOWER;
    if (sentinel == 0x0000021f)
        return RECOVERED_VIDEO_POST_21F;
    if (sentinel - 0x00000400 <= 30)
        return RECOVERED_VIDEO_POST_MIDDLE;
    if (sentinel - 0x00000420 <= 31)
        return RECOVERED_VIDEO_POST_HIGH;
    return RECOVERED_VIDEO_POST_DONE;
}

/* Lower-range sentinel-indexed e2040 pair at e3444. */
void recovered_video_dispatch_arm40(
    u32 sentinel, u32 bank_a, struct recovered_video_post_dispatch_plan *plan)
{
    const u32 offset = sentinel * 4;

    plan->sentinel_match = 1;
    plan->source[0] = 0x00129e28 + offset;
    plan->source[1] = 0x00129ea8 + offset;
    plan->helper[0] = 0x000e2040;
    plan->helper[1] = 0x000e2040;
    if (bank_a != 0) {
        plan->tile[0] = 5;
        plan->tile[1] = 7;
    } else {
        plan->tile[0] = 1;
        plan->tile[1] = 3;
    }
    plan->count = 2;
    plan->continuation = 0x000e35a0;
}

/* Unconditional e1fb0-backed arm at 0xe314c. */
void recovered_video_dispatch_arm31(
    struct recovered_video_helper_tile_plan *plan)
{
    plan->tile[0] = 21;
    plan->source[0] = 0x02fb3d90;
    plan->tile[1] = 23;
    plan->source[1] = 0x00142dd4;
    plan->tile[2] = 25;
    plan->source[2] = 0x02fa5ad0;
    plan->tile[3] = 27;
    plan->source[3] = 0x02fabb90;
    plan->tile[4] = 29;
    plan->source[4] = 0x02fb1c50;
    plan->helper = 0x000e1fb0;
    plan->count = 5;
    plan->exit_address = 0x000e33f4;
}

/* Nested e2e4c payload arms: two plain expansions per bank. */
void recovered_video_dispatch_arm25(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    plan->tile[0] = 1;
    plan->tile[1] = 3;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb3d90;
        plan->source[1] = 0x02fb3e50;
    } else {
        plan->source[0] = 0x02fb3f10;
        plan->source[1] = 0x02fb3fd0;
    }
    plan->count = 2;
    plan->exit_address = 0x000e33f4;
}

/* Conditional plain family at 0xe2ea0: two expansions per bank. */
void recovered_video_dispatch_arm26(
    u32 bank_a, struct recovered_video_conditional_plain_plan *plan)
{
    plan->tile[0] = 5;
    plan->tile[1] = 7;
    if (bank_a != 0) {
        plan->source[0] = 0x02fb4990;
        plan->source[1] = 0x02fb4a50;
    } else {
        plan->source[0] = 0x02fb4b10;
        plan->source[1] = 0x02fb4bd0;
    }
    plan->count = 2;
    plan->exit_address = 0x000e33f4;
}

/* Mirrored arm at 0xe291c: three expansions and the e33e4 exit. */
void recovered_video_dispatch_arm12(struct recovered_video_exit_tile_plan *plan)
{
    plan->tile[0] = 23;
    plan->source[0] = 0x02fb8350;
    plan->tile[1] = 25;
    plan->source[1] = 0x02fb8410;
    plan->tile[2] = 27;
    plan->source[2] = 0x02fb84d0;
    plan->count = 3;
    plan->exit_address = 0x000e33e4;
}

/* Mirrored arm at 0xe2950: five expansions and the normal e33f4 exit. */
void recovered_video_dispatch_arm13(struct recovered_video_tile_plan *plan)
{
    plan->tile[0] = 21;
    plan->source[0] = 0x02fb7f90;
    plan->tile[1] = 23;
    plan->source[1] = 0x02fb8050;
    plan->tile[2] = 25;
    plan->source[2] = 0x02fb8110;
    plan->tile[3] = 27;
    plan->source[3] = 0x02fb81d0;
    plan->tile[4] = 29;
    plan->source[4] = 0x02fb8290;
    plan->count = 5;
}
