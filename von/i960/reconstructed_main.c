/*
 * C reconstruction of the confirmed early vonj host path.
 *
 * This is intentionally separate from main.c, which remains the small
 * hardware smoke-test prototype.  The routines below preserve observed host
 * bus transfers; they do not claim to implement the SHARC or geometry
 * processors themselves.
 */

typedef unsigned long u32;
typedef unsigned short u16;

#define WORKRAM ((volatile u32 *)0x00500000)

u32 recovered_io_self_test(void);
void recovered_io_failure_prepare(void);
void recovered_io_input_initialize(void);
void recovered_host_queue_initialize(void);
void recovered_geometry_pipeline_startup(u32 mode);
void recovered_audio_initialize_scsp(void);
void recovered_audio_service_pending(void);

void i960_reconstructed_main(void)
{
    volatile u32 *const state = WORKRAM + 0x20;
    u32 io_result;

    state[0] = 0x52454330UL; /* REC0 */
    io_result = recovered_io_self_test();
    state[1] = io_result;
    if (io_result != 0) {
        recovered_io_failure_prepare();
        recovered_io_input_initialize();
        recovered_host_queue_initialize();
    }

    recovered_geometry_pipeline_startup(0);
    recovered_audio_initialize_scsp();
    state[3] = 0x47454f30UL; /* GEO0 */
    state[6] = 0;
    state[4] = 0x494e4954UL; /* INIT */

    for (;;) {
        recovered_audio_service_pending();
        state[5] = state[5] + 1;
    }
}
