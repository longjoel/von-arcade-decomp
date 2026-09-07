/* Recovered player-VR vertical physics and walk cap, in milli-units.
 *
 * Fitted from jump arcs in the full-bout position tap
 * (von/build/audio-queue/manual-02/input-audio.log, VON_IH_POS=1).
 * Two clean player jumps (f=3956-4073, f=4553-4670) fit
 * y = -0.015 t^2 + 1.755 t + 1.770 with max residual 0.000, giving
 * gravity 0.030/frame^2 and takeoff velocity 1.755 (first-frame delta
 * reads 1.77; the fit value reflects gravity applied before integrate).
 * Apex 53.1 and 119-frame flight follow: 1.770 + 1.755^2/0.06 = 53.07.
 * A third jump holds apex 53.1 for ~50 frames (hover state, f=1647-1697),
 * so constant velocity applies only outside hover.
 *
 * Horizontal speed caps at 3.50 u/f ground and air (113-frame sustained
 * segments at exactly 3.50); cruise walks sit near 2.9 (analog partial
 * deflection). No burst above 3.50 other than teleports appears in this
 * bout, so dash speed is not recovered here. CPU arcs are slower
 * (rise ~0.48, fall ~0.38) with no clean ballistic jump; CPU constants
 * remain open, as does the hover trigger.
 *
 * Stage-5 bout extension (von/build/stage5-fleet/stage-trace.log, fresh
 * NVRAM replay of von/captures/vonj-20260907T211227Z/inp/stage3-fleet,
 * frames 4430-29248):
 * - Ground dash: left dash trigger (IN1 bit 0x02) + L-stick direction
 *   cruises 4.20 u/f (290 units over frames 18041-18109, peak 4.52;
 *   second episode 263 units over 68 frames, peak 4.20). Dash length is
 *   ~69 frames; the trigger may release mid-dash without ending it.
 * - CPU dashes in the same band, peaking 4.62-4.70 u/f (6-frame
 *   episodes); one 7-frame 5.00 u/f burst pairs stick with shot.
 * - Knockback launches cost health and stay airborne exactly 30 frames
 *   (11 of 11 damage-linked liftoffs); planar peaks reach ~49 u/f.
 * - Hover floats at 18/22/24/38 units for 100-745 frames; an in-air
 *   re-jump leaves with the full ground takeoff impulse (+16 units per
 *   12 frames, same as liftoff). Tap hops last 28 frames peaking 6.0.
 * - Round-start posts are (0,0,-60) player / (0,0,+60) CPU; arena
 *   floor sits at y ~= 0.0 on every stage; stages are single-round.
 * - The jump button is still open: the input map exposes no jump
 *   field, and single-stick flicks (L-only 4%, R-only 7%, R+L 12%)
 *   do not reliably lift. Every ascent follows an L-stick flick
 *   (15 of 16, mostly IN1 0x80) plus an R-stick flick 2-9 frames
 *   before liftoff, but the causal edge is unconfirmed.
 */

typedef unsigned int u32;

u32 recovered_player_gravity_milli(void)
{
    return 30U;
}

u32 recovered_player_jump_vy_milli(void)
{
    return 1755U;
}

u32 recovered_player_walk_cap_milli(void)
{
    return 3500U;
}

u32 recovered_player_dash_cruise_milli(void)
{
    return 4200U;
}

u32 recovered_player_dash_length_frames(void)
{
    return 69U;
}

u32 recovered_cpu_dash_peak_milli(void)
{
    return 4700U;
}

u32 recovered_launch_airtime_frames(void)
{
    return 30U;
}

u32 recovered_round_post_z(void)
{
    return 60U;
}
