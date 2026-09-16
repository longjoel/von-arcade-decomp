/*
 * Bounded freestanding recovered-C runnable unit for the i960 velocity
 * accumulation block reached at 0x000358ac inside the 0x32810 per-object
 * update.  The listing span modelled here is 0x000358ac-0x00035cd4; the
 * registered ledger range is 0x000358ac-0x00035c28.
 *
 * The block services the SHARC velocity packet:
 *
 *   0x358ac  mov 6,r11 / st r11,0x884000      service word 6, no response
 *   0x358b8  ldos 0x30(r8),g4
 *   0x358bc  cmpibe 3,g4,0x36458              +0x30 == 3 returns at 0x36458
 *   0x358c0  ldos 0x186(r8),g4
 *   0x358c4  ldos 0x184(r8),g5
 *   0x358c8  shlo 1,g4,g4
 *   0x358cc  addo g5,g4,g4
 *   0x358d0  stos g4,0x2e(r8)                 +0x2e = +0x184 + 2*+0x186
 *   0x358d4  ldos 0x19c(r8),g4
 *   0x358d8  cmpibe 0,g4,0x3596c              +0x19c == 0 takes the state arm
 *
 * The primary arm (0x358dc-0x35968) clamps +0x1c4 to +0x7c, emits opcode 29
 * with the facing halfword +0x184 and the speed scalar +0x1c4 sign-flipped by
 * notbit 31, accumulates response 29 into +0x1c8, emits opcode 30 with the
 * masked facing and the raw speed, and carries response 30 to the shared tail
 * at 0x35bcc, which accumulates it into +0x1cc.  Because i960 `addr` is
 * add-real, those two stores are single-precision float adds.  Both exchanges
 * read the signed angle as the low 16 bits of the file word; the SHARC
 * opcode-0x1d (sin) and opcode-0x1e (cos) contracts multiply the sinusoid by
 * the delayed multiplier word, so response 29 lands in x (+0x1c8) and response
 * 30 lands in z (+0x1cc).
 *
 * Three more packet-29/30 shapes share the same tail:
 *
 *   0x3597c  state == 19 or 20: angle +0x3c, unclamped +0x1c4
 *   0x35a08  state == 31 or 34: angle +0x3c, unclamped +0x1c4
 *   0x35a80  every other state: normalise +0x1c4 when +0x7c < 70.0
 *            (speed = speed * (+0x7c + 130.0) / 200.0) and combine four
 *            exchanges of the +0x184 facing against the +0xf4/+0xf8
 *            multipliers, then x += flip31(respA + respB) * speed and
 *            z += (flip31(respC) + respD) * speed.
 *
 * After the shared tail the block re-reads object +0x172 and appends one more
 * pair of exchanges for state 18 (+0x670 multiplier) or for state 11 when
 * +0x190 != 0 (+0x678 multiplier), both against the +0x3c angle.  The block
 * ends at 0x35cd4, before the service-31/10 sequence and the 0x6f6f0 geometry
 * projection call, neither of which is reproduced here.  The 14-entry action
 * and 43-entry state handlers of 0x32810 are likewise untouched.
 *
 * The FIFO responses are external board behaviour; this file consumes whatever
 * 0x884000 returns.  Only the object +0x184/+0x1c4 operands, the notbit-31
 * multiplier flip, the +0x7c clamp, the 130/200 scaling and the add-real
 * velocity accumulation are modelled.  The pure helpers below are what the
 * host test exercises; _run touches absolute MMIO and is never called there.
 */

typedef unsigned short u16;
typedef unsigned int u32;

#define RECOVERED_VELOCITY_ACCUMULATE_358AC_FIFO 0x00884000U
#define RECOVERED_VELOCITY_ACCUMULATE_358AC_TABLE_SLOT 0x0051ab14U

#define RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_6 6U
#define RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_29 29U
#define RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_30 30U

/* the +0x1c4 > +0x7c clamp, the +0x7c < 70.0 scale gate and the 130/200
 * scale factors are all read or formed by the listing (0x358dc-0x358f0 and
 * 0x35a80-0x35ad8); 0x40518000/0x40604000/0x40690000 are the high words of
 * the double constants 70.0, 130.0 and 200.0 in the r10:r11/g4:g5/g6:g7
 * register pairs. */
#define RECOVERED_VELOCITY_ACCUMULATE_358AC_LIMIT_70 70.0
#define RECOVERED_VELOCITY_ACCUMULATE_358AC_SCALE_OFFSET 130.0
#define RECOVERED_VELOCITY_ACCUMULATE_358AC_SCALE_DIVISOR 200.0

static float recovered_velocity_accumulate_358ac_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return input.value;
}

static u32 recovered_velocity_accumulate_358ac_bits(float value)
{
    union {
        u32 bits;
        float value;
    } output;

    output.value = value;
    return output.bits;
}

/*
 * notbit 31,g4,g4 at 0x35910/0x35998/0x35a24 (multiplier) and
 * notbit 31,g5,g5 / notbit 31,g4,g4 at 0x35b50/0x35bbc (target response).
 * MAME's i960 core computes dst = src ^ (1 << bit).
 */
u32 recovered_velocity_accumulate_358ac_flip31(u32 bits)
{
    return bits ^ 0x80000000U;
}

/*
 * i960 `addr` add-real: dst = dst + src as a single-precision float.  This is
 * the +0x1c8/+0x1cc accumulation used at 0x35928, 0x359b0, 0x35a3c, 0x35b60,
 * 0x35bc0, 0x35c1c and 0x35c88.  Addition is commutative, so the listing's
 * operand order (response, lane) is not observable here.
 */
u32 recovered_velocity_accumulate_358ac_add_lane(u32 lane_bits, u32 addend_bits)
{
    return recovered_velocity_accumulate_358ac_bits(
        recovered_velocity_accumulate_358ac_float(lane_bits)
        + recovered_velocity_accumulate_358ac_float(addend_bits));
}

/* mulr at 0x35b54/0x35bc8: single-precision product. */
static u32 recovered_velocity_accumulate_358ac_mul(u32 a_bits, u32 b_bits)
{
    return recovered_velocity_accumulate_358ac_bits(
        recovered_velocity_accumulate_358ac_float(a_bits)
        * recovered_velocity_accumulate_358ac_float(b_bits));
}

/*
 * 0x358dc-0x358f0: ld +0x1c4,speed; ld +0x7c,limit; cmpr speed,limit; ble
 * past the store; otherwise +0x1c4 = +0x7c.  cmp_d leaves the i960 condition
 * bits clear for an unordered (NaN) compare, so ble is not taken and the clamp
 * fires; !(speed <= limit) reproduces that exactly.
 */
u32 recovered_velocity_accumulate_358ac_clamp_speed(u32 speed_bits, u32 limit_bits)
{
    float speed = recovered_velocity_accumulate_358ac_float(speed_bits);
    float limit = recovered_velocity_accumulate_358ac_float(limit_bits);

    if (!(speed <= limit))
        return limit_bits;
    return speed_bits;
}

/*
 * 0x35a80-0x35ad8: when +0x7c < 70.0 the speed is rescaled in double
 * precision, (double)speed * ((double)limit + 130.0) / 200.0, and rounded back
 * to a single before it is stored to +0x1c4.  cmprl fp0,r10; bge skips the
 * whole arm when limit >= 70.0, so the helper returns the original bits then.
 */
u32 recovered_velocity_accumulate_358ac_scale_speed(u32 speed_bits, u32 limit_bits)
{
    double limit = (double)recovered_velocity_accumulate_358ac_float(limit_bits);
    double speed = (double)recovered_velocity_accumulate_358ac_float(speed_bits);
    double scaled;

    if (limit >= RECOVERED_VELOCITY_ACCUMULATE_358AC_LIMIT_70)
        return speed_bits;
    scaled = speed * (limit + RECOVERED_VELOCITY_ACCUMULATE_358AC_SCALE_OFFSET)
        / RECOVERED_VELOCITY_ACCUMULATE_358AC_SCALE_DIVISOR;
    return recovered_velocity_accumulate_358ac_bits((float)scaled);
}

/*
 * Pure operand computation for the primary exchange: the facing halfword is
 * zero-extended by ldos for the opcode-29 word and masked with 0xffff for the
 * opcode-30 word, so both carry the same low 16 bits.  The opcode-29 multiplier
 * is the notbit-31 speed and the opcode-30 multiplier is the raw speed, in that
 * order (0x35908/0x35914 then 0x35950/0x35958).
 */
void recovered_velocity_accumulate_358ac_operands(
    u32 facing_word, u32 speed_bits, u32 *angle_29, u32 *multiplier_29,
    u32 *angle_30, u32 *multiplier_30)
{
    u32 angle = facing_word & 0xffffU;

    if (angle_29 != (u32 *)0)
        *angle_29 = angle;
    if (multiplier_29 != (u32 *)0)
        *multiplier_29 = recovered_velocity_accumulate_358ac_flip31(speed_bits);
    if (angle_30 != (u32 *)0)
        *angle_30 = angle;
    if (multiplier_30 != (u32 *)0)
        *multiplier_30 = speed_bits;
}

/*
 * Pure accumulation.  Response 29 is the opcode-0x1d (sin) result and response
 * 30 the opcode-0x1e (cos) result; the listing adds the first to +0x1c8 (x)
 * at 0x35928/0x35b60/0x35c1c/0x35c88 and the second to +0x1cc (z) at
 * 0x35bd0/0x35ccc.
 */
void recovered_velocity_accumulate_358ac_apply(
    u32 x_bits, u32 z_bits, u32 response_29, u32 response_30,
    u32 *out_x, u32 *out_z)
{
    if (out_x != (u32 *)0)
        *out_x = recovered_velocity_accumulate_358ac_add_lane(x_bits, response_29);
    if (out_z != (u32 *)0)
        *out_z = recovered_velocity_accumulate_358ac_add_lane(z_bits, response_30);
}

/*
 * 0x51ab14 holds the pointer whose +0x670 and +0x678 words are the state-18
 * and state-11 multipliers.  The i960 address space is 32-bit; the
 * unsigned-long hop keeps the host and i960 builds warning-free.
 */
static u32 recovered_velocity_accumulate_358ac_table_word(u32 offset)
{
    u32 table = *(volatile u32 *)RECOVERED_VELOCITY_ACCUMULATE_358AC_TABLE_SLOT;

    return *(volatile u32 *)(unsigned long)(table + offset);
}

static u32 recovered_velocity_accumulate_358ac_exchange(u32 service, u32 angle,
                                                       u32 multiplier)
{
    volatile u32 *const fifo =
        (volatile u32 *)RECOVERED_VELOCITY_ACCUMULATE_358AC_FIFO;

    *fifo = service;
    *fifo = angle;
    *fifo = multiplier;
    return *fifo;
}

static void recovered_velocity_accumulate_358ac_load_pair(
    volatile unsigned char *object, u32 angle, u32 speed, u32 *z_addend)
{
    u32 response_29 = recovered_velocity_accumulate_358ac_exchange(
        RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_29, angle,
        recovered_velocity_accumulate_358ac_flip31(speed));

    *(volatile u32 *)(object + 0x1c8) = recovered_velocity_accumulate_358ac_add_lane(
        *(volatile u32 *)(object + 0x1c8), response_29);
    *z_addend = recovered_velocity_accumulate_358ac_exchange(
        RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_30, angle, speed);
}

/*
 * Runnable body.  The +0x30 == 3 early return and the +0x19c selector are the
 * only control entry points; everything else is the five accumulation shapes
 * described in the file comment.
 */
void recovered_velocity_accumulate_358ac_run(volatile unsigned char *object)
{
    u32 facing;
    u32 aux;
    u32 selector;
    u32 state;
    u32 speed;
    u32 limit;
    u32 angle;
    u32 z_addend;

    /* 0x358ac: the service-6 word is emitted before any object read. */
    *(volatile u32 *)RECOVERED_VELOCITY_ACCUMULATE_358AC_FIFO =
        RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_6;

    /* 0x358bc: +0x30 == 3 leaves through the 0x36458 ret. */
    if ((u32)*(volatile u16 *)(object + 0x30) == 3U)
        return;

    /* 0x358c0-0x358d0: halfword +0x2e = +0x184 + 2 * +0x186. */
    facing = (u32)*(volatile u16 *)(object + 0x184);
    aux = (u32)*(volatile u16 *)(object + 0x186);
    *(volatile u16 *)(object + 0x2e) = (u16)(facing + (aux << 1));

    selector = (u32)*(volatile u16 *)(object + 0x19c);
    if (selector != 0U) {
        /* 0x358dc-0x358f0: clamp the speed scalar to +0x7c. */
        limit = *(volatile u32 *)(object + 0x7c);
        speed = recovered_velocity_accumulate_358ac_clamp_speed(
            *(volatile u32 *)(object + 0x1c4), limit);
        *(volatile u32 *)(object + 0x1c4) = speed;

        /* 0x358f4-0x35968: facing against the sign-flipped speed. */
        angle = facing;
        recovered_velocity_accumulate_358ac_load_pair(object, angle, speed,
                                                      &z_addend);
    } else {
        state = (u32)*(volatile u16 *)(object + 0x172);
        if (state == 19U || state == 20U) {
            /* 0x3597c-0x359f0 */
            angle = (u32)*(volatile u16 *)(object + 0x3c);
            speed = *(volatile u32 *)(object + 0x1c4);
            recovered_velocity_accumulate_358ac_load_pair(object, angle, speed,
                                                          &z_addend);
        } else if (state == 31U || state == 34U) {
            /* 0x35a08-0x35a7c */
            angle = (u32)*(volatile u16 *)(object + 0x3c);
            speed = *(volatile u32 *)(object + 0x1c4);
            recovered_velocity_accumulate_358ac_load_pair(object, angle, speed,
                                                          &z_addend);
        } else {
            /* 0x35a80-0x35bc8: target-shaped pair against +0xf4/+0xf8. */
            u32 x_addend;
            u32 f4;
            u32 f8;
            u32 response_a;
            u32 response_b;

            limit = *(volatile u32 *)(object + 0x7c);
            speed = *(volatile u32 *)(object + 0x1c4);
            {
                u32 scaled = recovered_velocity_accumulate_358ac_scale_speed(
                    speed, limit);
                if (scaled != speed)
                    *(volatile u32 *)(object + 0x1c4) = scaled;
                speed = scaled;
            }
            angle = facing & 0xffffU;
            f4 = *(volatile u32 *)(object + 0xf4);
            f8 = *(volatile u32 *)(object + 0xf8);
            response_a = recovered_velocity_accumulate_358ac_exchange(
                RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_30, angle, f4);
            response_b = recovered_velocity_accumulate_358ac_exchange(
                RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_29, angle, f8);
            x_addend = recovered_velocity_accumulate_358ac_mul(
                recovered_velocity_accumulate_358ac_flip31(
                    recovered_velocity_accumulate_358ac_add_lane(response_a,
                                                                 response_b)),
                speed);
            *(volatile u32 *)(object + 0x1c8) =
                recovered_velocity_accumulate_358ac_add_lane(
                    *(volatile u32 *)(object + 0x1c8), x_addend);
            response_a = recovered_velocity_accumulate_358ac_exchange(
                RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_29, angle, f4);
            response_b = recovered_velocity_accumulate_358ac_exchange(
                RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_30, angle, f8);
            z_addend = recovered_velocity_accumulate_358ac_mul(
                recovered_velocity_accumulate_358ac_add_lane(
                    recovered_velocity_accumulate_358ac_flip31(response_a),
                    response_b),
                speed);
        }
    }

    /* 0x35bcc-0x35bd4: shared z tail. */
    *(volatile u32 *)(object + 0x1cc) =
        recovered_velocity_accumulate_358ac_add_lane(
            *(volatile u32 *)(object + 0x1cc), z_addend);

    /* 0x35bd8-0x35cd0: inline state-18/state-11 extension. */
    state = (u32)*(volatile u16 *)(object + 0x172);
    if (state == 18U) {
        u32 multiplier = recovered_velocity_accumulate_358ac_table_word(0x670U);
        angle = (u32)*(volatile u16 *)(object + 0x3c);
        recovered_velocity_accumulate_358ac_load_pair(object, angle, multiplier,
                                                      &z_addend);
    } else if (state == 11U
            && (u32)*(volatile u16 *)(object + 0x190) != 0U) {
        u32 multiplier = recovered_velocity_accumulate_358ac_table_word(0x678U);
        angle = (u32)*(volatile u16 *)(object + 0x3c);
        recovered_velocity_accumulate_358ac_load_pair(object, angle, multiplier,
                                                      &z_addend);
    } else {
        return;
    }

    *(volatile u32 *)(object + 0x1cc) =
        recovered_velocity_accumulate_358ac_add_lane(
            *(volatile u32 *)(object + 0x1cc), z_addend);
}
