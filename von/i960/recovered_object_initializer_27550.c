/* Bounded object initializer recovered from i960 0x27550-0x27c50.
 *
 * Reproduces the identity/state/position seed writes the 0x32810 update
 * backbone and velocity integrator consume.  The profile-route switch
 * (0x275d4-0x27668), the per-kind callback pointer table, the transform
 * producer call (0x75d90), the stage selector call (0x6f600), the geometry
 * projection helper (0x6f600/0x75d90 family) and the 0x503xxx shadow
 * publication block remain outside this bounded model; the callback value is
 * supplied by the caller and stored verbatim.
 *
 * Field widths and constants were read back from the listing:
 *   0x2755c stos g14,(g0)           +0x00 = 0
 *   0x27564 stos g13,0x2(g0)        +0x02 = 1
 *   0x27558 st   g6,0x6c(g0)        +0x6c = config
 *   0x27568 st   g1,0x74(g0)        +0x74 = related
 *   0x2756c st   g3,0x64(g0)        +0x64 = kind
 *   0x27570 st   g5,0x68(g0)        +0x68 = team
 *   0x27574 stos g14,0x172(g0)      +0x172 = 0 (state)
 *   0x27578 stos g13,0x170(g0)      +0x170 = 1 (sub-phase)
 *   0x27670 st   r7,0x8(r4)         +0x08 = x
 *   0x27674 st   g8,0x10(r4)        +0x10 = z
 *   0x277ec stos g9,0x184(r4)       +0x184 = facing
 *   0x278b0 stos g13,0x1fc(r4)      +0x1fc = 0xff (g13 = 0xff from 0x278ac)
 *   0x2787c-0x27888 stos g4,0x1e{8,6,4,2}  +0x1e2..+0x1e8 = 0x64
 *   0x2788c-0x27898 stos g14,0x1f{0,e,c,a} +0x1ea..+0x1f0 = 0
 *   0x278a4/0x278a8 stos r6,0x1f{8,a}      +0x1f8/+0x1fa = 0xffff (r6 = -1)
 */

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

void recovered_object_initializer_27550_run(volatile unsigned char *object,
    unsigned int config_pointer, unsigned int callback_pointer,
    unsigned int related_pointer, unsigned int kind, unsigned int team,
    unsigned int x, unsigned int z, unsigned int facing)
{
    /* Identity / owner pointers (32-bit). */
    *(volatile u32 *)(object + 0x04) = callback_pointer; /* 0x27600 st g13,0x4(g0) */
    *(volatile u32 *)(object + 0x64) = kind;             /* 0x2756c st g3,0x64(g0) */
    *(volatile u32 *)(object + 0x68) = team;             /* 0x27570 st g5,0x68(g0) */
    *(volatile u32 *)(object + 0x6c) = config_pointer;   /* 0x27558 st g6,0x6c(g0) */
    *(volatile u32 *)(object + 0x74) = related_pointer;  /* 0x27568 st g1,0x74(g0) */

    /* Record header, state and sub-phase. */
    *(volatile u16 *)(object + 0x00) = 0U;               /* 0x2755c stos g14,(g0) */
    *(volatile u16 *)(object + 0x02) = 1U;               /* 0x27564 stos g13,0x2(g0) */
    *(volatile u16 *)(object + 0x170) = 1U;              /* 0x27578 stos g13,0x170(g0) */
    *(volatile u16 *)(object + 0x172) = 0U;              /* 0x27574 stos g14,0x172(g0) */

    /* Position seed (32-bit) and facing. */
    *(volatile u32 *)(object + 0x08) = x;                /* 0x27670 st r7,0x8(r4) */
    *(volatile u32 *)(object + 0x10) = z;                /* 0x27674 st g8,0x10(r4) */
    *(volatile u16 *)(object + 0x184) = (u16)facing;     /* 0x277ec stos g9,0x184(r4) */

    /* Reset halfword scratch fields. */
    *(volatile u16 *)(object + 0x174) = 0U;              /* 0x2758c stos g14,0x174(g0) */
    *(volatile u16 *)(object + 0x176) = 0U;              /* 0x2759c stos g14,0x176(g0) */
    *(volatile u16 *)(object + 0x178) = 0U;              /* 0x275a8 stos g14,0x178(g0) */
    *(volatile u16 *)(object + 0x17a) = 0U;              /* 0x275b4 stos g14,0x17a(g0) */
    *(volatile u16 *)(object + 0x17c) = 0U;              /* 0x275c0 stos g14,0x17c(g0) */
    *(volatile u16 *)(object + 0x17e) = 0U;              /* 0x275cc stos g14,0x17e(g0) */

    *(volatile u16 *)(object + 0x2c) = 0U;               /* 0x2768c stos g14,0x2c(r4) */
    *(volatile u16 *)(object + 0x2e) = 0U;               /* 0x27688 stos g14,0x2e(r4) */
    *(volatile u16 *)(object + 0x32) = 0U;               /* 0x27698 stos g14,0x32(r4) */
    *(volatile u16 *)(object + 0x34) = 0U;               /* 0x27694 stos g14,0x34(r4) */
    *(volatile u16 *)(object + 0x36) = 0U;               /* 0x27690 stos g14,0x36(r4) */
    *(volatile u16 *)(object + 0x38) = 0U;               /* 0x276a0 stos g14,0x38(r4) */
    *(volatile u16 *)(object + 0x3a) = 0U;               /* 0x2769c stos g14,0x3a(r4) */

    /* Sentinel halfword; g13 = subo 1,0 = 0xffffffff. */
    *(volatile u16 *)(object + 0x46) = 0xffffU;          /* 0x276c4 stos g13,0x46(r4) */

    /* Velocity accumulators begin at rest. */
    *(volatile u32 *)(object + 0x1c8) = 0U;              /* 0x276d4 st g4,0x1c8(r4) */
    *(volatile u32 *)(object + 0x1cc) = 0U;              /* 0x276d0 st g4,0x1cc(r4) */

    /* Action/state seed bytes and halfword. */
    *(volatile u8 *)(object + 0x1ab) = 0U;               /* 0x2781c stob g14,0x1ab(r4) */
    *(volatile u8 *)(object + 0x1ac) = 0U;               /* 0x27818 stob g14,0x1ac(r4) */
    *(volatile u8 *)(object + 0x1ad) = 0U;               /* 0x27814 stob g14,0x1ad(r4) */
    *(volatile u8 *)(object + 0x1b0) = 0U;               /* 0x27854 stob g14,0x1b0(r4) */
    *(volatile u8 *)(object + 0x1b1) = 0U;               /* 0x27850 stob g14,0x1b1(r4) */
    *(volatile u16 *)(object + 0x1b2) = 0U;              /* 0x2784c stos g14,0x1b2(r4) */

    /* Timer/limit halfwords: 0x64 packed limits then zero tail. */
    *(volatile u16 *)(object + 0x1e2) = 0x64U;           /* 0x27888 stos g4,0x1e2(r4) */
    *(volatile u16 *)(object + 0x1e4) = 0x64U;           /* 0x27884 stos g4,0x1e4(r4) */
    *(volatile u16 *)(object + 0x1e6) = 0x64U;           /* 0x27880 stos g4,0x1e6(r4) */
    *(volatile u16 *)(object + 0x1e8) = 0x64U;           /* 0x2787c stos g4,0x1e8(r4) */
    *(volatile u16 *)(object + 0x1ea) = 0U;              /* 0x27898 stos g14,0x1ea(r4) */
    *(volatile u16 *)(object + 0x1ec) = 0U;              /* 0x27894 stos g14,0x1ec(r4) */
    *(volatile u16 *)(object + 0x1ee) = 0U;              /* 0x27890 stos g14,0x1ee(r4) */
    *(volatile u16 *)(object + 0x1f0) = 0U;              /* 0x2788c stos g14,0x1f0(r4) */

    /* Signed sentinels (r6 = subo 1,0 = 0xffffffff) and mode byte 0xff. */
    *(volatile u16 *)(object + 0x1f8) = 0xffffU;         /* 0x278a8 stos r6,0x1f8(r4) */
    *(volatile u16 *)(object + 0x1fa) = 0xffffU;         /* 0x278a4 stos r6,0x1fa(r4) */
    *(volatile u16 *)(object + 0x1fc) = 0xffU;           /* 0x278b0 stos g13,0x1fc(r4) */
}
