/* Gameplay action -> host-to-SCSP command binding.
 *
 * The i960 gameplay handlers do not all use fixed sound IDs. A subset of the
 * per-frame action paths read the active fighter profile through the global
 * pointer at 0x51ab14 (set from object+0x6c) and forward one of its sound
 * fields to the host-to-SCSP producer at 0x2a4e0. This module records the
 * confirmed action/field pairs and the per-roster command values.
 *
 * Profile table:
 *   0x19360 holds ten profile pointers in roster order
 *   (0x57d0, 0xa5b0, 0xcdc0, 0x7be0, 0xeb90, 0x119e0,
 *    0x138d0, 0x15820, 0x16a10, 0x17b20). Each profile stores eight
 *   16-bit command IDs in +0x488..+0x4a6.
 *
 * Confirmed call sites (all `ld 0x51ab14` -> field -> `mov g4,g0` ->
 * `call 0x2a4e0`, with the object+0x68 selector choosing between the two
 * fields of a pair):
 *   - 0x34d9c/0x34dac (object+0x1ab weapon gate)   +0x48c / +0x488
 *   - 0x2fe6c/0x2fe74 (state 22, jump takeoff)     +0x494 / +0x490
 *   - 0x31060/0x31068 (state 35, air/hover loop)   +0x494 / +0x490
 *   - 0x3147c/0x31484 (state 37, air loop)         +0x494 / +0x490
 *   - 0x34300/0x34310 (locomotion enter)           +0x4a0 / +0x498
 *   - 0x34354/0x34364 (locomotion exit)            +0x4a4 / +0x49c
 *
 * The +0x488/0x48c pair is the per-roster primary weapon sound and the
 * +0x498/0x4a0 pair is the dash-loop sound; this is confirmed by the
 * recovered asset names (von/sound-id-names.json):
 *   profile 0: +0x488 SDE_tem_rifle,       +0x498 SDE_dash_01_loop
 *   profile 2: +0x488 SDE_rai_baz,         +0x498 SDE_rai_laser
 *   profile 4: +0x488 SDE_dor_phalanx_shoot
 *   profile 5: +0x488 SDE_fei_handbeam
 *   jump:      +0x490 SDE_jump_01/02/03 (SDE bank), +0x494 SDE_2_jump_01.. (SDE_2 bank)
 * The repeated +0x4a4/+0x49c reads in 0x4dc20..0x67c50 are the same
 * locomotion-exit/move-tail selection reached from the weapon/motion script
 * families; they share this binding and are not duplicated here.
 *
 * The 16-bit values are the host command words. The producer frames them as
 * 0xae, high byte, low byte, so the high byte is the 68000 sound-driver
 * family and the low byte is the per-roster entry. This module stops at the
 * host boundary; the asset-name mapping is a separate artifact.
 *
 * Values extracted from the original vonj maincpu image
 * (von/build/disasm/vonj-maincpu.bin) at profile+0x488..+0x4a4.
 */

typedef unsigned int u32;
typedef unsigned short u16;

enum {
    RECOVERED_AUDIO_CFG_WEAPON_A = 0x488,
    RECOVERED_AUDIO_CFG_WEAPON_B = 0x48c,
    RECOVERED_AUDIO_CFG_JUMP_A   = 0x490,
    RECOVERED_AUDIO_CFG_JUMP_B   = 0x494,
    RECOVERED_AUDIO_CFG_DASH_A   = 0x498,
    RECOVERED_AUDIO_CFG_DASH_B   = 0x4a0,
    RECOVERED_AUDIO_CFG_STOP_A   = 0x49c,
    RECOVERED_AUDIO_CFG_STOP_B   = 0x4a4
};

/* Field order matches RECOVERED_AUDIO_CFG_WEAPON_A..STOP_B. */
struct recovered_audio_profile_sounds {
    u16 weapon_a;
    u16 weapon_b;
    u16 jump_a;
    u16 jump_b;
    u16 dash_a;
    u16 stop_a;
    u16 dash_b;
    u16 stop_b;
};

static const struct recovered_audio_profile_sounds
recovered_audio_profiles[10] = {
    /* profile 0 @ 0x57d0 */ {0x1200U, 0x1228U, 0x1117U, 0x113bU, 0x1108U, 0x1123U, 0x112cU, 0x1147U},
    /* profile 1 @ 0xa5b0 */ {0x120aU, 0x1232U, 0x1118U, 0x113cU, 0x1108U, 0x1123U, 0x112cU, 0x1147U},
    /* profile 2 @ 0xcdc0 */ {0x120dU, 0x1235U, 0x1119U, 0x113dU, 0x1107U, 0x1122U, 0x112bU, 0x1146U},
    /* profile 3 @ 0x7be0 */ {0x1206U, 0x122eU, 0x1118U, 0x113cU, 0x1107U, 0x1122U, 0x112bU, 0x1146U},
    /* profile 4 @ 0xeb90 */ {0x1216U, 0x123eU, 0x1119U, 0x113dU, 0x1107U, 0x1122U, 0x112bU, 0x1146U},
    /* profile 5 @ 0x119e0 */ {0x121dU, 0x121dU, 0x1118U, 0x113cU, 0x1108U, 0x1123U, 0x112cU, 0x1147U},
    /* profile 6 @ 0x138d0 */ {0x1211U, 0x1239U, 0x1117U, 0x113bU, 0x1108U, 0x1123U, 0x112cU, 0x1147U},
    /* profile 7 @ 0x15820 */ {0x1218U, 0x1240U, 0x1119U, 0x113dU, 0x1107U, 0x1122U, 0x112bU, 0x1146U},
    /* profile 8 @ 0x16a10 */ {0x1220U, 0x1220U, 0x1119U, 0x113dU, 0x1107U, 0x1122U, 0x112bU, 0x1146U},
    /* profile 9 @ 0x17b20 */ {0x1200U, 0x1228U, 0x1119U, 0x113dU, 0x1107U, 0x1122U, 0x112bU, 0x1146U},
};

u32 recovered_audio_profile_count(void)
{
    return 10U;
}

u32 recovered_audio_profile_valid(u32 profile)
{
    return profile < 10U;
}

/* Original selector: object+0x68. Nonzero takes the "_b" field, which is
 * the SDE_2 bank variant of the same action. */
static u16 recovered_audio_select(u32 selector, u16 field_a, u16 field_b)
{
    return selector != 0U ? field_b : field_a;
}

/* field_code is one of RECOVERED_AUDIO_CFG_*; returns the selected command
 * word, or 0 when the profile or field code is out of range. A genuine
 * command word can itself be zero only for an unpopulated profile slot, so
 * callers that need a distinct error signal should use the _valid() test. */
u32 recovered_audio_profile_sound(u32 profile, u32 field_code, u32 selector,
                                  u16 *command)
{
    const struct recovered_audio_profile_sounds *sounds;

    if (!recovered_audio_profile_valid(profile) || command == (void *)0)
        return 0U;
    if ((field_code & 1U) != 0U)
        return 0U;
    sounds = &recovered_audio_profiles[profile];
    switch (field_code) {
    case RECOVERED_AUDIO_CFG_WEAPON_A:
        *command = recovered_audio_select(selector, sounds->weapon_a,
                                          sounds->weapon_b);
        return 1U;
    case RECOVERED_AUDIO_CFG_JUMP_A:
        *command = recovered_audio_select(selector, sounds->jump_a,
                                          sounds->jump_b);
        return 1U;
    case RECOVERED_AUDIO_CFG_DASH_A:
        *command = recovered_audio_select(selector, sounds->dash_a,
                                          sounds->dash_b);
        return 1U;
    case RECOVERED_AUDIO_CFG_STOP_A:
        *command = recovered_audio_select(selector, sounds->stop_a,
                                          sounds->stop_b);
        return 1U;
    default:
        return 0U;
    }
}

/* Confirmed action wrappers. The selector is object+0x68 at every site. */
u32 recovered_audio_jump_command(u32 profile, u32 selector, u16 *command)
{
    return recovered_audio_profile_sound(profile, RECOVERED_AUDIO_CFG_JUMP_A,
                                         selector, command);
}

u32 recovered_audio_dash_command(u32 profile, u32 selector, u16 *command)
{
    return recovered_audio_profile_sound(profile, RECOVERED_AUDIO_CFG_DASH_A,
                                         selector, command);
}

u32 recovered_audio_move_exit_command(u32 profile, u32 selector,
                                      u16 *command)
{
    return recovered_audio_profile_sound(profile, RECOVERED_AUDIO_CFG_STOP_A,
                                         selector, command);
}

u32 recovered_audio_weapon_command(u32 profile, u32 selector, u16 *command)
{
    return recovered_audio_profile_sound(profile, RECOVERED_AUDIO_CFG_WEAPON_A,
                                         selector, command);
}
