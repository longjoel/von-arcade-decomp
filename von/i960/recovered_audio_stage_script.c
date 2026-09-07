/* Recovered per-stage intro audio scripts for the host-to-SCSP ring.
 *
 * Observed with a write tap over 0x0051aa70-0x0051aabf during a full-bout
 * playback (von/build/audio-queue/manual-02/input-audio.log): every stage
 * opens with an ordered packet script in the ~130 frames before the spawn
 * teleport, ending one frame before spawn with the FIGHT call. Packets are
 * datum triples as emitted (see von/tools/extract_audio_stage_script.py
 * for the grouping rules); the S3 FIGHT tick emits a bare 0x52U plus a
 * trailing [ae, 13] rather than one triple.
 *
 * Shared core across stages 1-3: AE 00 02 near offset -120, AE 13 3F near
 * -110, AE 13 41 near -72, AE 11 11 twice near -53/-32. Per-stage IDs
 * ascend with the stage: BGM triple AE 13 (0x4a + stage) near -63 and
 * FIGHT ID byte (0x4f + stage) on the final tick.
 */

typedef unsigned int u32;
typedef signed int s32;
typedef unsigned char u8;

#define RECOVERED_AUDIO_SCRIPT_MAX_BYTES 3u

typedef struct {
    s32 frame_offset;
    u8 length;
    u8 bytes[RECOVERED_AUDIO_SCRIPT_MAX_BYTES];
} recovered_audio_script_step;

typedef struct {
    u32 count;
    recovered_audio_script_step steps[11];
} recovered_audio_stage_script;

static const recovered_audio_stage_script recovered_audio_stage_scripts[3] = {
    {7, {
        {-121, 3, {0xaeU, 0x00U, 0x02U}},
        {-111, 3, {0xaeU, 0x13U, 0x3fU}},
        {-73, 3, {0xaeU, 0x13U, 0x41U}},
        {-64, 3, {0xaeU, 0x13U, 0x4bU}},
        {-54, 3, {0xaeU, 0x11U, 0x11U}},
        {-33, 3, {0xaeU, 0x11U, 0x11U}},
        {-1, 3, {0xaeU, 0x13U, 0x50U}},
    }},
    {11, {
        {-128, 3, {0xaeU, 0x11U, 0x15U}},
        {-120, 3, {0xaeU, 0x11U, 0x15U}},
        {-120, 3, {0xaeU, 0x00U, 0x03U}},
        {-120, 3, {0xaeU, 0x00U, 0x03U}},
        {-119, 3, {0xaeU, 0x00U, 0x02U}},
        {-109, 3, {0xaeU, 0x13U, 0x3fU}},
        {-71, 3, {0xaeU, 0x13U, 0x41U}},
        {-62, 3, {0xaeU, 0x13U, 0x4cU}},
        {-52, 3, {0xaeU, 0x11U, 0x11U}},
        {-31, 3, {0xaeU, 0x11U, 0x11U}},
        {-1, 3, {0xaeU, 0x13U, 0x51U}},
    }},
    {11, {
        {-128, 3, {0xaeU, 0x11U, 0x15U}},
        {-121, 3, {0xaeU, 0x00U, 0x03U}},
        {-121, 3, {0xaeU, 0x00U, 0x03U}},
        {-120, 3, {0xaeU, 0x00U, 0x02U}},
        {-110, 3, {0xaeU, 0x13U, 0x3fU}},
        {-72, 3, {0xaeU, 0x13U, 0x41U}},
        {-63, 3, {0xaeU, 0x13U, 0x4dU}},
        {-53, 3, {0xaeU, 0x11U, 0x11U}},
        {-32, 3, {0xaeU, 0x11U, 0x11U}},
        {-1, 1, {0x52U, 0x00U, 0x00U}},
        {-1, 2, {0xaeU, 0x13U, 0x00U}},
    }},
};

u32 recovered_audio_stage_script_step_count(u32 stage)
{
    if (stage < 1U || stage > 3U)
        return 0U;
    return recovered_audio_stage_scripts[stage - 1U].count;
}

u32 recovered_audio_stage_script_step(u32 stage, u32 index,
                                      recovered_audio_script_step *out)
{
    const recovered_audio_stage_script *script;
    u32 i;
    if (stage < 1U || stage > 3U)
        return 0U;
    script = &recovered_audio_stage_scripts[stage - 1U];
    if (index >= script->count)
        return 0U;
    out->frame_offset = script->steps[index].frame_offset;
    out->length = script->steps[index].length;
    for (i = 0U; i < RECOVERED_AUDIO_SCRIPT_MAX_BYTES; i++)
        out->bytes[i] = script->steps[index].bytes[i];
    return 1U;
}
