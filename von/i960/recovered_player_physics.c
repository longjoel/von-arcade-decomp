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
