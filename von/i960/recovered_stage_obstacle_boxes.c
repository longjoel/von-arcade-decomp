/* Recovered stage obstacle boxes: render-measured bounds plus kind.
 *
 * Bounds come from the t=150 stage export
 * (von/build/attract-coverage/manual-02/stage2-arena.glb), where local
 * coordinates equal world coordinates (verified by placing statics through
 * V^-1 * P against the west-wall matrix). All bounds are integral except
 * the B5 z minimum, which the export stores as 44.0000038 and is rounded
 * here to 44.
 *
 * Kinds are movement-evidenced, not game truth. Pads (B5/B6) contain the
 * spawn points (0, 0, +/-60) and are entered from the spawn frame in every
 * observed bout. Obstacles B1-B4 and C show a solid-until-broken pattern:
 * in the audio-queue bout S1, fighters approach (15/21/103 margin samples)
 * but never enter before break frames ~3910 (B2), ~4377 (B1), ~6722 (B3),
 * then enter freely after (22/29/81 samples); B4/C are never entered
 * there. The complementary manual-02 bout shows the mirror image: B1-B3
 * never entered even with margin, while the CPU walks through B4
 * (f=3575-3616) and C (f=4333-4360) at ground level with no health
 * change. Both directions support destructible obstacles whose break
 * set varies per bout; the collision-code site itself is still open.
 */

typedef unsigned int u32;
typedef signed int s32;

#define RECOVERED_OBSTACLE_KIND_BLOCK 0U
#define RECOVERED_OBSTACLE_KIND_PAD 1U

typedef struct {
    u32 oba;
    u32 kind;
    s32 min_x;
    s32 min_y;
    s32 min_z;
    s32 max_x;
    s32 max_y;
    s32 max_z;
} recovered_obstacle_box;

static const recovered_obstacle_box recovered_obstacle_boxes[7] = {
    {0x0080078eU, RECOVERED_OBSTACLE_KIND_BLOCK, -156, 0, 164, -124, 20, 236},
    {0x008003ddU, RECOVERED_OBSTACLE_KIND_BLOCK, -156, 0, -236, -124, 20, -164},
    {0x00800972U, RECOVERED_OBSTACLE_KIND_BLOCK, 124, 0, 164, 156, 20, 236},
    {0x0080055dU, RECOVERED_OBSTACLE_KIND_BLOCK, 124, 0, -236, 156, 20, -164},
    {0x00800126U, RECOVERED_OBSTACLE_KIND_PAD, -36, 0, 44, 36, 20, 76},
    {0x0080009dU, RECOVERED_OBSTACLE_KIND_PAD, -36, 0, -76, 36, 20, -44},
    {0x0080060eU, RECOVERED_OBSTACLE_KIND_BLOCK, 204, 0, -36, 236, 20, 36},
};

u32 recovered_obstacle_box_count(void)
{
    return 7U;
}

u32 recovered_obstacle_box_at(u32 index, recovered_obstacle_box *out)
{
    if (index >= 7U)
        return 0U;
    out->oba = recovered_obstacle_boxes[index].oba;
    out->kind = recovered_obstacle_boxes[index].kind;
    out->min_x = recovered_obstacle_boxes[index].min_x;
    out->min_y = recovered_obstacle_boxes[index].min_y;
    out->min_z = recovered_obstacle_boxes[index].min_z;
    out->max_x = recovered_obstacle_boxes[index].max_x;
    out->max_y = recovered_obstacle_boxes[index].max_y;
    out->max_z = recovered_obstacle_boxes[index].max_z;
    return 1U;
}
