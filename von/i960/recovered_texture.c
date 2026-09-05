/* Recovered from i960 routine 0x00028548. */

/* i960 words remain 32-bit when this source is compiled on an LP64 host. */
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

#define TEXTURE_RAM0 ((volatile u16 *)0x11400000)
#define TEXTURE_RAM1 ((volatile u16 *)0x11401000)
#define TEXTURE_TABLE ((volatile const u8 *)0x02fb1d10)
#define TEXTURE_BANK0 ((volatile u16 *)0x11000000)
#define TEXTURE_BANK1 ((volatile u16 *)0x11200000)
#define TEXTURE_SECOND_SOURCE ((volatile u32 *)0x00512bd0)
#define GEOMETRY_STATE_A ((volatile u32 *)0x005039f4)
#define GEOMETRY_STATE_B ((volatile u32 *)0x00503a00)
#define TEXT_LOADING_TEXTURE ((volatile const u8 *)0x000280e0)
#define TEXT_BANK0 ((volatile const u8 *)0x000280f0)
#define TEXT_DONE ((volatile const u8 *)0x00028100)
#define TEXT_BANK1 ((volatile const u8 *)0x00028110)

int recovered_texture_decompress(volatile const u8 *source,
                                 volatile u16 *primary,
                                 volatile u16 *secondary);
void recovered_text_set_position(u32 column, u32 row);
void recovered_text_write_string(volatile const u8 *text);

/* Deterministic table/ramp portion of the 0x28548 initializer. */
void recovered_texture_initialize_tables(volatile u16 *ramp_destination,
                                         volatile u16 *table_destination,
                                         volatile const u8 *table_source)
{
    u32 index;

    for (index = 1; index <= 0x7f; ++index)
        ramp_destination[index - 1] = (u16)(index >> 1);
    for (index = 1; index <= 0x7f; ++index)
        ramp_destination[0x7f + index - 1] = (u16)(index >> 1);
    for (index = 0; index <= 0x207f; ++index)
        table_destination[index] = (u16)table_source[index];
}

void recovered_texture_initializer(void)
{
    recovered_texture_initialize_tables(TEXTURE_RAM0, TEXTURE_RAM1,
                                        TEXTURE_TABLE);
}

/* Recovered from i960 loader/profile setup routine 0x00028120. */
int recovered_texture_loader_profile_setup(void)
{
    int status;

    recovered_text_set_position(8, 12);
    recovered_text_write_string(TEXT_LOADING_TEXTURE);
    recovered_text_set_position(25, 12);
    recovered_text_write_string(TEXT_BANK0);

    status = recovered_texture_decompress((volatile const u8 *)0x02c00008,
                                          TEXTURE_BANK0, TEXTURE_BANK1);
    if (status != 0)
        goto failed;

    recovered_text_write_string(TEXT_DONE);
    recovered_text_set_position(25, 13);
    recovered_text_write_string(TEXT_BANK1);

    *TEXTURE_SECOND_SOURCE = 0x02c77438U;
    status = recovered_texture_decompress((volatile const u8 *)0x02c77438,
                                          TEXTURE_BANK1, TEXTURE_BANK0);
    if (status == 0) {
        recovered_text_write_string(TEXT_DONE);
        return 0;
    }

failed:
    *GEOMETRY_STATE_B = 0;
    *GEOMETRY_STATE_A = 5;
    return status;
}
