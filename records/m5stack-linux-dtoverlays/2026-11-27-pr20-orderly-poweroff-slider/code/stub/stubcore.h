/* Host stub core for compiling modules/CardputerZero/powerfail_suo.c
 * outside the kernel. Only the semantics the driver depends on are modelled:
 * simulated M5IOE1 register file, simulated jiffies, recorded workqueue
 * scheduling, recorded sysrq / orderly_poweroff calls.
 */
#ifndef STUB_CORE_H
#define STUB_CORE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <errno.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int32_t  s32;

struct device_node { const char *compatible; int id; };
struct device { struct device_node *of_node; const char *name; };

#define container_of(ptr, type, member) \
	((type *)((char *)(ptr) - offsetof(type, member)))

#ifndef clamp_t
#define clamp_t(type, x, lo, hi) ({			\
	type __cx = (type)(x);				\
	type __clo = (type)(lo);			\
	type __chi = (type)(hi);			\
	__cx < __clo ? __clo : (__cx > __chi ? __chi : __cx); })
#endif

#define EPROBE_DEFER 517

#define IS_ERR(p)  ((unsigned long)(void *)(p) >= (unsigned long)-4095)
#define PTR_ERR(p) ((long)(p))
#define ERR_PTR(e) ((void *)(long)(e))

/* ---- simulation state (defined in harness.c) ---- */
extern unsigned long jiffies;
#define SYSTEM_BOOT      0
#define SYSTEM_RESTART   1
#define SYSTEM_POWER_OFF 2
#define SYSTEM_HALT      3
extern int system_state;

extern int sim_irq_level;          /* level of irq-gpios */
extern int sim_ioe_present;        /* m5ioe1 i2c client exists */
extern int sim_has_power_ctrl;     /* m5stack,power-controller phandle */
extern int sim_has_disabled_gpios; /* disabled-gpios phandle */
extern int sim_disabled_is_m5ioe1;
extern int sim_prop_debounce_ms;   /* -1: absent */
extern int sim_prop_power_hold_ms; /* -1: absent */
extern int sim_i2c_write_fail;
extern int sim_i2c_read_fail;

extern u16 sim_off_time_reg;       /* 0xB2/0xB3 */
extern int sim_power_state_seq[8]; /* scripted 0xB6 reads */
extern int sim_power_state_len;
extern int sim_power_state_idx;

extern int sim_orderly_calls;
extern int sim_orderly_force;
extern int sim_sysrq_seq[8];
extern int sim_sysrq_len;
extern int sim_backlight_off;
extern int sim_disabled_gpio_writes;
extern int sim_disabled_gpio_value;
extern int sim_irq_enable_calls;
extern int sim_irq_disable_calls;
extern int sim_work_pending;
extern int sim_backstop_armed;
extern unsigned long sim_backstop_delay;

void sim_msleep(unsigned int ms);
int  sim_next_power_state(void);

#endif
