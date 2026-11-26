/*
 * Host-level harness for modules/CardputerZero/powerfail_suo.c (PR #20).
 * Compiles the driver's real source against stub kernel headers and drives it
 * against a simulated M5IOE1 register file. Time is simulated: msleep() only
 * advances jiffies, so delays are deterministic.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

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

/* ---------------- simulation state ---------------- */
unsigned long jiffies;
int system_state;
int sim_irq_level = 0;
int sim_ioe_present = 1;
int sim_has_power_ctrl = 1;
int sim_has_disabled_gpios = 1;
int sim_disabled_is_m5ioe1 = 1;
int sim_prop_debounce_ms = 500;
int sim_prop_power_hold_ms = -1;
int sim_i2c_write_fail = 0;
int sim_i2c_read_fail = 0;
u16 sim_off_time_reg = 2000;
int sim_power_state_seq[8] = {1};
int sim_power_state_len = 1;
int sim_power_state_idx = 0;
int sim_orderly_calls = 0;
int sim_orderly_force = -1;
int sim_sysrq_seq[8];
int sim_sysrq_len = 0;
int sim_backlight_off = 0;
int sim_disabled_gpio_writes = 0;
int sim_disabled_gpio_value = -1;
int sim_irq_enable_calls = 0;
int sim_irq_disable_calls = 0;
int sim_work_pending = 0;
int sim_backstop_armed = 0;
unsigned long sim_backstop_delay = 0;
int sim_work_runs = 0;

static struct i2c_client g_ioe;
static struct gpio_desc g_irq_desc, g_disabled_desc;
static struct backlight_device g_bl;
static struct device_node g_m5ioe1 = { "m5stack,m5ioe1", 1 };
static struct device_node g_other = { "gpio-keys", 2 };
static irq_handler_t g_handler;
static void *g_handler_arg;

void sim_msleep(unsigned int ms) { jiffies += ms; }
int sim_next_power_state(void)
{
	int s = sim_power_state_seq[sim_power_state_idx < sim_power_state_len ?
				    sim_power_state_idx : sim_power_state_len - 1];
	if (sim_power_state_idx < sim_power_state_len)
		sim_power_state_idx++;
	return s;
}

/* ---------------- stub kernel API ---------------- */
struct device_node *of_parse_phandle(const struct device_node *np,
				     const char *name, int index)
{
	(void)np; (void)index;
	if (!strcmp(name, "m5stack,power-controller"))
		return sim_has_power_ctrl ? &g_m5ioe1 : NULL;
	if (!strcmp(name, "disabled-gpios"))
		return sim_has_disabled_gpios ? (sim_disabled_is_m5ioe1 ? &g_m5ioe1 : &g_other) : NULL;
	return NULL;
}
void of_node_put(struct device_node *np) { (void)np; }
int of_device_is_compatible(const struct device_node *np, const char *c)
{ return np && !strcmp(np->compatible, c); }
int of_property_read_u32(const struct device_node *np, const char *name, u32 *out)
{
	(void)np;
	if (!strcmp(name, "debounce-ms") && sim_prop_debounce_ms >= 0) {
		*out = sim_prop_debounce_ms; return 0;
	}
	if (!strcmp(name, "power-hold-ms") && sim_prop_power_hold_ms >= 0) {
		*out = sim_prop_power_hold_ms; return 0;
	}
	return -EINVAL;
}
struct i2c_client *of_find_i2c_device_by_node(struct device_node *node)
{ return (node == &g_m5ioe1 && sim_ioe_present) ? &g_ioe : NULL; }

s32 i2c_smbus_write_i2c_block_data(const struct i2c_client *c, u8 cmd,
				   u8 len, const u8 *values)
{
	(void)c;
	if (sim_i2c_write_fail)
		return -EIO;
	if (cmd == 0xB2 && len == 2)
		sim_off_time_reg = (u16)(values[0] | (values[1] << 8));
	return 0;
}
s32 i2c_smbus_read_word_data(const struct i2c_client *c, u8 cmd)
{
	(void)c;
	if (sim_i2c_read_fail)
		return -EIO;
	if (cmd == 0xB2)
		return sim_off_time_reg;
	return -EIO;
}
s32 i2c_smbus_read_byte_data(const struct i2c_client *c, u8 cmd)
{
	(void)c;
	if (sim_i2c_read_fail)
		return -EIO;
	if (cmd == 0xB6)
		return sim_next_power_state();
	return -EIO;
}

struct gpio_desc *devm_gpiod_get(struct device *dev, const char *con, enum gpiod_flags f)
{ (void)dev; (void)con; (void)f; return &g_irq_desc; }
struct gpio_desc *devm_gpiod_get_optional(struct device *dev, const char *con, enum gpiod_flags f)
{ (void)dev; (void)con; (void)f; return sim_has_disabled_gpios ? &g_disabled_desc : NULL; }
int gpiod_get_raw_value_cansleep(const struct gpio_desc *d) { (void)d; return sim_irq_level; }
void gpiod_set_value_cansleep(struct gpio_desc *d, int val)
{ (void)d; sim_disabled_gpio_writes++; sim_disabled_gpio_value = val; }

int devm_request_irq(struct device *dev, unsigned int irq, irq_handler_t h,
		     unsigned long flags, const char *name, void *arg)
{ (void)dev; (void)irq; (void)flags; (void)name; g_handler = h; g_handler_arg = arg; return 0; }
void disable_irq_nosync(unsigned int irq) { (void)irq; sim_irq_disable_calls++; }
void enable_irq(unsigned int irq) { (void)irq; sim_irq_enable_calls++; }

void orderly_poweroff(bool force) { sim_orderly_calls++; sim_orderly_force = force; }
void handle_sysrq(int key)
{ if (sim_sysrq_len < 8) sim_sysrq_seq[sim_sysrq_len++] = key; }

struct backlight_device *devm_of_find_backlight(struct device *dev) { (void)dev; return &g_bl; }
void backlight_device_set_brightness(struct backlight_device *bd, int v)
{ (void)bd; if (v == 0) sim_backlight_off++; }

bool schedule_work(struct work_struct *w) { (void)w; sim_work_pending = 1; return true; }
bool schedule_delayed_work(struct delayed_work *w, unsigned long delay)
{ (void)w; sim_backstop_armed = 1; sim_backstop_delay = delay; return true; }
bool cancel_work_sync(struct work_struct *w) { (void)w; sim_work_pending = 0; return true; }
bool cancel_delayed_work_sync(struct delayed_work *w) { (void)w; sim_backstop_armed = 0; return true; }

int platform_get_irq(struct platform_device *pdev, unsigned int n) { (void)pdev; (void)n; return 185; }
void *platform_get_drvdata(struct platform_device *pdev) { return pdev->drvdata; }
void platform_set_drvdata(struct platform_device *pdev, void *data) { pdev->drvdata = data; }

/* ---------------- the driver under test ---------------- */
#ifndef DRIVER_SRC
#define DRIVER_SRC "powerfail_suo.c"
#endif
#include DRIVER_SRC

/* ---------------- scenarios ---------------- */
static struct platform_device pdev = { .dev = { .of_node = (struct device_node *)&g_m5ioe1,
						.name = "powerfail" } };
static struct powerfail_suo_data *drvdata(void) { return pdev.drvdata; }

static void reset_sim(void)
{
	jiffies = 0;
	system_state = SYSTEM_BOOT;
	sim_irq_level = 0;
	sim_ioe_present = 1;
	sim_has_power_ctrl = 1;
	sim_has_disabled_gpios = 1;
	sim_disabled_is_m5ioe1 = 1;
	sim_prop_debounce_ms = 500;
	sim_prop_power_hold_ms = -1;
	sim_i2c_write_fail = 0;
	sim_i2c_read_fail = 0;
	sim_off_time_reg = 2000;
	sim_power_state_seq[0] = 1;
	sim_power_state_len = 1;
	sim_power_state_idx = 0;
	sim_orderly_calls = 0;
	sim_orderly_force = -1;
	sim_sysrq_len = 0;
	sim_backlight_off = 0;
	sim_disabled_gpio_writes = 0;
	sim_disabled_gpio_value = -1;
	sim_irq_enable_calls = 0;
	sim_irq_disable_calls = 0;
	sim_work_pending = 0;
	sim_backstop_armed = 0;
	sim_backstop_delay = 0;
	sim_work_runs = 0;
	memset(&pdev, 0, sizeof(pdev));
	pdev.dev.of_node = (struct device_node *)&g_m5ioe1;
	pdev.dev.name = "powerfail";
}

static void set_states(const int *s, int n)
{
	memcpy(sim_power_state_seq, s, sizeof(int) * n);
	sim_power_state_len = n;
	sim_power_state_idx = 0;
}

/* fire the IRQ like the gpio controller would, then run the queued work */
static void fire_slider_off(void)
{
	sim_irq_level = 0;
	if (g_handler)
		g_handler(185, g_handler_arg);
	if (sim_work_pending && drvdata() && drvdata()->work.func) {
		sim_work_pending = 0;
		sim_work_runs++;
		drvdata()->work.func(&drvdata()->work);
	}
}

static void run_backstop(void)
{
	if (drvdata() && drvdata()->backstop.work.func)
		drvdata()->backstop.work.func(&drvdata()->backstop.work);
}

static int fails;

static void check(const char *name, int cond, const char *what)
{
	printf("  %-42s %s  %s\n", name, cond ? "PASS" : "FAIL", what);
	if (!cond)
		fails++;
}

int main(void)
{
	int r;
	const int s_deb_then_count[] = { 2, 3 };
	const int s_deb_stuck[] = { 2, 2 };
	const int s_on[] = { 1 };
	const int s_counting[] = { 3 };

	printf("== S1 probe, no power-hold-ms: default hold programmed ==\n");
	reset_sim();
	r = powerfail_suo_probe(&pdev);
	check("probe_return", r == 0, "expect 0");
	check("off_time_reg_written", sim_off_time_reg == 20000, "OFF_TIME 0xB2/0xB3 = 20000");
	check("hold_default", drvdata() && drvdata()->hold_ms == 20000, "hold_ms = 20000");

	printf("== S2 probe, no power controller: legacy path only ==\n");
	reset_sim();
	sim_has_power_ctrl = 0;
	sim_has_disabled_gpios = 0;
	r = powerfail_suo_probe(&pdev);
	check("probe_return", r == 0, "expect 0");
	check("ioe_null", drvdata() && drvdata()->ioe == NULL, "data->ioe stays NULL");
	check("off_time_untouched", sim_off_time_reg == 2000, "stock 2000 ms untouched");

	printf("== S3 probe, phandle present but i2c client absent ==\n");
	reset_sim();
	sim_ioe_present = 0;
	r = powerfail_suo_probe(&pdev);
	check("probe_defer", r == -EPROBE_DEFER, "returns -EPROBE_DEFER");

	printf("== S4 slider off, debounce -> countdown: orderly poweroff ==\n");
	reset_sim();
	set_states(s_deb_then_count, 2);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
	check("confirmed", sim_orderly_calls == 1, "orderly_poweroff() called once");
	check("force_arg", sim_orderly_force == 1, "force = true");
	check("off_time_reprogrammed", sim_off_time_reg == 20000, "OFF_TIME = 20000 at the event");
	check("backstop_armed", sim_backstop_armed == 1, "backstop armed");
	check("backstop_at_16s", sim_backstop_delay == 16000 - 650,
	      "delay = 16000 ms - 650 ms elapsed (fires 16.0 s after the flip)");
	check("backlight_off", sim_backlight_off == 1, "backlight 0 before userspace stop");

	printf("== S5 slider off but 0xB6 still reads DEBOUNCE(2) on the retry ==\n");
	reset_sim();
	set_states(s_deb_stuck, 2);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
#ifdef FIXED_BUILD
	check("event_handled", sim_orderly_calls == 1, "orderly_poweroff called for DEBOUNCE(2)");
	check("backstop_armed", sim_backstop_armed == 1, "backstop armed");
#else
	check("event_dropped", sim_orderly_calls == 0, "no orderly_poweroff");
	check("hold_left_long", sim_off_time_reg == 20000, "OFF_TIME stays 20000, not restored to stock");
	check("backstop_not_armed", sim_backstop_armed == 0, "no backstop for a dropped event");
	check("irq_reenabled", sim_irq_enable_calls == 1 && sim_irq_level == 0,
	      "IRQ re-enabled while irq-gpios is still low");
#endif

	printf("== S5b dropped event leaves the hold armed (state ON(1)) ==\n");
	reset_sim();
	set_states(s_on, 1);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
#ifdef FIXED_BUILD
	check("hold_restored", sim_off_time_reg == 2000, "OFF_TIME restored to 2000 on the drop path");
#else
	check("hold_left_long", sim_off_time_reg == 20000, "OFF_TIME stays 20000 on the drop path");
#endif

	printf("== S6 spurious edge, power state ON(1): event dropped (intended) ==\n");
	reset_sim();
	set_states(s_on, 1);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
	check("event_dropped", sim_orderly_calls == 0, "no orderly_poweroff");
#ifdef FIXED_BUILD
	check("hold_restored", sim_off_time_reg == 2000, "OFF_TIME restored to 2000 on the drop path");
#else
	check("hold_left_long", sim_off_time_reg == 20000, "OFF_TIME stays 20000");
#endif

	printf("== S7 cannot program OFF_TIME at the event: legacy fallback ==\n");
	reset_sim();
	set_states(s_counting, 1);
	powerfail_suo_probe(&pdev);
	sim_i2c_write_fail = 1;
	fire_slider_off();
	check("legacy_sysrq", sim_sysrq_len == 1 && sim_sysrq_seq[0] == 'u', "SysRq U executed");
	check("legacy_disabled_gpio", sim_disabled_gpio_writes == 1, "disabled-gpios asserted");
	check("no_orderly", sim_orderly_calls == 0, "no orderly_poweroff");

	printf("== S8 .shutdown on poweroff after slider-off: 200 ms cut ==\n");
	reset_sim();
	set_states(s_deb_then_count, 2);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
	system_state = SYSTEM_POWER_OFF;
	powerfail_suo_shutdown(&pdev);
	check("short_off_time", sim_off_time_reg == 200, "OFF_TIME = 200 ms");
	check("backstop_cancelled", sim_backstop_armed == 0, "backstop cancelled");
	check("lcd_reset_asserted", sim_disabled_gpio_value == 1, "disabled-gpios asserted");

	printf("== S9 .shutdown on reboot: OFF_TIME untouched ==\n");
	reset_sim();
	set_states(s_deb_then_count, 2);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
	system_state = SYSTEM_RESTART;
	powerfail_suo_shutdown(&pdev);
	check("reboot_skips", sim_off_time_reg == 20000, "OFF_TIME stays 20000 on reboot");

	printf("== S10 .shutdown on menu poweroff (slider still on) ==\n");
	reset_sim();
	powerfail_suo_probe(&pdev);
	system_state = SYSTEM_POWER_OFF;
	powerfail_suo_shutdown(&pdev);
	check("short_off_time", sim_off_time_reg == 200, "OFF_TIME = 200 ms");
	check("lcd_reset_untouched", sim_disabled_gpio_writes == 0, "disabled-gpios not asserted");

	printf("== S11 remove: restore stock hold ==\n");
	reset_sim();
	powerfail_suo_probe(&pdev);
	powerfail_suo_remove(&pdev);
	check("restored", sim_off_time_reg == 2000, "OFF_TIME back to 2000");

	printf("== S12 power-hold-ms = 8000 (allowed minimum) ==\n");
	reset_sim();
	sim_prop_power_hold_ms = 8000;
	set_states(s_counting, 1);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
	check("hold_8000", drvdata()->hold_ms == 8000, "hold_ms = 8000");
	check("backstop_4s", sim_backstop_delay == 4000 - 500,
	      "backstop fires 4.0 s after the flip, healthy shutdown took ~4.9 s");

	printf("== S13 power-hold-ms = 4000: clamped to the minimum ==\n");
	reset_sim();
	sim_prop_power_hold_ms = 4000;
	powerfail_suo_probe(&pdev);
	check("clamped", drvdata()->hold_ms == 8000, "hold_ms clamped to 8000");

	printf("== S14 backstop body: SysRq S, 1 s, SysRq U ==\n");
	reset_sim();
	set_states(s_deb_then_count, 2);
	powerfail_suo_probe(&pdev);
	fire_slider_off();
	run_backstop();
	check("sysrq_su", sim_sysrq_len == 2 && sim_sysrq_seq[0] == 's' && sim_sysrq_seq[1] == 'u',
	      "S then U");

	printf("\n%s: %d failure(s)\n", fails ? "FAIL" : "PASS", fails);
	return fails ? 1 : 0;
}
