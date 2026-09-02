/* Mixed plain/converted upload sequence recovered from i960 0x20210. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_mixed_upload_record {
    u32 source;
    u32 helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

struct recovered_mixed_upload_plan {
    u32 origin;
    struct recovered_mixed_upload_record record[5];
};

void recovered_mixed_upload_plan(u32 caller_g14, u32 caller_g17,
                                u32 caller_g8, u32 caller_g12, u32 caller_g16,
                                struct recovered_mixed_upload_plan *plan)
{
    u32 row8 = caller_g8 + 31U;
    (void)caller_g17;
    (void)caller_g12;

    plan->origin = caller_g14;
    plan->record[0] = (struct recovered_mixed_upload_record){
        0x02fefee8U, 0x1dc10U, caller_g14, caller_g14, 0x40U, 30U
    };
    plan->record[1] = (struct recovered_mixed_upload_record){
        0x02ff16e8U, 0x1de80U, caller_g14, caller_g14, 0x40U, row8
    };
    plan->record[2] = (struct recovered_mixed_upload_record){
        0x02ff1568U, 0x1de80U, caller_g14, row8, 0x40U, 4U
    };
    plan->record[3] = (struct recovered_mixed_upload_record){
        0x02ff1568U, 0x1de80U, caller_g14, caller_g14, 0x40U, 4U
    };
    plan->record[4] = (struct recovered_mixed_upload_record){
        0x02ff1568U, 0x1de80U, caller_g14, caller_g16 + 31U, 0x40U, 4U
    };
}
