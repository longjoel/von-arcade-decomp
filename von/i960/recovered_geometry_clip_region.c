/* Signed branch classifier for the geometry clip family at 0x701a0. */
typedef unsigned int u32;

/* 0..3 select the four strict quadrants; 4 is the shared equality path. */
u32 recovered_geometry_clip_region(u32 x, u32 y, u32 right, u32 bottom)
{
    int sx = (int)x;
    int sy = (int)y;
    int sr = (int)right;
    int sb = (int)bottom;

    if (sx == sr || sy == sb)
        return 4U;
    if (sx < sr)
        return sy < sb ? 0U : 1U;
    return sy < sb ? 2U : 3U;
}
