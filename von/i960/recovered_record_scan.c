/* Recovered from i960 routine 0x000bf0c0. */

typedef unsigned int u32;

#define RECOVERED_RECORD_STRIDE 32U

/* Scan fixed-size records from count-1 down to zero. */
int recovered_record_find_last_nonempty(const unsigned char *records, u32 count)
{
    while (count != 0U)
    {
        --count;
        if (records[count * RECOVERED_RECORD_STRIDE] != 0U)
            return (int)count;
    }
    return -1;
}
