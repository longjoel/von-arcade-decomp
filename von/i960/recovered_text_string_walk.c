/* Shared NUL-terminated text dispatcher recovered from 0x0001d1b0. */
typedef unsigned char u8;
typedef void (*recovered_text_emit_byte)(u8 value, void *opaque);

void recovered_text_string_walk(const u8 *string,
                                recovered_text_emit_byte emit,
                                void *opaque)
{
    while (*string != 0) {
        emit(*string, opaque);
        string++;
    }
}
