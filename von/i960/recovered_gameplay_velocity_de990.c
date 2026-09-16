/*
 * Faithful bounded recovered model of the i960 velocity producer at
 * 0x000de990-0x000df058.
 *
 * The routine reads the literal stage/state pair at 0x503b00/0x504100,
 * unconditionally clears the player velocity words 0x503c98/0x503c9c, and
 * either the stage==4 or state==1 gate (or the two fallback states) selects one
 * of three shapes:
 *
 *   1. DOUBLED_NEGATED_OTHER  -- one object is left at zero and the other
 *      receives 2.0 * (-r) for both response lanes.  Selected when the
 *      0x504134 mode word is 9 (70.0) or 8 (30.0), or when the 0x503b34 mode
 *      word is 9 or 8 in the gate path.
 *   2. SIGNED                 -- the service-38 object receives r unchanged and
 *      the service-39 object receives -r.  Selected by both 10.4 default arms.
 *   3. DOUBLED_SELF           -- the service-38 object receives 2.0 * r and the
 *      service-39 object is untouched.  Selected only by the state==3 arm.
 *
 * Everything below the mode decision is pure: no MMIO is performed here.  The
 * 0x884000 service-38/39 packet is emitted into a word array, and the three
 * FIFO responses are consumed by recovered_gameplay_velocity_de990_apply.
 *
 * Signedness and lane width: the two response lanes are independent 32-bit
 * words loaded by the 64-bit ldl at 0xdea94 / 0xdee58 / 0xdf024; they are not a
 * packed 16-bit pair.  The velocity stores at +0x1c8/+0x1cc are 32-bit st
 * operations, so no 16-bit truncation occurs on this path.  The listing's
 * notbit 31 is a sign-bit toggle (MAME i960.cpp: dst = src ^ (1 << bit)), used
 * to flip the direction of the published vector.  For the negative responses
 * this routine consumes it therefore doubles the magnitude, which is the
 * "2.0 * |r|" reading; it is not a magnitude clamp.
 */

typedef unsigned int u32;

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_FIFO 0x00884000U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_SERVICE_SELF 38U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_SERVICE_OTHER 39U

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_PLAYER_BASE 0x00503ad0U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_CPU_BASE 0x005040d0U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_POSITION_OFFSET 0x008U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_VELOCITY_OFFSET 0x1c8U

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_PLAYER_VELOCITY 0x00503c98U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_CPU_VELOCITY 0x00504298U

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_MODE_STAGE 0x00503b00U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_MODE_STATE 0x00504100U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_MODE_PRIMARY 0x00504134U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_MODE_SECONDARY 0x00503b34U

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_70 0x428c0000U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_30 0x41f00000U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_DEFAULT 0x41266666U

enum {
    RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER = 0,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU = 1
};

enum {
    RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_NONE = 0,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_NEGATED_OTHER = 1,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_SIGNED = 2,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_SELF = 3
};

enum {
    RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_504134_MODE9 = 0,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_504134_MODE8 = 1,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_503B34_MODE9 = 2,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_503B34_MODE8 = 3,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_GATE_DEFAULT = 4,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_STATE3_DOUBLED = 5,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_STATE_DEFAULT_SIGNED = 6
};

struct recovered_gameplay_velocity_de990_plan {
    u32 clear_player;
    u32 clear_cpu;
    u32 self_object;
    u32 other_object;
    u32 threshold_bits;
    u32 transform;
    u32 selection;
};

struct recovered_gameplay_velocity_de990_velocity {
    u32 player_written;
    u32 cpu_written;
    u32 player[2];
    u32 cpu[2];
};

struct recovered_gameplay_velocity_de990_packet {
    u32 service_self;
    u32 service_other;
    u32 word_count;
    u32 words[10];
};

static float recovered_gameplay_velocity_de990_as_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return input.value;
}

static u32 recovered_gameplay_velocity_de990_as_bits(float value)
{
    union {
        u32 bits;
        float value;
    } output;

    output.value = value;
    return output.bits;
}

/* The listing's notbit 31 inverts the sign bit of each 32-bit lane. */
u32 recovered_gameplay_velocity_de990_toggle_sign(u32 bits)
{
    return bits ^ 0x80000000U;
}

/* The doubled arms run the value through movr, addrl (an IEEE double add of
 * the value with itself) and movr back, so the truncating f2u conversion of
 * the exact double sum is reproduced here. */
u32 recovered_gameplay_velocity_de990_double(u32 bits)
{
    float value = recovered_gameplay_velocity_de990_as_float(bits);
    double doubled = (double)value + (double)value;

    return recovered_gameplay_velocity_de990_as_bits((float)doubled);
}

static void recovered_gameplay_velocity_de990_choose(
    struct recovered_gameplay_velocity_de990_plan *plan, u32 self_object,
    u32 other_object, u32 threshold_bits, u32 transform, u32 selection)
{
    plan->self_object = self_object;
    plan->other_object = other_object;
    plan->threshold_bits = threshold_bits;
    plan->transform = transform;
    plan->selection = selection;
}

/*
 * Reproduce the 0xde9a8..0xdee90 branch tree.  The two ldos operands are
 * zero-extended 16-bit values; the 0x504134/0x503b34 modes are full 32-bit
 * loads.  Return the descriptor that the emission and velocity stages consume.
 */
void recovered_gameplay_velocity_de990_select(
    u32 stage_503b00, u32 state_504100, u32 mode_504134, u32 mode_503b34,
    struct recovered_gameplay_velocity_de990_plan *plan)
{
    u32 stage = stage_503b00 & 0xffffU;
    u32 state = state_504100 & 0xffffU;

    plan->clear_player = 1U;
    if (stage == 4U || state == 1U) {
        /* 0xde9c0: the literal-first gate clears both velocity pairs. */
        plan->clear_cpu = 1U;
        if (mode_504134 == 9U) {
            recovered_gameplay_velocity_de990_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_70,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_NEGATED_OTHER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_504134_MODE9);
        } else if (mode_504134 == 8U) {
            recovered_gameplay_velocity_de990_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_30,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_NEGATED_OTHER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_504134_MODE8);
        } else if (mode_503b34 == 9U) {
            recovered_gameplay_velocity_de990_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_70,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_NEGATED_OTHER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_503B34_MODE9);
        } else if (mode_503b34 == 8U) {
            recovered_gameplay_velocity_de990_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_30,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_NEGATED_OTHER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_503B34_MODE8);
        } else {
            recovered_gameplay_velocity_de990_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_DEFAULT,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_SIGNED,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_GATE_DEFAULT);
        }
    } else if (state == 3U) {
        /* 0xdee88->0xdef7c: state 3 skips the CPU clear and doubles self. */
        plan->clear_cpu = 0U;
        recovered_gameplay_velocity_de990_choose(
            plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_DEFAULT,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_SELF,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_STATE3_DOUBLED);
    } else {
        /* 0xdee88->0xdee94: CPU is cleared, then player keeps r and CPU gets -r. */
        plan->clear_cpu = 1U;
        recovered_gameplay_velocity_de990_choose(
            plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_CPU,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_THRESHOLD_DEFAULT,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_SIGNED,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_SELECT_STATE_DEFAULT_SIGNED);
    }
}

/*
 * Build the ten-word packet the routine writes to 0x884000: service 38 with the
 * self position triple, the selected threshold and zero, then service 39 with
 * the other position triple.  No MMIO is performed.
 */
void recovered_gameplay_velocity_de990_build_packet(
    const struct recovered_gameplay_velocity_de990_plan *plan,
    const u32 self_position[3], const u32 other_position[3],
    struct recovered_gameplay_velocity_de990_packet *packet)
{
    packet->service_self = RECOVERED_GAMEPLAY_VELOCITY_DE990_SERVICE_SELF;
    packet->service_other = RECOVERED_GAMEPLAY_VELOCITY_DE990_SERVICE_OTHER;
    packet->word_count = 10U;
    packet->words[0] = RECOVERED_GAMEPLAY_VELOCITY_DE990_SERVICE_SELF;
    packet->words[1] = self_position[0];
    packet->words[2] = self_position[1];
    packet->words[3] = self_position[2];
    packet->words[4] = plan->threshold_bits;
    packet->words[5] = 0U;
    packet->words[6] = RECOVERED_GAMEPLAY_VELOCITY_DE990_SERVICE_OTHER;
    packet->words[7] = other_position[0];
    packet->words[8] = other_position[1];
    packet->words[9] = other_position[2];
}

static void recovered_gameplay_velocity_de990_publish(
    struct recovered_gameplay_velocity_de990_velocity *velocity, u32 object,
    u32 low, u32 high)
{
    if (object == RECOVERED_GAMEPLAY_VELOCITY_DE990_OBJECT_PLAYER) {
        velocity->player[0] = low;
        velocity->player[1] = high;
        velocity->player_written = 1U;
    } else {
        velocity->cpu[0] = low;
        velocity->cpu[1] = high;
        velocity->cpu_written = 1U;
    }
}

/*
 * Apply the three FIFO responses to the selected object layout.  A zero third
 * response is the out-of-range gate: the routine returns at 0xdead0 / 0xdebc4 /
 * 0xdedac / 0xdee84 / 0xdef78 / 0xdf058 before any velocity store, so nothing is
 * published (the earlier clears are the caller-visible residue).  Return 1 when
 * the velocity pair was published and 0 when the gate suppressed it.
 */
u32 recovered_gameplay_velocity_de990_apply(
    const struct recovered_gameplay_velocity_de990_plan *plan,
    u32 response_1, u32 response_2, u32 response_3,
    struct recovered_gameplay_velocity_de990_velocity *velocity)
{
    velocity->player_written = 0U;
    velocity->cpu_written = 0U;
    velocity->player[0] = 0U;
    velocity->player[1] = 0U;
    velocity->cpu[0] = 0U;
    velocity->cpu[1] = 0U;

    if (response_3 == 0U)
        return 0U;

    switch (plan->transform) {
    case RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_NEGATED_OTHER:
        recovered_gameplay_velocity_de990_publish(
            velocity, plan->other_object,
            recovered_gameplay_velocity_de990_double(
                recovered_gameplay_velocity_de990_toggle_sign(response_1)),
            recovered_gameplay_velocity_de990_double(
                recovered_gameplay_velocity_de990_toggle_sign(response_2)));
        break;
    case RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_DOUBLED_SELF:
        recovered_gameplay_velocity_de990_publish(
            velocity, plan->self_object,
            recovered_gameplay_velocity_de990_double(response_1),
            recovered_gameplay_velocity_de990_double(response_2));
        break;
    case RECOVERED_GAMEPLAY_VELOCITY_DE990_TRANSFORM_SIGNED:
        recovered_gameplay_velocity_de990_publish(
            velocity, plan->self_object, response_1, response_2);
        recovered_gameplay_velocity_de990_publish(
            velocity, plan->other_object,
            recovered_gameplay_velocity_de990_toggle_sign(response_1),
            recovered_gameplay_velocity_de990_toggle_sign(response_2));
        break;
    default:
        break;
    }
    return 1U;
}
