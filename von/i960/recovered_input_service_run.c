/* Freestanding Model 2 Sega 315-5649 input service for the i960 main CPU.
 *
 * Purpose
 * -------
 * The reconstructed i960 player object keeps its committed command in the
 * halfword at object+0x108, and the input-commit unit at 0x72ea0 consumes the
 * two byte words at 0x504dac (MA) and 0x504db0 (MB). On the real board those
 * bytes are latched from the Sega 315-5649 I/O controller. The sibling
 * per-object update at 0x25040 copies the packed controller words
 * 0x50249c -> object+0xec and 0x5024a4 -> object+0xf0 (0x2504c-0x2506c),
 * snapshots the old command into object+0x106 (0x25070-0x25080), and then
 * decodes object+0x108 from object+0xec through the two nibble tables at
 * 0x3d70/0x3da0 (0x250f4-0x2515c).
 *
 * This unit reads the two twin-stick ports directly, derives the MA/MB bytes
 * with the twin-stick sum/difference mapping, and reproduces the exact nibble
 * lookup so object+0x108 matches what the sibling decoder would produce from
 * the same sticks. It never calls the input-commit unit; the caller drives
 * 0x72ea0 itself.
 *
 * Port layout (mame/src/mame/sega/model2.cpp)
 * -------------------------------------------
 * model2a() maps the 315-5649 at 0x01c00000..0x01c0001f and wires its port
 * callbacks to the von ioports:
 *   io.in_pb_callback  -> IN0  (register 0x01)
 *   io.in_pc_callback  -> IN1  (register 0x02)  P1 left stick + buttons
 *   io.in_pd_callback  -> IN2  (register 0x03)  P1 right stick + buttons
 *   io.in_pg_callback  -> SW   (register 0x06)
 * INPUT_PORTS_START(von) gives IN1 and IN2 the same bit order, all
 * IP_ACTIVE_LOW (a pressed direction or button reads 0 on the bus):
 *   0x01 shot, 0x02 dash, 0x10 down, 0x20 up, 0x40 right, 0x80 left.
 *
 * Twin-stick derivation (von/i960/recovered-twin-stick-map.md)
 * ------------------------------------------------------------
 * Translation is the sum of the two sticks and twist is their difference;
 * pushing the sticks together is guard and pulling them apart is jump. MA
 * (0x504dac) is the packed translation byte and MB (0x504db0) is the packed
 * twist byte, both in the same 0x10/0x20/0x40/0x80 direction order. The
 * input-commit counters test MA/MB bits 0x02 (dash), 0x10 (down), 0x20 (up),
 * which line up with this layout.
 *
 * Integer-only, no libc, no soft-float.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed int s32;

/* 315-5649 register window and the two twin-stick register offsets. */
#define RECOVERED_INPUT_SERVICE_IO_WINDOW 0x01c00000UL
#define RECOVERED_INPUT_SERVICE_REG_IN1   0x04U
#define RECOVERED_INPUT_SERVICE_REG_IN2   0x06U

/* Shared IN1/IN2 bit order (INPUT_PORTS_START(von), model2.cpp:2170-2186). */
#define RECOVERED_INPUT_SERVICE_BIT_SHOT  0x01U
#define RECOVERED_INPUT_SERVICE_BIT_DASH  0x02U
#define RECOVERED_INPUT_SERVICE_BIT_DOWN  0x10U
#define RECOVERED_INPUT_SERVICE_BIT_UP    0x20U
#define RECOVERED_INPUT_SERVICE_BIT_RIGHT 0x40U
#define RECOVERED_INPUT_SERVICE_BIT_LEFT  0x80U

/* object+0x108 command halfword, object+0xec/object+0xf0 sibling copies. */
#define RECOVERED_INPUT_SERVICE_OBJ_COMMAND 0x108U
#define RECOVERED_INPUT_SERVICE_OBJ_STATUS  0xecU
#define RECOVERED_INPUT_SERVICE_OBJ_WORK    0xf0U

/* Input-commit MA/MB cells (0x72ea0 prelude, 0x72ec0-0x72f00). */
#define RECOVERED_INPUT_SERVICE_MA_WORD 0x00504dacUL
#define RECOVERED_INPUT_SERVICE_MB_WORD 0x00504db0UL

/* Sibling nibble tables, i960 0x3d70 and 0x3da0 (identical contents). The
 * little-endian ROM bytes are
 *   ff00 0400 0000 ff00 0600 0500 0700 ff00
 *   0200 0300 0100 ff00 ff00 ff00 ff00 ff00
 * so each table holds
 *   {0xff,4,0,0xff,6,5,7,0xff,2,3,1,0xff,0xff,0xff,0xff,0xff}.
 * The sibling takes the high direction nibble of the copied controller word
 * (bits 12-15 via shift 0x3d90=12, bits 20-23 via shift 0x3dc0=20) and looks
 * it up. 1=down->4, 2=up->0, 4=right->6, 5=down+right->5, 6=up+right->7,
 * 8=left->2, 9=down+left->3, 10=up+left->1; every other nibble (including
 * neutral) selects the 0xff no-command lane. */
static const u16 recovered_input_service_nibble_table[16] = {
    0x00ffU, 0x0004U, 0x0000U, 0x00ffU,
    0x0006U, 0x0005U, 0x0007U, 0x00ffU,
    0x0002U, 0x0003U, 0x0001U, 0x00ffU,
    0x00ffU, 0x00ffU, 0x00ffU, 0x00ffU
};

struct recovered_input_service_derived {
    u32 command_code;   /* object+0x108 halfword value */
    u32 ma;             /* 0x504dac byte lane, 0..0xff */
    u32 mb;             /* 0x504db0 byte lane, 0..0xff */
};

/* -1/0/+1 axis from one active-low port byte. */
static int recovered_input_service_axis(u32 logical_byte, u32 positive,
                                        u32 negative)
{
    return ((logical_byte & positive) != 0U ? 1 : 0)
         - ((logical_byte & negative) != 0U ? 1 : 0);
}

/* Pure IN1/IN2 -> (command code, MA, MB) derivation. */
void recovered_input_service_derive(
    unsigned int in1, unsigned int in2,
    struct recovered_input_service_derived *out)
{
    u32 left = (~(u32)in1) & 0xffU;
    u32 right = (~(u32)in2) & 0xffU;
    u32 buttons = (left | right) & (RECOVERED_INPUT_SERVICE_BIT_SHOT |
                                    RECOVERED_INPUT_SERVICE_BIT_DASH);
    int lz = recovered_input_service_axis(
        left, RECOVERED_INPUT_SERVICE_BIT_UP,
        RECOVERED_INPUT_SERVICE_BIT_DOWN);
    int lx = recovered_input_service_axis(
        left, RECOVERED_INPUT_SERVICE_BIT_RIGHT,
        RECOVERED_INPUT_SERVICE_BIT_LEFT);
    int rz = recovered_input_service_axis(
        right, RECOVERED_INPUT_SERVICE_BIT_UP,
        RECOVERED_INPUT_SERVICE_BIT_DOWN);
    int rx = recovered_input_service_axis(
        right, RECOVERED_INPUT_SERVICE_BIT_RIGHT,
        RECOVERED_INPUT_SERVICE_BIT_LEFT);
    int sum_z = lz + rz;
    int sum_x = lx + rx;
    int diff_z = lz - rz;
    int diff_x = lx - rx;
    u32 ma = buttons;
    u32 mb = buttons;
    u32 hi;
    u32 lo;

    /* MA: translation is the sum of the sticks. */
    if (sum_z > 0)
        ma |= RECOVERED_INPUT_SERVICE_BIT_UP;
    else if (sum_z < 0)
        ma |= RECOVERED_INPUT_SERVICE_BIT_DOWN;
    if (sum_x > 0)
        ma |= RECOVERED_INPUT_SERVICE_BIT_RIGHT;
    else if (sum_x < 0)
        ma |= RECOVERED_INPUT_SERVICE_BIT_LEFT;

    /* MB: twist is the difference. diff_x > 0 is left stick right with the
     * right stick left (together -> guard); diff_x < 0 is the opposite
     * (apart -> jump). */
    if (diff_z > 0)
        mb |= RECOVERED_INPUT_SERVICE_BIT_UP;
    else if (diff_z < 0)
        mb |= RECOVERED_INPUT_SERVICE_BIT_DOWN;
    if (diff_x > 0)
        mb |= RECOVERED_INPUT_SERVICE_BIT_RIGHT;
    else if (diff_x < 0)
        mb |= RECOVERED_INPUT_SERVICE_BIT_LEFT;

    /* Sibling 0x250f4-0x2515c: table[MA high nibble] << 8 | table[MB high
     * nibble], stored to object+0x108 with `stos`. */
    hi = (u32)recovered_input_service_nibble_table[(ma >> 4) & 0x0fU];
    lo = (u32)recovered_input_service_nibble_table[(mb >> 4) & 0x0fU];
    out->command_code = ((hi << 8) | lo) & 0xffffU;
    out->ma = ma & 0xffU;
    out->mb = mb & 0xffU;
}

/* Pure body of the service: derive, publish the sibling copies, publish the
 * command halfword, and publish the input-commit MA/MB cells. */
void recovered_input_service_run_core(
    volatile unsigned char *object,
    unsigned int in1, unsigned int in2,
    volatile unsigned int *ma_word, volatile unsigned int *mb_word)
{
    struct recovered_input_service_derived derived;
    u32 source;

    recovered_input_service_derive(in1, in2, &derived);

    /* object+0xec gets the sibling decoder source: MA high nibble at bits
     * 12-15 and MB high nibble at bits 20-23, so re-running 0x250f4-0x2515c on
     * object+0xec reproduces object+0x108. object+0xf0 mirrors the 0x5024a4 ->
     * object+0xf0 copy at 0x2505c-0x2506c. */
    source = ((derived.mb & 0xf0U) << 16) | ((derived.ma & 0xf0U) << 8);
    *(volatile u32 *)(object + RECOVERED_INPUT_SERVICE_OBJ_STATUS) = source;
    *(volatile u32 *)(object + RECOVERED_INPUT_SERVICE_OBJ_WORK) = derived.mb;

    /* 0x2515c `stos g5,0x108(g0)`. */
    *(volatile u16 *)(object + RECOVERED_INPUT_SERVICE_OBJ_COMMAND) =
        (u16)derived.command_code;

    /* The input-commit prelude sign-extends record bytes with `shlo 24` /
     * `shri 24` (0x72ee0-0x72f00); mirror that contract. */
    *ma_word = (u32)(s32)(s8)(derived.ma & 0xffU);
    *mb_word = (u32)(s32)(s8)(derived.mb & 0xffU);
}

/* Thin mapped wrapper around the 0x01c00002/0x01c00003 controller bytes. Not
 * host-testable: the absolute read is isolated here so the pure derivation
 * above can be exercised on the host. */
unsigned int recovered_input_service_read_ports(void)
{
    volatile unsigned char *io =
        (volatile unsigned char *)(unsigned long)RECOVERED_INPUT_SERVICE_IO_WINDOW;
    /* The 315-5649 port bytes appear as 16-bit reads with the value in the low
     * lane (the io window uses umask32 0x00ff00ff), so read the halfwords. */
    unsigned int in1 = (unsigned int)(*(volatile unsigned short *)
        (io + RECOVERED_INPUT_SERVICE_REG_IN1)) & 0xffU;
    unsigned int in2 = (unsigned int)(*(volatile unsigned short *)
        (io + RECOVERED_INPUT_SERVICE_REG_IN2)) & 0xffU;

    return (in1 & 0xffU) | ((in2 & 0xffU) << 8);
}

/* Original absolute-global entry. Reads the 315-5649 and commits object+0x108
 * plus 0x504dac/0x504db0. Leaves the 0x72ea0 input-commit call to the caller. */
void recovered_input_service_run(volatile unsigned char *object)
{
    unsigned int ports = recovered_input_service_read_ports();

    recovered_input_service_run_core(
        object, ports & 0xffU, (ports >> 8) & 0xffU,
        (volatile unsigned int *)(unsigned long)RECOVERED_INPUT_SERVICE_MA_WORD,
        (volatile unsigned int *)(unsigned long)RECOVERED_INPUT_SERVICE_MB_WORD);
}
