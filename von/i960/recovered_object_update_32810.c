/* Bounded state-dispatch and position-integration contract recovered from i960 0x32810.
 *
 * Covers the object-family state selector/dispatch at 0x33ae8-0x33b1c (table
 * 0x32560, 43 handlers, 16-byte stride) and the position integrator cores
 * 0x36044, 0x360c0, 0x363bc and 0x363e4. The geometry projection call and the
 * individual state-handler bodies are outside this bounded model.
 */

typedef unsigned int u32;

#define RECOVERED_OBJECT_UPDATE_STATE_FIELD 0x172U
#define RECOVERED_OBJECT_UPDATE_STATE_TABLE 0x32560U
#define RECOVERED_OBJECT_UPDATE_STATE_STRIDE 16U
#define RECOVERED_OBJECT_UPDATE_STATE_COUNT 43U
#define RECOVERED_OBJECT_UPDATE_STATE_MAX 42U
#define RECOVERED_OBJECT_UPDATE_ACTION_FIELD 0x1b2U
#define RECOVERED_OBJECT_UPDATE_ACTION_MAX 13U

struct recovered_object_update_32810_plan {
    u32 state_field_offset;
    u32 state_table_address;
    u32 state_table_stride;
    u32 state_handler_count;
    u32 state_max;
    u32 action_field_offset;
    u32 action_max;
    u32 state_handler[43];
};

struct recovered_object_update_32810_position {
    u32 x;  /* object +0x08 */
    u32 z;  /* object +0x10 */
    u32 vx; /* object +0x1c8 */
    u32 vz; /* object +0x1cc */
};

void recovered_object_update_32810_plan(
    struct recovered_object_update_32810_plan *plan)
{
    static const u32 handlers[43] = {
        0x0002f580U, 0x0002f930U, 0x0002e450U, 0x0002e590U, 0x0002e6f0U,
        0x0002e860U, 0x0002e990U, 0x0002eaa0U, 0x0002ebb0U, 0x0002ece0U,
        0x0002ef90U, 0x0002f010U, 0x0002f360U, 0x0002f260U, 0x0002f460U,
        0x0002fa20U, 0x0002fb20U, 0x0002fd50U, 0x00031910U, 0x00031ab0U,
        0x00031d20U, 0x00032120U, 0x0002fe30U, 0x0002ff80U, 0x000300c0U,
        0x00030230U, 0x00032330U, 0x000303e0U, 0x00030460U, 0x00030590U,
        0x00030420U, 0x00030660U, 0x00030c20U, 0x00030d40U, 0x00030e40U,
        0x00030ff0U, 0x00031210U, 0x000313e0U, 0x000315a0U, 0x000316d0U,
        0x000317f0U, 0x000324e0U, 0x00032540U
    };
    u32 index;

    plan->state_field_offset = RECOVERED_OBJECT_UPDATE_STATE_FIELD;
    plan->state_table_address = RECOVERED_OBJECT_UPDATE_STATE_TABLE;
    plan->state_table_stride = RECOVERED_OBJECT_UPDATE_STATE_STRIDE;
    plan->state_handler_count = RECOVERED_OBJECT_UPDATE_STATE_COUNT;
    plan->state_max = RECOVERED_OBJECT_UPDATE_STATE_MAX;
    plan->action_field_offset = RECOVERED_OBJECT_UPDATE_ACTION_FIELD;
    plan->action_max = RECOVERED_OBJECT_UPDATE_ACTION_MAX;
    for (index = 0U; index < RECOVERED_OBJECT_UPDATE_STATE_COUNT; ++index)
        plan->state_handler[index] = handlers[index];
}

/* The state selector is masked to 16 bits before the signed range guard. */
u32 recovered_object_update_32810_state_selector(u32 state_word)
{
    return (state_word << 16) >> 16;
}

/* Dispatch runs only when the masked, signed value is in 0..42. */
u32 recovered_object_update_32810_state_in_range(u32 state_word)
{
    u32 value = recovered_object_update_32810_state_selector(state_word);

    if ((value & 0x8000U) != 0U)
        return 0U;
    return value <= RECOVERED_OBJECT_UPDATE_STATE_MAX ? 1U : 0U;
}

/* Integrator core 0x363bc: object+0x08 += object+0x1c8; object+0x10 += object+0x1cc.
 * The i960 mnemonic `addr` is add-real (single precision), so this is a float add. */
void recovered_object_update_32810_integrate_position(
    struct recovered_object_update_32810_position *position)
{
    union {
        u32 bits;
        float value;
    } x, z, vx, vz;

    x.bits = position->x;
    z.bits = position->z;
    vx.bits = position->vx;
    vz.bits = position->vz;
    x.value += vx.value;
    z.value += vz.value;
    position->x = x.bits;
    position->z = z.bits;
}
