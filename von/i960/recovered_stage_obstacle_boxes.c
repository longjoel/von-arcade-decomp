/* Recovered stage obstacle boxes: render-measured bounds plus kind.
 *
 * Bounds come from the t=150 stage export
 * (von/build/attract-coverage/manual-02/stage2-arena.glb), where local
 * coordinates equal world coordinates (verified by placing statics through
 * V^-1 * P against the west-wall matrix). All bounds are integral except
 * the B5 z minimum, which the export stores as 44.0000038 and is rounded
 * here to 44.
 *
 * Kinds are movement-evidenced. Pads (B5/B6) contain the spawn points
 * (0, 0, +/-60) and are entered from the spawn frame in every observed bout.
 * The other boxes are solid, permanent obstacles: nothing in any map is
 * destructible (confirmed on hardware), so the earlier "solid-until-broken"
 * reading was a movement artefact. Obstacle tops are landing surfaces - a
 * fighter can jump onto an obstacle. The collision-code site is still open.
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
