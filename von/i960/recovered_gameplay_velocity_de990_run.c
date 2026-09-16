/*
 * Runnable, freestanding recovered-C driver for the i960 velocity producer at
 * 0x000de990-0x000df058.
 *
 * The routine services one player/CPU pair through the 0x884000 FIFO.  The
 * listing copies the same body across three mode arms:
 *
 *   0x428c0000 (70.0), 0x504134 == 9         -> self=CPU,    other=player
 *   0x41f00000 (30.0), 0x504134 == 8         -> self=CPU,    other=player
 *   0x428c0000 (70.0), 0x503b34 == 9         -> self=player, other=CPU
 *   0x41f00000 (30.0), 0x503b34 == 8         -> self=player, other=CPU
 *   0x41266666 (10.4), gate default          -> self=CPU,    other=player, signed
 *   0x41266666 (10.4), state == 3            -> self=player, doubled self
 *   0x41266666 (10.4), other fallback state  -> self=player, other=CPU, signed
 *
 * This file is deliberately self-contained: it links into the freestanding
 * i960 image without libc, without the GCC soft-float runtime, and without the
 * float-typed pure model in recovered_gameplay_velocity_de990.c.  It mirrors
 * that model's select/apply semantics, but the listing's notbit 31 and addrl
 * floating-point doubling are re-expressed as 32-bit integer bit operations.
 *
 * Integer-only float model
 * ------------------------
 * The FIFO responses read from 0x884000 are raw 32-bit IEEE-754 single words.
 * The listing consumes them with:
 *
 *   notbit 31,<src>,<dst>       dst = src ^ 0x80000000     (sign-bit flip)
 *   movr / addrl x,x / movr     float( (double)x + (double)x )
 *
 * For every normal finite single, doubling is exactly a one-step increment of
 * the biased exponent (the significand is untouched), so
 * recovered_gameplay_velocity_de990_scale2x is exponent+1 plus the sign:
 *
 *   exponent 0x00        +/-0 and denormals: returned unchanged.  The board
 *                        responses on this path are normal velocities, so the
 *                        conservative identity is chosen over denormal
 *                        normalization.
 *   exponent 0x01..0xfd  exponent+1, sign and significand preserved.
 *   exponent 0xfe        the doubled single overflows, so saturate to
 *                        infinity (0x7f800000 masked with the sign bit; the
 *                        addrl/movr path yields -inf for negative operands).
 *   exponent 0xff        +/-inf and NaN: returned unchanged (quiet NaN stays
 *                        quiet because the payload is preserved).
 *
 * No float or double arithmetic is emitted, so this object has no soft-float
 * dependencies.  recovered_gameplay_velocity_de990_flip31 is the notbit 31
 * operation, layered by the caller exactly where the listing places it.
 *
 * Memory layout (from the listing):
 *   player base 0x00503ad0  position +0x08/+0x0c/+0x10  velocity +0x1c8/+0x1cc
 *   CPU    base 0x005040d0  position +0x08/+0x0c/+0x10  velocity +0x1c8/+0x1cc
 *   stage 0x00503b00 (u16)  state 0x00504100 (u16)
 *   primary mode 0x00504134 (u32)  secondary mode 0x00503b34 (u32)
 *   FIFO 0x00884000, service words 38 (0x26) then 39 (0x27).
 */

typedef unsigned int u32;
typedef unsigned short u16;

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_FIFO 0x00884000U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_SERVICE_SELF 38U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_SERVICE_OTHER 39U

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_POSITION_0 0x00503ad8U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_POSITION_1 0x00503adcU
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_POSITION_2 0x00503ae0U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_POSITION_0 0x005040d8U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_POSITION_1 0x005040dcU
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_POSITION_2 0x005040e0U

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_VELOCITY_0 0x00503c98U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_VELOCITY_1 0x00503c9cU
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_VELOCITY_0 0x00504298U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_VELOCITY_1 0x0050429cU

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_STAGE 0x00503b00U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_STATE 0x00504100U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_PRIMARY 0x00504134U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_SECONDARY 0x00503b34U

#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_70 0x428c0000U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_30 0x41f00000U
#define RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_DEFAULT 0x41266666U

enum {
    RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER = 0,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU = 1
};

enum {
    RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_NEGATED_OTHER = 0,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_SIGNED = 1,
    RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_SELF = 2
};

struct recovered_gameplay_velocity_de990_run_plan {
    u32 clear_player;
    u32 clear_cpu;
    u32 self_object;
    u32 other_object;
    u32 threshold_bits;
    u32 rule;
};

struct recovered_gameplay_velocity_de990_run_velocity {
    u32 player_written;
    u32 cpu_written;
    u32 player[2];
    u32 cpu[2];
};

/*
 * notbit 31: 0xdead4 notbit 31,g6,g4.  MAME's i960 core computes
 * dst = src ^ (1 << bit), so this is an unconditional sign toggle.
 */
u32 recovered_gameplay_velocity_de990_flip31(u32 bits)
{
    return bits ^ 0x80000000U;
}

/*
 * The addrl doubling of the listing arms, in integer bit space.  See the file
 * comment for the exponent table; this is 2.0 * x for a normal float with the
 * sign preserved and overflow saturated to infinity.
 */
u32 recovered_gameplay_velocity_de990_scale2x(u32 bits)
{
    u32 exponent = (bits >> 23) & 0xffU;
    u32 sign = bits & 0x80000000U;
    u32 significand = bits & 0x007fffffU;

    if (exponent == 0x00U || exponent == 0xffU)
        return bits;
    if (exponent == 0xfeU)
        return sign | 0x7f800000U;
    return sign | ((exponent + 1U) << 23) | significand;
}

static void recovered_gameplay_velocity_de990_run_choose(
    struct recovered_gameplay_velocity_de990_run_plan *plan, u32 self_object,
    u32 other_object, u32 threshold_bits, u32 rule)
{
    plan->self_object = self_object;
    plan->other_object = other_object;
    plan->threshold_bits = threshold_bits;
    plan->rule = rule;
}

/*
 * Pure reproduction of the 0xde9a8..0xdee90 branch tree.  The stage/state
 * operands are the zero-extended 16-bit ldos words; the two mode operands are
 * full 32-bit loads.  The clear_player bit is always set (0xde998/0xde9a0) and
 * clear_cpu follows the 0xde9c0 gate and the 0xdee94 signed fallback, while the
 * state==3 arm at 0xdef7c leaves the CPU pair alone.
 */
void recovered_gameplay_velocity_de990_run_select(
    u32 stage_503b00, u32 state_504100, u32 mode_504134, u32 mode_503b34,
    struct recovered_gameplay_velocity_de990_run_plan *plan)
{
    u32 stage = stage_503b00 & 0xffffU;
    u32 state = state_504100 & 0xffffU;

    plan->clear_player = 1U;
    if (stage == 4U || state == 1U) {
        plan->clear_cpu = 1U;
        if (mode_504134 == 9U) {
            recovered_gameplay_velocity_de990_run_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_70,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_NEGATED_OTHER);
        } else if (mode_504134 == 8U) {
            recovered_gameplay_velocity_de990_run_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_30,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_NEGATED_OTHER);
        } else if (mode_503b34 == 9U) {
            recovered_gameplay_velocity_de990_run_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_70,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_NEGATED_OTHER);
        } else if (mode_503b34 == 8U) {
            recovered_gameplay_velocity_de990_run_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_30,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_NEGATED_OTHER);
        } else {
            recovered_gameplay_velocity_de990_run_choose(
                plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_DEFAULT,
                RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_SIGNED);
        }
    } else if (state == 3U) {
        plan->clear_cpu = 0U;
        recovered_gameplay_velocity_de990_run_choose(
            plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_DEFAULT,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_SELF);
    } else {
        plan->clear_cpu = 1U;
        recovered_gameplay_velocity_de990_run_choose(
            plan, RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_CPU,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_THRESHOLD_DEFAULT,
            RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_SIGNED);
    }
}

static void recovered_gameplay_velocity_de990_run_publish(
    struct recovered_gameplay_velocity_de990_run_velocity *velocity, u32 object,
    u32 low, u32 high)
{
    if (object == RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER) {
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
 * Pure application of the three responses to the selected object layout.  The
 * third response is the out-of-range gate: a zero returns 0 without touching
 * either velocity pair, matching the ret at 0xdead0/0xdebc4/0xdedac/0xdee84/
 * 0xdef78/0xdf058 before the stores.
 */
u32 recovered_gameplay_velocity_de990_run_apply(
    const struct recovered_gameplay_velocity_de990_run_plan *plan,
    u32 response_1, u32 response_2, u32 response_3,
    struct recovered_gameplay_velocity_de990_run_velocity *velocity)
{
    velocity->player_written = 0U;
    velocity->cpu_written = 0U;
    velocity->player[0] = 0U;
    velocity->player[1] = 0U;
    velocity->cpu[0] = 0U;
    velocity->cpu[1] = 0U;

    if (response_3 == 0U)
        return 0U;

    switch (plan->rule) {
    case RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_NEGATED_OTHER:
        recovered_gameplay_velocity_de990_run_publish(
            velocity, plan->other_object,
            recovered_gameplay_velocity_de990_scale2x(
                recovered_gameplay_velocity_de990_flip31(response_1)),
            recovered_gameplay_velocity_de990_scale2x(
                recovered_gameplay_velocity_de990_flip31(response_2)));
        break;
    case RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_DOUBLED_SELF:
        recovered_gameplay_velocity_de990_run_publish(
            velocity, plan->self_object,
            recovered_gameplay_velocity_de990_scale2x(response_1),
            recovered_gameplay_velocity_de990_scale2x(response_2));
        break;
    case RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_RULE_SIGNED:
        recovered_gameplay_velocity_de990_run_publish(
            velocity, plan->self_object, response_1, response_2);
        recovered_gameplay_velocity_de990_run_publish(
            velocity, plan->other_object,
            recovered_gameplay_velocity_de990_flip31(response_1),
            recovered_gameplay_velocity_de990_flip31(response_2));
        break;
    default:
        break;
    }
    return 1U;
}

static void recovered_gameplay_velocity_de990_run_read_self(
    u32 self_object, u32 *x, u32 *y, u32 *z)
{
    if (self_object == RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_OBJECT_PLAYER) {
        *x = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_POSITION_0;
        *y = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_POSITION_1;
        *z = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_POSITION_2;
    } else {
        *x = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_POSITION_0;
        *y = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_POSITION_1;
        *z = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_POSITION_2;
    }
}

static void recovered_gameplay_velocity_de990_run_read_other(
    u32 other_object, u32 *x, u32 *y, u32 *z)
{
    recovered_gameplay_velocity_de990_run_read_self(other_object, x, y, z);
}

/*
 * The callable body of 0xde990.  The player always clears its velocity pair;
 * the CPU pair is cleared whenever the selection sets clear_cpu (the
 * stage==4/state==1 gate at 0xde9c0 and the non-state-3 signed fallback at
 * 0xdee94).  The selected self/other positions are emitted around the 0x26/0x27
 * services, the three responses are collected, and the selected rule writes the
 * two velocity lanes at the destination object's +0x1c8/+0x1cc.
 */
void recovered_gameplay_velocity_de990_run(void)
{
    struct recovered_gameplay_velocity_de990_run_plan plan;
    struct recovered_gameplay_velocity_de990_run_velocity velocity;
    u16 stage_503b00 = *(volatile u16 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_STAGE;
    u16 state_504100 = *(volatile u16 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_STATE;
    u32 mode_504134 = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_PRIMARY;
    u32 mode_503b34 = *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_MODE_SECONDARY;
    u32 self_x, self_y, self_z;
    u32 other_x, other_y, other_z;
    u32 response_1, response_2, response_3;

    recovered_gameplay_velocity_de990_run_select(
        stage_503b00, state_504100, mode_504134, mode_503b34, &plan);

    *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_VELOCITY_0 = 0U;
    *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_VELOCITY_1 = 0U;
    if (plan.clear_cpu != 0U) {
        *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_VELOCITY_0 = 0U;
        *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_VELOCITY_1 = 0U;
    }

    recovered_gameplay_velocity_de990_run_read_self(
        plan.self_object, &self_x, &self_y, &self_z);
    recovered_gameplay_velocity_de990_run_read_other(
        plan.other_object, &other_x, &other_y, &other_z);

    *(volatile unsigned int *)0x884000U = RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_SERVICE_SELF;
    *(volatile unsigned int *)0x884000U = self_x;
    *(volatile unsigned int *)0x884000U = self_y;
    *(volatile unsigned int *)0x884000U = self_z;
    *(volatile unsigned int *)0x884000U = plan.threshold_bits;
    *(volatile unsigned int *)0x884000U = 0U;
    *(volatile unsigned int *)0x884000U = RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_SERVICE_OTHER;
    *(volatile unsigned int *)0x884000U = other_x;
    *(volatile unsigned int *)0x884000U = other_y;
    *(volatile unsigned int *)0x884000U = other_z;

    response_1 = *(volatile unsigned int *)0x884000U;
    response_2 = *(volatile unsigned int *)0x884000U;
    response_3 = *(volatile unsigned int *)0x884000U;

    if (recovered_gameplay_velocity_de990_run_apply(
            &plan, response_1, response_2, response_3, &velocity) == 0U)
        return;

    if (velocity.player_written != 0U) {
        *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_VELOCITY_0 =
            velocity.player[0];
        *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_PLAYER_VELOCITY_1 =
            velocity.player[1];
    }
    if (velocity.cpu_written != 0U) {
        *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_VELOCITY_0 =
            velocity.cpu[0];
        *(volatile u32 *)RECOVERED_GAMEPLAY_VELOCITY_DE990_RUN_CPU_VELOCITY_1 =
            velocity.cpu[1];
    }
}
