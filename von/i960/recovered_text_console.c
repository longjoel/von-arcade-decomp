/* Bounded freestanding recovery of the i960 hardware text console used by the
 * attract/UI modes: the reset at 0x1c618, the emit primitive at 0x1ccf8, the
 * cursor setter at 0x1cac8, the control-code handler at 0x1cbb8 and the putc /
 * puts entry points at 0x1cc40 / 0x1ccd0.
 *
 * Listing map:
 *
 *   0x1c618-0x1c6f0  reset: clears 0x504d24..0x504d38 and the nametable
 *                    buffers 0x1000000 (0x4000 hw), 0x1008000 (0x800 hw),
 *                    0x100c000 (0x1000 hw), 0x100a000 (8 hw)
 *   0x1ccf8          st g0,0x1800000        emit glyph / command register
 *   0x1cac8          st a,0x504cdc ; st a,0x504ce0 ; st b,0x504ce4
 *   0x1cbb8          control: cmd 9 = tab (cursor to next multiple of 8),
 *                    cmd 10 = line feed (cursor <- 0x504cdc, row++)
 *   0x1cc40          putc: ch <= 31 -> control; else write the nametable cell
 *   0x1ccd0          puts: putc until the NUL terminator
 *
 * State cells: 0x504cdc saved cursor, 0x504ce0 cursor column (nametable index
 * low), 0x504ce4 row (index high, scaled by 64), 0x504cf4 glyph attribute OR.
 * The pure core keeps that state in a struct so the host build never touches a
 * target address; the _run wrappers own the absolute cells, the 0x1000000
 * nametable and the 0x1800000 command register.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

#define RECOVERED_TEXT_CELL_SAVED 0x00504cdcU
#define RECOVERED_TEXT_CELL_COLUMN 0x00504ce0U
#define RECOVERED_TEXT_CELL_ROW 0x00504ce4U
#define RECOVERED_TEXT_CELL_ATTR 0x00504cf4U

#define RECOVERED_TEXT_NAMETABLE 0x01000000U
#define RECOVERED_TEXT_COMMAND 0x01800000U

#define RECOVERED_TEXT_NAMETABLE_WORDS 0x4000U
#define RECOVERED_TEXT_EXTRA_A 0x0100c000U
#define RECOVERED_TEXT_EXTRA_A_WORDS 0x1000U
#define RECOVERED_TEXT_EXTRA_B 0x01008000U
#define RECOVERED_TEXT_EXTRA_B_WORDS 0x800U
#define RECOVERED_TEXT_EXTRA_C 0x0100a000U
#define RECOVERED_TEXT_EXTRA_C_WORDS 0x8U

struct recovered_text_console {
    u32 saved;    /* 0x504cdc */
    u32 column;   /* 0x504ce0 */
    u32 row;      /* 0x504ce4 */
    u32 attr;     /* 0x504cf4 */
};

void recovered_text_console_reset_core(struct recovered_text_console *console)
{
    console->saved = 0U;
    console->column = 0U;
    console->row = 0U;
    console->attr = 0U;
}

void recovered_text_console_set_cursor_core(
    struct recovered_text_console *console, u32 a, u32 b)
{
    /* 0x1cac8: 0x504cdc = 0x504ce0 = a ; 0x504ce4 = b. */
    console->saved = a;
    console->column = a;
    console->row = b;
}

/* 0x1cbb8: cmd 9 = tab, cmd 10 = line feed. */
static void recovered_text_console_control_core(
    struct recovered_text_console *console, u32 command)
{
    u32 cmd = command & 0xffU;

    if (cmd == 9U) {
        u32 pos = (console->column + 8U) & ~7U;

        console->column = pos;
        if (pos > 61U) {
            console->column = 0U;
            if (console->row <= 46U)
                console->row += 1U;
        }
    } else if (cmd == 10U) {
        console->column = console->saved;
        if (console->row <= 46U)
            console->row += 1U;
    }
}

/* 0x1cc40: returns 1 when a nametable cell was produced. */
u32 recovered_text_console_putc_core(
    struct recovered_text_console *console, u32 ch,
    u32 *out_index, u32 *out_value)
{
    u32 character = ch & 0xffU;

    if (character <= 31U) {
        recovered_text_console_control_core(console, character);
        return 0U;
    }

    /* 0x1cc68-0x1ccb8: idx = (row << 6) + column, value = ch | attr | 0x8000. */
    if (out_index != (void *)0)
        *out_index = (console->row << 6) + console->column;
    if (out_value != (void *)0)
        *out_value = character | console->attr | 0xffff8000U;

    if (console->column <= 61U)
        console->column += 1U;
    return 1U;
}

/* 0x1ccd0: putc every byte until the NUL terminator. */
u32 recovered_text_console_puts_core(
    struct recovered_text_console *console, const volatile unsigned char *text,
    u32 *out_last_index, u32 *out_last_value)
{
    u32 index = 0U;
    u32 value = 0U;

    while (*text != 0U) {
        if (recovered_text_console_putc_core(console, *text, &index, &value)) {
            if (out_last_index != (void *)0)
                *out_last_index = index;
            if (out_last_value != (void *)0)
                *out_last_value = value;
        }
        text++;
    }
    return 1U;
}

/* Absolute-global entries.  The state cells are not contiguous, so load and
 * store them explicitly. */
static void recovered_text_console_load(struct recovered_text_console *console)
{
    console->saved = *(volatile u32 *)(unsigned long)RECOVERED_TEXT_CELL_SAVED;
    console->column = *(volatile u32 *)(unsigned long)RECOVERED_TEXT_CELL_COLUMN;
    console->row = *(volatile u32 *)(unsigned long)RECOVERED_TEXT_CELL_ROW;
    console->attr = (u32)*(volatile u16 *)(unsigned long)
        RECOVERED_TEXT_CELL_ATTR;
}

static void recovered_text_console_store(const struct recovered_text_console *c)
{
    *(volatile u32 *)(unsigned long)RECOVERED_TEXT_CELL_SAVED = c->saved;
    *(volatile u32 *)(unsigned long)RECOVERED_TEXT_CELL_COLUMN = c->column;
    *(volatile u32 *)(unsigned long)RECOVERED_TEXT_CELL_ROW = c->row;
}

void recovered_text_console_reset_run(void)
{
    struct recovered_text_console console;
    volatile u32 *word;
    u32 index;

    recovered_text_console_reset_core(&console);
    recovered_text_console_store(&console);
    *(volatile u16 *)0x00504d24U = 0U;
    *(volatile u16 *)0x00504d26U = 0U;
    *(volatile u16 *)0x00504d28U = 0U;
    *(volatile u16 *)0x00504d2aU = 0U;
    *(volatile u16 *)0x00504d2cU = 0U;
    *(volatile u16 *)0x00504d2eU = 0U;
    *(volatile u16 *)0x00504d30U = 0U;
    *(volatile u16 *)0x00504d32U = 0U;
    *(volatile u32 *)0x00504d34U = 0U;
    *(volatile u32 *)0x00504d38U = 0U;

    word = (volatile u32 *)(unsigned long)RECOVERED_TEXT_NAMETABLE;
    for (index = 0U; index < RECOVERED_TEXT_NAMETABLE_WORDS; index++)
        word[index] = 0U;
    word = (volatile u32 *)(unsigned long)RECOVERED_TEXT_EXTRA_A;
    for (index = 0U; index < RECOVERED_TEXT_EXTRA_A_WORDS; index++)
        word[index] = 0U;
    word = (volatile u32 *)(unsigned long)RECOVERED_TEXT_EXTRA_B;
    for (index = 0U; index < RECOVERED_TEXT_EXTRA_B_WORDS; index++)
        word[index] = 0U;
    word = (volatile u32 *)(unsigned long)RECOVERED_TEXT_EXTRA_C;
    for (index = 0U; index < RECOVERED_TEXT_EXTRA_C_WORDS; index++)
        word[index] = 0U;
}

void recovered_text_console_emit_run(u32 code)
{
    *(volatile u32 *)(unsigned long)RECOVERED_TEXT_COMMAND = code;
}

void recovered_text_console_set_cursor_run(u32 a, u32 b)
{
    struct recovered_text_console console;

    recovered_text_console_load(&console);
    recovered_text_console_set_cursor_core(&console, a, b);
    recovered_text_console_store(&console);
}

void recovered_text_console_putc_run(u32 ch)
{
    struct recovered_text_console console;
    u32 index = 0U;
    u32 value = 0U;

    recovered_text_console_load(&console);
    if (recovered_text_console_putc_core(&console, ch, &index, &value)) {
        *(volatile u16 *)(unsigned long)
            (RECOVERED_TEXT_NAMETABLE + index * 2U) = (u16)value;
    }
    recovered_text_console_store(&console);
}

void recovered_text_console_puts_run(const volatile unsigned char *text)
{
    struct recovered_text_console console;
    u32 index = 0U;
    u32 value = 0U;

    recovered_text_console_load(&console);
    (void)recovered_text_console_puts_core(&console, text, &index, &value);
    *(volatile u16 *)(unsigned long)
        (RECOVERED_TEXT_NAMETABLE + index * 2U) = (u16)value;
    recovered_text_console_store(&console);
}
