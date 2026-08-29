/* Recovered constant selection from i960 routine 0x00028840. */

typedef unsigned long u32;
typedef unsigned char u8;

#define BACKUP_PROFILE ((volatile const u8 *)0x01d00027)
#define PROFILE_FIRST  ((volatile u32 *)0x00512bd4)
#define PROFILE_SECOND ((volatile u32 *)0x00512bd8)
#define PROFILE_THIRD  ((volatile u32 *)0x00512bdc)

struct geometry_profile_constants
{
    u32 first;
    u32 second;
    u32 third;
};

/* Values are preserved as raw IEEE-754 bits, matching lda/stores in the ROM. */
static const struct geometry_profile_constants profiles[9] = {
    { 0x3f000000U, 0x3f4ccccdU, 0x3e4ccccdU },
    { 0x3ee66666U, 0x3f400000U, 0x3e800000U },
    { 0x3ee66666U, 0x3f266666U, 0x3eb33333U },
    { 0x3eb33333U, 0x3f0ccccdU, 0x3ee66666U },
    { 0x3eb33333U, 0x3ee66666U, 0x3f0ccccdU },
    { 0x3f800000U, 0x3f59999aU, 0x00000000U },
    { 0x3f733333U, 0x3f59999aU, 0x00000000U },
    { 0x3f59999aU, 0x3f59999aU, 0x3d4ccccdU },
    { 0x3f400000U, 0x3f59999aU, 0x3dcccccdU },
};

/* Returns nonzero only for a direct table entry. */
int recovered_geometry_profile_constants(u8 backup_value,
                                          volatile u32 *first,
                                          volatile u32 *second,
                                          volatile u32 *third)
{
    u32 index;

    if (backup_value == 0)
        goto default_profile;
    index = (u32)backup_value - 1U;
    if (index >= 9)
    {
default_profile:
        *first = 0x3f0ccccdU;
        *second = 0x3f59999aU;
        *third = 0x3e19999aU;
        return 0;
    }
    *first = profiles[index].first;
    *second = profiles[index].second;
    *third = profiles[index].third;
    return 1;
}

/* First, directly observable part of the 0x28840 profile dispatch. */
void recovered_geometry_profile_setup(void)
{
    (void)recovered_geometry_profile_constants(*BACKUP_PROFILE,
                                                PROFILE_FIRST,
                                                PROFILE_SECOND,
                                                PROFILE_THIRD);
}
