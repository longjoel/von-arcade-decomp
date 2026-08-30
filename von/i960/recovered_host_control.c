/* Recovered host interrupt-mask, timer, and dispatcher helpers. */

typedef unsigned int u32;

#define IRQ_CONTROL       (*(volatile u32 *)0x00501cd0)
#define IRQ_CONTROL_MMIO  (*(volatile u32 *)0x00e80004)
#define IRQ_ACK_MMIO      (*(volatile u32 *)0x00e80000)
#define TIMER_0            (*(volatile u32 *)0x00f00000)
#define TIMER_1            (*(volatile u32 *)0x00f00004)
#define TIMER_2            (*(volatile u32 *)0x00f00008)
#define TIMER_3            (*(volatile u32 *)0x00f0000c)
#define HOST_TIMER_STATE   (*(volatile u32 *)0x0051aac0)

enum recovered_host_interrupt_route {
    HOST_INTERRUPT_ROUTE_ACK = 0U,
    HOST_INTERRUPT_ROUTE_SYSTEM = 1U,
    HOST_INTERRUPT_ROUTE_FATAL = 2U,
    HOST_INTERRUPT_ROUTE_TEXT = 3U,
    HOST_INTERRUPT_ROUTE_AUDIO = 4U,
    HOST_INTERRUPT_ROUTE_UNHANDLED = 5U
};

/* The original 0x12d0 path flushes registers and loops forever. */
u32 recovered_host_fatal_halt_is_terminal(void)
{
    return 1U;
}

void recovered_host_fatal_halt(void)
{
    for (;;) {
    }
}

/* Route values selected by the common 0x1380 dispatcher. */
u32 recovered_host_interrupt_route(u32 mask)
{
    if (mask == 1U)
        return HOST_INTERRUPT_ROUTE_SYSTEM;
    if (mask == 2U || mask == 0x800U)
        return HOST_INTERRUPT_ROUTE_FATAL;
    if (mask == 0x200U)
        return HOST_INTERRUPT_ROUTE_TEXT;
    if (mask == 0x400U)
        return HOST_INTERRUPT_ROUTE_AUDIO;
    if (mask > 0x80U)
        return HOST_INTERRUPT_ROUTE_UNHANDLED;
    return HOST_INTERRUPT_ROUTE_ACK;
}

u32 recovered_host_interrupt_ack_value(u32 mask)
{
    return ~mask;
}

u32 recovered_host_interrupt_rearm_control(u32 control, u32 mask)
{
    return control | mask;
}

/* Recovered dispatcher acknowledgement tail at i960 0x1750-0x1780. */
void recovered_host_interrupt_acknowledge(u32 mask)
{
    u32 control;

    IRQ_ACK_MMIO = recovered_host_interrupt_ack_value(mask);
    control = recovered_host_interrupt_rearm_control(IRQ_CONTROL, mask);
    IRQ_CONTROL = control;
    IRQ_CONTROL_MMIO = control;
}

u32 recovered_host_timer_initial_value(void)
{
    return 0x00061a80U;
}

u32 recovered_host_initial_interrupt_control(void)
{
    return 0x0000023dU;
}

/* Recovered 0x1bb8 timer and interrupt bootstrap. */
void recovered_host_interrupt_initialize(void)
{
    u32 timer_value = recovered_host_timer_initial_value();
    u32 control = recovered_host_initial_interrupt_control();

    IRQ_ACK_MMIO = 0U;
    TIMER_1 = timer_value;
    TIMER_0 = timer_value;
    TIMER_3 = timer_value;
    TIMER_2 = timer_value;
    IRQ_CONTROL = control;
    IRQ_CONTROL_MMIO = control;
    HOST_TIMER_STATE = 0U;
}

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
