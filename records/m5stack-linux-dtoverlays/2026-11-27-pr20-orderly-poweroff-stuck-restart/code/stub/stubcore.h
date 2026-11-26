/*
 * Host stubs for modules/CardputerZero/powerfail_suo.c (m5stack-linux-dtoverlays
 * PR #20 follow-up, commit ff4cd84). Only the kernel APIs the driver touches
 * are modelled. Time is simulated: 1 jiffy == 1 ms, and delayed work is kept in
 * a small queue so the harness can advance time and run every due callback in
 * order.
 */
#ifndef STUB_CORE_H
#define STUB_CORE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <setjmp.h>
#include <errno.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int32_t  s32;
typedef struct { int counter; } atomic_t;

struct device_node { const char *compatible; int id; };
struct device { struct device_node *of_node; const char *name; };
struct platform_device { struct device dev; void *drvdata; };
struct i2c_client { struct device dev; };
struct gpio_desc { int value; };
struct backlight_device { int dummy; };

struct of_device_id { const char *compatible; };
struct platform_driver {
	int (*probe)(struct platform_device *);
	void (*remove)(struct platform_device *);
	void (*shutdown)(struct platform_device *);
	struct { const char *name; const struct of_device_id *of_match_table; } driver;
};

struct work_struct { void (*func)(struct work_struct *); };
struct delayed_work { struct work_struct work; };

#define container_of(ptr, type, member) \
	((type *)((char *)(ptr) - offsetof(type, member)))
#define to_delayed_work(w) container_of(w, struct delayed_work, work)
#define INIT_WORK(w, f) do { (w)->func = (f); } while (0)
#define INIT_DELAYED_WORK(w, f) do { (w)->work.func = (f); } while (0)

#define clamp_t(type, x, lo, hi) ({			\
	type __cx = (type)(x);				\
	type __clo = (type)(lo);			\
	type __chi = (type)(hi);			\
	__cx < __clo ? __clo : (__cx > __chi ? __chi : __cx); })

#define msecs_to_jiffies(m) ((unsigned long)(m))
#define time_after(a, b) ((long)((b) - (a)) < 0)
#define msleep(ms) sim_msleep(ms)

#define EPROBE_DEFER 517
#define ENOMEM 12
#define EIO 5
#define GFP_KERNEL 0
#define IRQ_HANDLED 1
#define IRQ_NONE 0

#define IS_ERR(p)  ((unsigned long)(void *)(p) >= (unsigned long)-4095)
#define PTR_ERR(p) ((long)(p))
#define ERR_PTR(e) ((void *)(long)(e))

enum gpiod_flags { GPIOD_IN = 0, GPIOD_OUT_LOW = 1, GPIOD_OUT_HIGH = 2 };

typedef int irqreturn_t;
typedef irqreturn_t (*irq_handler_t)(int, void *);

/* ---- generic helpers ---- */
#define MODULE_LICENSE(x)
#define MODULE_AUTHOR(x)
#define MODULE_DESCRIPTION(x)
#define MODULE_DEVICE_TABLE(a, b)
#define module_platform_driver(d) static struct platform_driver *const _unused_drv = &(d)

static inline void atomic_set(atomic_t *a, int v) { a->counter = v; }
static inline int atomic_read(const atomic_t *a) { return a->counter; }
static inline int atomic_xchg(atomic_t *a, int v)
{ int old = a->counter; a->counter = v; return old; }

/* ---- simulation state (defined in harness.c) ---- */
extern unsigned long jiffies;
extern int system_state;

#define SYSTEM_BOOT      0
#define SYSTEM_RESTART   1
#define SYSTEM_POWER_OFF 2
#define SYSTEM_HALT      3

extern int sim_switch;          /* power slider: 1 on, 0 off (raw irq-gpios level) */
extern int sim_irq_enabled;
extern int sim_gpio_fail;       /* gpiod_get_raw_value_cansleep() returns -EIO */
extern int sim_i2c_write_fail;  /* every SMBus write returns -EIO */
extern int sim_i2c_read_fail;   /* every SMBus read returns -EIO */
extern int sim_ioe_present;
extern int sim_has_power_ctrl;
extern int sim_has_disabled_gpios;
extern int sim_ioe_is_m5ioe1;
extern int sim_prop_debounce_ms;
extern int sim_prop_power_hold_ms;
extern int sim_bad_waiting_log;

extern int sim_orderly_calls;
extern int sim_orderly_force;
extern int sim_restart_calls;
extern int sim_sysrq_seq[8];
extern int sim_sysrq_len;
extern int sim_backlight_off;
extern int sim_disabled_writes;
extern int sim_disabled_value;
extern int sim_irq_enable_calls;
extern int sim_irq_disable_calls;

/* M5IOE1 model */
struct sim_chip {
	int state;                  /* 0 off, 1 on, 2 off-debounce, 3 countdown, 4 cutting */
	unsigned long t_state;
	unsigned long t_last;       /* last 50 ms poll boundary */
	int ready;                  /* 0xB0 bit0 */
	u16 off_time;               /* 0xB2/0xB3, clamped >= 200 */
	unsigned long debounce_ms;  /* state 2 -> 3 after this (normally 100) */
};
extern struct sim_chip chip;
extern int sim_chip_ready_writes;
extern unsigned long sim_chip_ready_write_at;

void sim_msleep(unsigned int ms);
void chip_reset(void);
void chip_advance(unsigned long now);
void chip_poll_tick(void);
int  chip_read_state(void);
int  chip_read_ready(void);
u16  chip_read_off_time(void);
void chip_write_off_time(u16 v);
void chip_write_ready(int v);

/* ---- kernel API stubs ---- */
struct device_node *of_parse_phandle(const struct device_node *np, const char *name, int index);
void of_node_put(struct device_node *np);
struct i2c_client *of_find_i2c_device_by_node(struct device_node *node);
int of_property_read_u32(const struct device_node *np, const char *name, u32 *out);

s32 i2c_smbus_write_i2c_block_data(const struct i2c_client *c, u8 cmd, u8 len, const u8 *values);
s32 i2c_smbus_read_word_data(const struct i2c_client *c, u8 cmd);
s32 i2c_smbus_read_byte_data(const struct i2c_client *c, u8 cmd);
s32 i2c_smbus_write_byte_data(const struct i2c_client *c, u8 cmd, u8 value);

struct gpio_desc *devm_gpiod_get(struct device *dev, const char *con, enum gpiod_flags flags);
struct gpio_desc *devm_gpiod_get_optional(struct device *dev, const char *con, enum gpiod_flags flags);
int gpiod_get_raw_value_cansleep(const struct gpio_desc *d);
void gpiod_set_value_cansleep(struct gpio_desc *d, int val);

int devm_request_irq(struct device *dev, unsigned int irq, irq_handler_t h,
		     unsigned long flags, const char *name, void *arg);
void disable_irq_nosync(unsigned int irq);
void enable_irq(unsigned int irq);

bool schedule_work(struct work_struct *w);
bool schedule_delayed_work(struct delayed_work *w, unsigned long delay);
bool cancel_work_sync(struct work_struct *w);
bool cancel_delayed_work_sync(struct delayed_work *w);

void orderly_poweroff(bool force);
void emergency_restart(void);
void handle_sysrq(int key);

struct backlight_device *devm_of_find_backlight(struct device *dev);
void backlight_device_set_brightness(struct backlight_device *bd, int v);

int platform_get_irq(struct platform_device *pdev, unsigned int n);
void *platform_get_drvdata(struct platform_device *pdev);
void platform_set_drvdata(struct platform_device *pdev, void *data);

static inline void put_device(struct device *d) { (void)d; }
static inline void *devm_kzalloc(struct device *dev, size_t n, int gfp)
{ (void)dev; (void)gfp; return calloc(1, n); }
int devm_add_action_or_reset(struct device *dev, void (*fn)(void *), void *arg);
const char *dev_name(const struct device *dev);

#define dev_emerg(dev, fmt, ...) sim_log("emerg", fmt, ##__VA_ARGS__)
#define dev_err(dev, fmt, ...)   sim_log("err  ", fmt, ##__VA_ARGS__)
#define dev_warn(dev, fmt, ...)  sim_log("warn ", fmt, ##__VA_ARGS__)
#define dev_info(dev, fmt, ...)  sim_log("info ", fmt, ##__VA_ARGS__)
#define dev_err_probe(dev, ret, fmt, ...) \
	({ sim_log("probe", fmt, ##__VA_ARGS__); (int)(ret); })

void sim_log(const char *lvl, const char *fmt, ...);

#endif
