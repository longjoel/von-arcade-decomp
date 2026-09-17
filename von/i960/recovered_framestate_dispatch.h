#ifndef RECOVERED_FRAMESTATE_DISPATCH_H
#define RECOVERED_FRAMESTATE_DISPATCH_H

typedef unsigned char recovered_framestate_u8;
typedef unsigned short recovered_framestate_u16;
typedef unsigned int recovered_framestate_u32;
typedef signed int recovered_framestate_s32;

typedef recovered_framestate_u32 (*recovered_framestate_arm)(
    volatile unsigned char *object);

/* Pure 0x37130 frame-step dispatch (i960 0x37350-0x37388). */
recovered_framestate_u32 recovered_framestate_dispatch_core(
    volatile unsigned char *object,
    const recovered_framestate_arm *table,
    recovered_framestate_u32 count);

/* Absolute-global entry binding the recovered 0x37130 arm bodies. */
recovered_framestate_u32 recovered_framestate_dispatch_run(
    volatile unsigned char *object);

#endif /* RECOVERED_FRAMESTATE_DISPATCH_H */
