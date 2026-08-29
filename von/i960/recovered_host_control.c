/* Recovered host interrupt-mask/timer helper at i960 0x17c8-0x18a8. */

typedef unsigned int u32;

#define IRQ_CONTROL       (*(volatile u32 *)0x00501cd0)
#define IRQ_CONTROL_MMIO  (*(volatile u32 *)0x00e80004)
#define IRQ_ACK_MMIO      (*(volatile u32 *)0x00e80000)

u32 recovered_host_timer_address(u32 mask)
{
    if (mask == 4U)
        return 0x00f00000U;
    if (mask == 8U)
        return 0x00f00004U;
    if (mask == 16U)
        return 0x00f00008U;
    if (mask == 32U)
        return 0x00f0000cU;
    return 0U;
}

u32 recovered_host_timer_reload(u32 mask)
{
    if (mask == 4U)
        return 0x000186a0U;
    if (mask == 8U || mask == 16U || mask == 32U)
        return 0x000fffffU;
    return 0U;
}

static volatile u32 *recovered_host_timer(u32 mask)
{
    if (mask == 4U)
        return (volatile u32 *)0x00f00000UL;
    if (mask == 8U)
        return (volatile u32 *)0x00f00004UL;
    if (mask == 16U)
        return (volatile u32 *)0x00f00008UL;
    if (mask == 32U)
        return (volatile u32 *)0x00f0000cUL;
    return (volatile u32 *)0;
}

/* Clear, optionally reload, and re-arm one host interrupt source. */
void recovered_host_interrupt_mask_update(u32 mask)
{
    u32 control = IRQ_CONTROL;
    u32 timer_reload = recovered_host_timer_reload(mask);
    volatile u32 *timer = recovered_host_timer(mask);

    control &= ~mask;
    IRQ_CONTROL = control;
    IRQ_CONTROL_MMIO = control;
    if (timer != (volatile u32 *)0) {
        *timer = 0U;
        *timer = timer_reload;
    }
    control = IRQ_CONTROL | mask;
    IRQ_CONTROL_MMIO = control;
    IRQ_CONTROL = control;
    IRQ_ACK_MMIO = ~mask;
}
