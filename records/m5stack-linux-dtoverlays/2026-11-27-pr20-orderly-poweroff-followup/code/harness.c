/*
 * Host-level harness for modules/CardputerZero/powerfail_suo.c at
 * m5stack/m5stack-linux-dtoverlays PR #20 head ff4cd84 (second review round).
 *
 * The driver's real source is compiled unchanged against stub kernel headers.
 * Time is simulated (1 jiffy = 1 ms) and delayed work runs from a queue in due
 * order, so the new recheck/ready/backstop timing can be asserted exactly.
 *
 * The M5IOE1 below is a model of the documented power state machine
 * (0:off 1:on 2:off-debounce 3:countdown 4:cutting; 100 ms debounce; state 3
 * compares against the live OFF_TIME and clears READY; state 4 drops PWR_EN for
 * 100 ms and returns to 0). It is a model of the register table, not a measured
 * chip; with the slider on, the boost is held by SW_EN and the SoC stays up.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <setjmp.h>
#include <stdarg.h>

#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/of.h>
#include <linux/i2c.h>
#include <linux/gpio/consumer.h>
#include <linux/interrupt.h>
#include <linux/reboot.h>
#include <linux/sysrq.h>
#include <linux/workqueue.h>
#include <linux/delay.h>
#include <linux/backlight.h>
#include <linux/slab.h>
#include <linux/atomic.h>

/* ---------------- simulation state ---------------- */
unsigned long jiffies;
int system_state;

int sim_switch = 1;
int sim_irq_enabled = 1;
int sim_gpio_fail;
int sim_i2c_write_fail;
int sim_i2c_read_fail;
int sim_state_read_fail;
int sim_ioe_present = 1;
int sim_has_power_ctrl = 1;
int sim_has_disabled_gpios = 1;
int sim_ioe_is_m5ioe1 = 1;
int sim_prop_debounce_ms = 500;
int sim_prop_power_hold_ms = -1;   /* m5stack,power-hold-ms */
int sim_prop_legacy_hold_ms = -1;  /* power-hold-ms (no vendor prefix) */
int sim_bad_waiting_log;

int sim_orderly_calls;
int sim_orderly_force = -1;
int sim_restart_calls;
int sim_sysrq_seq[8];
int sim_sysrq_len;
int sim_backlight_off;
int sim_disabled_writes;
int sim_disabled_value = -1;
int sim_irq_enable_calls;
int sim_irq_disable_calls;
int sim_chip_ready_writes;
unsigned long sim_chip_ready_write_at;

struct sim_chip chip;
static int fails;
static int checks;

/* ---------------- M5IOE1 model ---------------- */
void chip_reset(void)
{
	chip.state = 1;          /* switch on, power pass done */
	chip.t_state = 0;
	chip.t_last = 0;
	chip.ready = 1;          /* m5ioe1 probe set it (REV 0x5A) */
	chip.off_time = 2000;    /* stock power-up value */
	chip.debounce_ms = 100;
}

void chip_poll_tick(void)
{
	unsigned long now = chip.t_last;

	switch (chip.state) {
	case 0:
		if (sim_switch) {
			chip.state = 1;
			chip.t_state = now;
		}
		break;
	case 1:
		if (!sim_switch) {
			chip.state = 2;
			chip.t_state = now;
		}
		break;
	case 2:
		if (sim_switch) {
			chip.state = 1;
			chip.t_state = now;
		} else if (now - chip.t_state >= chip.debounce_ms) {
			chip.state = 3;
			chip.t_state = now;
			chip.ready = 0;      /* the countdown clears READY */
		}
		break;
	case 3:
		/* OFF_TIME is re-read live on every pass */
		if (now - chip.t_state >= chip.off_time) {
			chip.state = 4;      /* PWR_EN low */
			chip.t_state = now;
		}
		break;
	case 4:
		if (now - chip.t_state >= 100) {
			chip.state = 0;      /* switch on -> straight back to 1 */
			chip.t_state = now;
		}
		break;
	}
}

void chip_advance(unsigned long now)
{
	while (chip.t_last + 50 <= now) {
		chip.t_last += 50;
		chip_poll_tick();
	}
}

int chip_read_state(void)
{
	chip_advance(jiffies);
	if (sim_state_read_fail)
		return -EIO;
	return chip.state;
}

int chip_read_ready(void)
{
	chip_advance(jiffies);
	return chip.ready;
}

u16 chip_read_off_time(void) { return chip.off_time; }

void chip_write_off_time(u16 v)
{
	if (v < 200)
		v = 200;
	chip.off_time = v;
}

void chip_write_ready(int v)
{
	chip.ready = v & 1;
	if (v == 1) {
		sim_chip_ready_writes++;
		sim_chip_ready_write_at = jiffies;
	}
}

/* ---------------- kernel API stubs ---------------- */
static struct i2c_client g_ioe;
static struct gpio_desc g_irq_desc, g_disabled_desc;
static struct backlight_device g_bl;
static struct device_node g_power_node = { "cardputerzero,powerfail-suo", 1 };
static struct device_node g_ioe_node = { "m5stack,m5ioe1", 2 };
static struct device_node g_other_node = { "gpio-keys", 3 };
static irq_handler_t g_handler;
static void *g_handler_arg;

struct device_node *of_parse_phandle(const struct device_node *np, const char *name, int index)
{
	(void)np; (void)index;
	if (!strcmp(name, "m5stack,power-controller"))
		return sim_has_power_ctrl ? &g_ioe_node : NULL;
	if (!strcmp(name, "disabled-gpios"))
		return sim_has_disabled_gpios ? (sim_ioe_is_m5ioe1 ? &g_ioe_node : &g_other_node) : NULL;
	return NULL;
}
void of_node_put(struct device_node *np) { (void)np; }
struct i2c_client *of_find_i2c_device_by_node(struct device_node *node)
{ return (node == &g_ioe_node && sim_ioe_present) ? &g_ioe : NULL; }
int of_property_read_u32(const struct device_node *np, const char *name, u32 *out)
{
	(void)np;
	if (!strcmp(name, "debounce-ms") && sim_prop_debounce_ms >= 0) {
		*out = sim_prop_debounce_ms;
		return 0;
	}
	if (!strcmp(name, "m5stack,power-hold-ms") && sim_prop_power_hold_ms >= 0) {
		*out = sim_prop_power_hold_ms;
		return 0;
	}
	if (!strcmp(name, "power-hold-ms") && sim_prop_legacy_hold_ms >= 0) {
		*out = sim_prop_legacy_hold_ms;
		return 0;
	}
	return -EINVAL;
}

s32 i2c_smbus_write_i2c_block_data(const struct i2c_client *c, u8 cmd, u8 len, const u8 *values)
{
	(void)c;
	if (sim_i2c_write_fail)
		return -EIO;
	if (cmd == 0xB2 && len == 2) {
		u16 v = (u16)(values[0] | (values[1] << 8));
		printf("[t=%6lu] I2C  0xB2 <- %u\n", jiffies, v);
		chip_write_off_time(v);
		return 0;
	}
	return -EIO;
}
s32 i2c_smbus_read_word_data(const struct i2c_client *c, u8 cmd)
{
	(void)c;
	if (sim_i2c_read_fail)
		return -EIO;
	if (cmd == 0xB2)
		return chip_read_off_time();
	return -EIO;
}
s32 i2c_smbus_read_byte_data(const struct i2c_client *c, u8 cmd)
{
	(void)c;
	if (cmd == 0xB6)
		return chip_read_state();
	if (cmd == 0xB0)
		return chip_read_ready();
	return -EIO;
}
s32 i2c_smbus_write_byte_data(const struct i2c_client *c, u8 cmd, u8 value)
{
	(void)c;
	if (sim_i2c_write_fail)
		return -EIO;
	if (cmd == 0xB0) {
		printf("[t=%6lu] I2C  0xB0 <- %u (READY)\n", jiffies, value);
		chip_write_ready(value);
		return 0;
	}
	return -EIO;
}

struct gpio_desc *devm_gpiod_get(struct device *dev, const char *con, enum gpiod_flags flags)
{ (void)dev; (void)con; (void)flags; return &g_irq_desc; }
struct gpio_desc *devm_gpiod_get_optional(struct device *dev, const char *con, enum gpiod_flags flags)
{ (void)dev; (void)con; (void)flags; return sim_has_disabled_gpios ? &g_disabled_desc : NULL; }
int gpiod_get_raw_value_cansleep(const struct gpio_desc *d)
{ (void)d; return sim_gpio_fail ? -EIO : sim_switch; }
void gpiod_set_value_cansleep(struct gpio_desc *d, int val)
{ (void)d; sim_disabled_writes++; sim_disabled_value = val; }

int devm_request_irq(struct device *dev, unsigned int irq, irq_handler_t h,
		     unsigned long flags, const char *name, void *arg)
{ (void)dev; (void)irq; (void)flags; (void)name; g_handler = h; g_handler_arg = arg; return 0; }
void disable_irq_nosync(unsigned int irq) { (void)irq; sim_irq_disable_calls++; sim_irq_enabled = 0; }
void enable_irq(unsigned int irq) { (void)irq; sim_irq_enable_calls++; sim_irq_enabled = 1; }

static jmp_buf restart_jb;
static int restart_jb_valid;

void orderly_poweroff(bool force) { sim_orderly_calls++; sim_orderly_force = force; }
void emergency_restart(void)
{
	sim_restart_calls++;
	if (restart_jb_valid) {
		restart_jb_valid = 0;
		longjmp(restart_jb, 1);
	}
	fprintf(stderr, "emergency_restart() from an unexpected place\n");
	exit(2);
}
void handle_sysrq(int key)
{
	if (sim_sysrq_len < 8)
		sim_sysrq_seq[sim_sysrq_len++] = key;
}

struct backlight_device *devm_of_find_backlight(struct device *dev) { (void)dev; return &g_bl; }
void backlight_device_set_brightness(struct backlight_device *bd, int v)
{ (void)bd; if (v == 0) sim_backlight_off++; }

int platform_get_irq(struct platform_device *p, unsigned int n) { (void)p; (void)n; return 185; }
void *platform_get_drvdata(struct platform_device *p) { return p->drvdata; }
void platform_set_drvdata(struct platform_device *p, void *d) { p->drvdata = d; }

int devm_add_action_or_reset(struct device *dev, void (*fn)(void *), void *arg)
{ (void)dev; (void)fn; (void)arg; return 0; }
const char *dev_name(const struct device *dev) { return dev->name; }
void sim_msleep(unsigned int ms) { jiffies += ms; }

/* ---------------- driver under test ---------------- */
#ifndef DRIVER_SRC
#define DRIVER_SRC "powerfail_suo.c"
#endif
#include DRIVER_SRC

/* ---------------- work queue ---------------- */
struct qent {
	struct delayed_work *dw;
	unsigned long due;
	int pending;
};
static struct qent queue[8];
static struct platform_device pdev;

static struct powerfail_suo_data *drv(void) { return pdev.drvdata; }

static const char *w_name(struct delayed_work *w)
{
	if (!drv())
		return "work";
	if (w == &drv()->check)
		return "check";
	if (w == &drv()->backstop)
		return "backstop";
	if (w == &drv()->ready)
		return "ready";
	return "work";
}

void sim_log(const char *lvl, const char *fmt, ...)
{
	va_list ap;

	printf("[t=%6lu] %s ", jiffies, lvl);
	va_start(ap, fmt);
	vprintf(fmt, ap);
	va_end(ap);
}

static struct qent *q_find(struct delayed_work *w)
{
	int i;

	for (i = 0; i < 8; i++)
		if (queue[i].dw == w)
			return &queue[i];
	return NULL;
}

bool schedule_delayed_work(struct delayed_work *w, unsigned long delay)
{
	struct qent *e = q_find(w);
	int i;

	if (e && e->pending)
		return false;
	if (!e) {
		for (i = 0; i < 8; i++)
			if (!queue[i].dw) {
				e = &queue[i];
				break;
			}
	}
	if (!e) {
		fprintf(stderr, "queue full\n");
		exit(2);
	}
	e->dw = w;
	e->due = jiffies + delay;
	e->pending = 1;
	printf("[t=%6lu] ARM  %-8s delay=%lu due=%lu\n", jiffies, w_name(w), delay, e->due);
	return true;
}

bool cancel_delayed_work_sync(struct delayed_work *w)
{
	struct qent *e = q_find(w);

	if (e && e->pending) {
		e->pending = 0;
		printf("[t=%6lu] CANCEL %-8s (was due %lu)\n", jiffies, w_name(w), e->due);
		return true;
	}
	return false;
}

bool schedule_work(struct work_struct *w) { (void)w; return true; }
bool cancel_work_sync(struct work_struct *w) { (void)w; return true; }

static void run_until(unsigned long t)
{
	for (;;) {
		struct qent *best = NULL;
		int i;

		for (i = 0; i < 8; i++)
			if (queue[i].dw && queue[i].pending && queue[i].due <= t &&
			    (!best || queue[i].due < best->due))
				best = &queue[i];
		if (!best)
			break;
		jiffies = best->due;
		best->pending = 0;
		best->dw->work.func(&best->dw->work);
	}
	if (jiffies < t)
		jiffies = t;
}


/* ---------------- scenarios ---------------- */
static void reset_all(void)
{
	int i;

	jiffies = 0;
	system_state = SYSTEM_BOOT;
	sim_switch = 1;
	sim_irq_enabled = 1;
	sim_gpio_fail = 0;
	sim_i2c_write_fail = 0;
	sim_i2c_read_fail = 0;
	sim_state_read_fail = 0;
	sim_ioe_present = 1;
	sim_has_power_ctrl = 1;
	sim_has_disabled_gpios = 1;
	sim_ioe_is_m5ioe1 = 1;
	sim_prop_debounce_ms = 500;
	sim_prop_power_hold_ms = -1;
	sim_prop_legacy_hold_ms = -1;
	sim_orderly_calls = 0;
	sim_orderly_force = -1;
	sim_restart_calls = 0;
	sim_sysrq_len = 0;
	sim_backlight_off = 0;
	sim_disabled_writes = 0;
	sim_disabled_value = -1;
	sim_irq_enable_calls = 0;
	sim_irq_disable_calls = 0;
	sim_chip_ready_writes = 0;
	sim_chip_ready_write_at = 0;
	chip_reset();
	for (i = 0; i < 8; i++)
		queue[i] = (struct qent){ 0 };
	g_handler = NULL;
	g_handler_arg = NULL;
	memset(&pdev, 0, sizeof(pdev));
	pdev.dev.of_node = &g_power_node;
	pdev.dev.name = "powerfail";
}

static void expect(const char *what, int cond)
{
	checks++;
	if (!cond)
		fails++;
	printf("  %-58s %s\n", what, cond ? "PASS" : "FAIL");
}

static int do_probe(void)
{
	return powerfail_suo_probe(&pdev);
}

static void fire_irq(void)
{
	if (sim_irq_enabled && g_handler)
		g_handler(185, g_handler_arg);
}

static void set_switch(int on)
{
	if (on == sim_switch)
		return;
	chip_advance(jiffies);           /* let the chip see the old level first */
	sim_switch = on;
	printf("[t=%6lu] ---- slider %s (irq-gpios %s)\n", jiffies, on ? "ON" : "OFF",
	       on ? "high" : "low");
	if (!on)
		fire_irq();
}

static unsigned long due_of(struct delayed_work *w)
{
	struct qent *e = q_find(w);

	return (e && e->pending) ? e->due : 0;
}

int main(void)
{

	printf("== T1 probe: m5stack,power-controller + default hold ==\n");
	reset_all();
	expect("probe returns 0", do_probe() == 0);
	expect("hold_ms = 20000", drv() && drv()->hold_ms == 20000);
	expect("OFF_TIME 0xB2/0xB3 = 20000", chip.off_time == 20000);
	run_until(100);

	printf("== T2 no power controller: legacy SysRq U only ==\n");
	reset_all();
	sim_has_power_ctrl = 0;
	sim_has_disabled_gpios = 0;
	expect("probe returns 0", do_probe() == 0);
	expect("ioe stays NULL", drv() && drv()->ioe == NULL);
	expect("stock OFF_TIME 2000 untouched", chip.off_time == 2000);
	run_until(1000);
	set_switch(0);
	run_until(6000);
	expect("SysRq U fired", sim_sysrq_len == 1 && sim_sysrq_seq[0] == 'u');
	expect("no orderly_poweroff", sim_orderly_calls == 0);
	expect("no backstop", due_of(&drv()->backstop) == 0);
	expect("IRQ left disabled (one-shot)", sim_irq_enable_calls == 0);

	printf("== T3 no power-controller but disabled-gpios is the M5IOE1: no fallback ==\n");
	reset_all();
	sim_has_power_ctrl = 0;
	sim_has_disabled_gpios = 1;
	sim_ioe_is_m5ioe1 = 1;
	expect("probe returns 0", do_probe() == 0);
	expect("new path not entered", drv() && drv()->ioe == NULL);
	expect("stock OFF_TIME 2000 untouched", chip.off_time == 2000);

	printf("== T4 phandle present, i2c client absent: -EPROBE_DEFER ==\n");
	reset_all();
	sim_ioe_present = 0;
	expect("probe returns -EPROBE_DEFER", do_probe() == -EPROBE_DEFER);

	printf("== T5 slider off, countdown confirmed: orderly poweroff ==\n");
	reset_all();
	expect("probe returns 0", do_probe() == 0);
	run_until(1000);
	set_switch(0);
	run_until(1500);
	expect("one orderly_poweroff(force=true)", sim_orderly_calls == 1 && sim_orderly_force == 1);
	expect("OFF_TIME rewritten to 20000", chip.off_time == 20000);
	expect("backlight off", sim_backlight_off == 1);
	expect("slider_off latched", drv() && atomic_read(&drv()->slider_off) == 1);
	expect("backstop due 17000 (flip 1000 + 20000 - 4000)", due_of(&drv()->backstop) == 17000);
	expect("IRQ still disabled while low", sim_irq_enabled == 0);
	system_state = SYSTEM_POWER_OFF;
	powerfail_suo_shutdown(&pdev);
	expect("poweroff cuts at 200 ms", chip.off_time == 200);
	expect("backstop cancelled at shutdown", due_of(&drv()->backstop) == 0);
	expect("disabled-gpios asserted", sim_disabled_value == 1);
	expect("no restart", sim_restart_calls == 0);

	printf("== T6 debounce outlasts the 500 ms check: recheck, then orderly ==\n");
	reset_all();
	expect("probe returns 0", do_probe() == 0);
	chip.debounce_ms = 700;          /* the case the new recheck exists for */
	run_until(1000);
	set_switch(0);
	run_until(1600);
	expect("no decision while 0xB6 reads DEBOUNCE(2)", sim_orderly_calls == 0);
	expect("IRQ not re-enabled while the line is low", sim_irq_enable_calls == 0);
	expect("check re-armed for +100 ms", due_of(&drv()->check) == 1700);
	run_until(1700);
	expect("still DEBOUNCE(2) at 1700: another recheck", sim_orderly_calls == 0 &&
	       due_of(&drv()->check) == 1800);
	run_until(1800);
	expect("orderly_poweroff once at 1800", sim_orderly_calls == 1);
	expect("backstop due 17700 (last ON/DEBOUNCE read 1700 + 16000)", due_of(&drv()->backstop) == 17700);
	expect("real chip cut 21750, backstop 4.05 s earlier", chip.state == 3 && chip.t_state == 1750);

	printf("== T7 line goes high during the countdown: no poweroff, READY restored ==\n");
	reset_all();
	expect("probe returns 0", do_probe() == 0);
	run_until(1000);
	set_switch(0);                   /* IRQ, check at 1500 */
	run_until(1200);                 /* chip now in countdown, READY cleared */
	chip_advance(1200);
	expect("chip countdown started, READY cleared", chip.state == 3 && chip.ready == 0);
	run_until(1300);
	set_switch(1);                   /* before the check: no rising IRQ */
	run_until(1500);
	expect("no orderly_poweroff", sim_orderly_calls == 0);
	expect("no backstop", due_of(&drv()->backstop) == 0);
	expect("IRQ re-enabled because the line is high", sim_irq_enable_calls == 1 && sim_irq_enabled == 1);
	expect("ready work armed", due_of(&drv()->ready) != 0);
	run_until(21000);
	expect("no READY write while the countdown still runs", sim_chip_ready_writes == 0);
	expect("chip still counting at 21000", chip.state == 3);
	run_until(21500);
	expect("READY written once at 21500, after 0xB6 reads ON", sim_chip_ready_writes == 1 &&
	       sim_chip_ready_write_at == 21500 && chip.ready == 1);
	expect("no poweroff / no restart", sim_orderly_calls == 0 && sim_restart_calls == 0);
	expect("hold stays 20000", chip.off_time == 20000);

	printf("== T8 slider high at .shutdown after a slider-off: emergency restart ==\n");
	reset_all();
	expect("probe returns 0", do_probe() == 0);
	run_until(1000);
	set_switch(0);
	run_until(1500);
	expect("orderly poweroff started", sim_orderly_calls == 1);
	set_switch(1);                   /* 3000, during the poweroff */
	run_until(3000);
	system_state = SYSTEM_POWER_OFF;
	restart_jb_valid = 1;
	if (setjmp(restart_jb) == 0)
		powerfail_suo_shutdown(&pdev);
	expect("emergency_restart() called once", sim_restart_calls == 1);
	expect("200 ms cut NOT programmed", chip.off_time == 20000);
	expect("disabled-gpios NOT asserted", sim_disabled_writes == 0);
	expect("backstop cancelled first", due_of(&drv()->backstop) == 0);

	printf("== T9 slider low at .shutdown after a slider-off: no restart, 200 ms ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1500);
	system_state = SYSTEM_POWER_OFF;
	powerfail_suo_shutdown(&pdev);
	expect("no restart", sim_restart_calls == 0);
	expect("OFF_TIME 200 ms", chip.off_time == 200);
	expect("disabled-gpios asserted", sim_disabled_value == 1);

	printf("== T10 menu poweroff (slider still on): 200 ms, no restart ==\n");
	reset_all();
	do_probe();
	system_state = SYSTEM_POWER_OFF;
	powerfail_suo_shutdown(&pdev);
	expect("OFF_TIME 200 ms", chip.off_time == 200);
	expect("no restart", sim_restart_calls == 0);
	expect("disabled-gpios untouched", sim_disabled_writes == 0);

	printf("== T11 .shutdown on reboot: OFF_TIME untouched ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1500);
	system_state = SYSTEM_RESTART;
	powerfail_suo_shutdown(&pdev);
	expect("OFF_TIME stays 20000", chip.off_time == 20000);
	expect("no restart", sim_restart_calls == 0);
	expect("backstop cancelled", due_of(&drv()->backstop) == 0);

	printf("== T12 hold 12000: backstop no earlier than 8 s ==\n");
	reset_all();
	sim_prop_power_hold_ms = 12000;
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1500);
	expect("hold_ms = 12000", drv()->hold_ms == 12000);
	expect("OFF_TIME 12000", chip.off_time == 12000);
	expect("backstop due 9000 (8 s after the flip)", due_of(&drv()->backstop) == 9000);
	expect("real cut 13000, backstop 4 s earlier", 9000 == 13000 - 4000);

	printf("== T13 hold clamping ==\n");
	reset_all();
	sim_prop_power_hold_ms = 4000;
	do_probe();
	expect("4000 -> 12000", drv()->hold_ms == 12000);
	reset_all();
	sim_prop_power_hold_ms = 8000;
	do_probe();
	expect("8000 -> 12000", drv()->hold_ms == 12000);
	reset_all();
	sim_prop_power_hold_ms = 70000;
	do_probe();
	expect("70000 -> 60000", drv()->hold_ms == 60000);

	printf("== T14 unprefixed power-hold-ms is ignored (renamed property) ==\n");
	reset_all();
	sim_prop_legacy_hold_ms = 12000;
	do_probe();
	expect("hold_ms = 20000 default", drv()->hold_ms == 20000);
	expect("OFF_TIME 20000", chip.off_time == 20000);

	printf("== T15 backstop body: SysRq S, 1 s, SysRq U ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1500);
	jiffies = due_of(&drv()->backstop);
	powerfail_backstop_work(&drv()->backstop.work);
	expect("S then U", sim_sysrq_len == 2 && sim_sysrq_seq[0] == 's' && sim_sysrq_seq[1] == 'u');

	printf("== T16 OFF_TIME write fails at the event: legacy path ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	sim_i2c_write_fail = 1;
	run_until(1500);
	expect("SysRq U", sim_sysrq_len == 1 && sim_sysrq_seq[0] == 'u');
	expect("no orderly_poweroff", sim_orderly_calls == 0);
	expect("disabled-gpios asserted", sim_disabled_value == 1);
	expect("backlight off", sim_backlight_off == 1);
	expect("no backstop", due_of(&drv()->backstop) == 0);

	printf("== T17 OFF_TIME write fails at probe: legacy from then on ==\n");
	reset_all();
	sim_i2c_write_fail = 1;
	do_probe();
	expect("ioe dropped to NULL", drv()->ioe == NULL);
	expect("stock OFF_TIME 2000 untouched", chip.off_time == 2000);
	sim_i2c_write_fail = 0;
	run_until(1000);
	set_switch(0);
	run_until(6000);
	expect("SysRq U on the flip", sim_sysrq_len == 1 && sim_sysrq_seq[0] == 'u');
	expect("no orderly_poweroff", sim_orderly_calls == 0);

	printf("== T18 remove: restore 2000 only when no slider-off is latched ==\n");
	reset_all();
	do_probe();
	powerfail_suo_remove(&pdev);
	expect("OFF_TIME back to 2000", chip.off_time == 2000);
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1500);
	powerfail_suo_remove(&pdev);
	expect("after a slider-off the hold is left alone", chip.off_time == 20000);

	printf("== T19 irq-gpios unreadable: recheck forever (residual path) ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	sim_gpio_fail = 1;
	run_until(3000);
	expect("no orderly_poweroff", sim_orderly_calls == 0);
	expect("no backstop", due_of(&drv()->backstop) == 0);
	expect("IRQ stays disabled", sim_irq_enable_calls == 0);
	expect("OFF_TIME left at 20000", chip.off_time == 20000);
	expect("check still re-arming", due_of(&drv()->check) > 3000);

	printf("== T20 spurious falling edge with the slider on: no poweroff, READY untouched ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	fire_irq();                      /* line stays high */
	run_until(1500);
	expect("no orderly_poweroff", sim_orderly_calls == 0);
	expect("IRQ re-enabled", sim_irq_enabled == 1);
	expect("READY not rewritten (already 1)", sim_chip_ready_writes == 0);

	printf("== T21 quick flick back on inside the debounce: no poweroff, no READY write ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1050);
	set_switch(1);                   /* still in debounce, countdown never starts */
	run_until(1500);
	expect("no orderly_poweroff", sim_orderly_calls == 0);
	expect("IRQ re-enabled", sim_irq_enabled == 1);
	expect("READY was never cleared, so no write", sim_chip_ready_writes == 0);

	printf("== T22 state read fails at the check: treated as confirmed ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	sim_state_read_fail = 1;
	run_until(1500);
	expect("orderly_poweroff once", sim_orderly_calls == 1);
	expect("OFF_TIME 20000", chip.off_time == 20000);
	sim_state_read_fail = 0;

	printf("== T23 .shutdown without a power controller leaves the chip alone ==\n");
	reset_all();
	sim_has_power_ctrl = 0;
	sim_has_disabled_gpios = 0;
	do_probe();
	system_state = SYSTEM_POWER_OFF;
	powerfail_suo_shutdown(&pdev);
	expect("OFF_TIME stays 2000", chip.off_time == 2000);
	expect("no restart", sim_restart_calls == 0);

	printf("== T24 flip back on, IRQ re-armed, second switch-off still works ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1300);
	set_switch(1);                   /* back on before the check */
	run_until(1500);
	expect("first switch-off produced no poweroff", sim_orderly_calls == 0);
	expect("IRQ re-armed", sim_irq_enabled == 1 && sim_irq_enable_calls == 1);
	jiffies = 3000;
	set_switch(0);                   /* second, real switch-off */
	run_until(3500);
	expect("second switch-off runs orderly_poweroff", sim_orderly_calls == 1);
	expect("backstop due 19000", due_of(&drv()->backstop) == 19000);

	printf("== T25 flip back on while the poweroff is hung: no restart point ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1500);
	expect("orderly poweroff started", sim_orderly_calls == 1);
	run_until(8000);
	set_switch(1);                   /* user flips back on; userspace never finishes */
#ifdef PROPOSED_BUILD
	restart_jb_valid = 1;
	if (setjmp(restart_jb) == 0)
		run_until(22000);
	expect("backstop restarts once the line is high", sim_restart_calls == 1);
	expect("S + U before the restart", sim_sysrq_len == 2 &&
	       sim_sysrq_seq[0] == 's' && sim_sysrq_seq[1] == 'u');
	expect("restart after the RO remount, jiffies 18000", jiffies >= 18000);
#else
	run_until(22000);
	expect("no .shutdown means no restart", sim_restart_calls == 0);
	expect("backstop ran SysRq S + U", sim_sysrq_len == 2 &&
	       sim_sysrq_seq[0] == 's' && sim_sysrq_seq[1] == 'u');
	chip_advance(22000);
	expect("chip is back at ON, slider holds the boost", chip.state == 1);
	expect("no READY restore (ready work never armed)", sim_chip_ready_writes == 0);
#endif

	printf("== T26 flip back after the backstop: still no restart path ==\n");
	reset_all();
	do_probe();
	run_until(1000);
	set_switch(0);
	run_until(1500);
	expect("orderly poweroff started", sim_orderly_calls == 1);
	run_until(18000);                /* backstop ran S at 17000, U at 18000, line low */
	set_switch(1);                   /* flip after the single backstop sample */
	run_until(22000);
	expect("no restart even with the proposal", sim_restart_calls == 0);
	expect("S + U still ran", sim_sysrq_len == 2 &&
	       sim_sysrq_seq[0] == 's' && sim_sysrq_seq[1] == 'u');
	chip_advance(22000);
	expect("chip back at ON, slider holds the boost", chip.state == 1);
	expect("no READY restore", sim_chip_ready_writes == 0);

	printf("\n%s: %d checks, %d failure(s)\n", fails ? "FAIL" : "PASS", checks, fails);
	return fails ? 1 : 0;
}
