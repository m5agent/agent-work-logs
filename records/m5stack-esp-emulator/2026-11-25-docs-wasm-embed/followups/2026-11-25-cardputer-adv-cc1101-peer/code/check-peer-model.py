"""Compile and run the actual CC1101 state/transfer functions with host stubs."""
from pathlib import Path
import re
from subprocess import run
from tempfile import TemporaryDirectory

lab = Path(__file__).resolve().parent
source_file = lab / 'peer-source/modified/hw/m5stopwatch/m5_cc1101_spi.c'
source = source_file.read_text().split('static void cc1101_peer_get_state', 1)[0]
source = re.sub(r'^#include ".*"\n', '', source, flags=re.MULTILINE)

prelude = r'''
#include <assert.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define g_new0(T, n) ((T *)calloc((n), sizeof(T)))
#define QEMU_CLOCK_VIRTUAL 0
#define QEMU_CLOCK_REALTIME 1
typedef struct {
    void (*set_cs)(void *, int);
    uint8_t (*transfer)(void *, uint8_t);
} M5SpiSlaveOps;
typedef struct {
    const M5SpiSlaveOps *ops;
    void *opaque;
    int cs_pin;
} DeviceState;
typedef struct {
    int clock;
    int64_t deadline;
    bool pending;
    void (*callback)(void *);
    void *opaque;
} QEMUTimer;
static int64_t clocks[] = {100,1000};
static int pin_levels[64];
static void esp32_gpio_force_line(int pin, int level) {pin_levels[pin] = level;}
static void esp32_gpio_set_input(int pin, int level) {pin_levels[pin] = level;}
static int64_t qemu_clock_get_ms(int clock) {return clocks[clock];}
static QEMUTimer *timer_new_ms(int clock, void (*fn)(void *), void *opaque) {
    QEMUTimer *timer = calloc(1,sizeof(*timer));
    timer->clock = clock;
    timer->callback = fn;
    timer->opaque = opaque;
    return timer;
}
static void timer_mod(QEMUTimer *timer, int64_t deadline) {
    timer->pending = true;
    timer->deadline = deadline;
}
static void timer_del(QEMUTimer *timer) {timer->pending = false;}
static void run_timer(QEMUTimer *timer) {
    assert(timer->pending && timer->deadline <= clocks[timer->clock]);
    timer->pending = false;
    timer->callback(timer->opaque);
}
static void esp32s3_gpspi_attach_spi_slave_passive_cs(DeviceState *dev,
              const M5SpiSlaveOps *ops, void *state, int pin) {
    dev->ops = ops;
    dev->opaque = state;
    dev->cs_pin = pin;
}
'''
cases = r'''
static void strobe(DeviceState *spi, uint8_t command) {
    spi->ops->set_cs(spi->opaque, 0);
    assert(spi->ops->transfer(spi->opaque, command) == 0);
    spi->ops->set_cs(spi->opaque, 1);
}
static uint8_t read_status(DeviceState *spi, uint8_t reg) {
    spi->ops->set_cs(spi->opaque, 0);
    assert(spi->ops->transfer(spi->opaque, 0xc0 | reg) == 0);
    uint8_t value = spi->ops->transfer(spi->opaque, 0);
    spi->ops->set_cs(spi->opaque, 1);
    return value;
}
static void write_frame(DeviceState *spi, const uint8_t *frame, size_t length) {
    spi->ops->set_cs(spi->opaque, 0);
    assert(spi->ops->transfer(spi->opaque, 0x7f) == 0);
    for (size_t i=0; i<length; ++i) assert(spi->ops->transfer(spi->opaque,frame[i]) == 0);
    spi->ops->set_cs(spi->opaque, 1);
}
static void read_frame(DeviceState *spi, const uint8_t *frame, size_t length) {
    spi->ops->set_cs(spi->opaque, 0);
    assert(spi->ops->transfer(spi->opaque, 0xff) == 0);
    for (size_t i=0; i<length; ++i) assert(spi->ops->transfer(spi->opaque,0) == frame[i]);
    assert(spi->ops->transfer(spi->opaque,0) == 0x80);
    assert(spi->ops->transfer(spi->opaque,0) == 0x80);
    assert(spi->ops->transfer(spi->opaque,0) == 0);
    spi->ops->set_cs(spi->opaque, 1);
}
int main(void) {
    DeviceState tx_spi={0}, rx_spi={0}, native_spi={0};
    M5Cc1101SpiState *tx = cc1101_attach(&tx_spi,5,15,true);
    M5Cc1101SpiState *rx = cc1101_attach(&rx_spi,5,16,true);
    m5_cc1101_spi_attach(&native_spi,5,17);
    M5Cc1101SpiState *native = native_spi.opaque;
    const uint8_t frame[] = "\x14" "CC1101, SEQ=0, Hello";
    const size_t size = sizeof(frame)-1;

    assert(size == 21 && tx_spi.cs_pin == 5 && rx_spi.cs_pin == 5);
    assert(!cc1101_peer_receive(rx,frame,size));
    assert(read_status(&tx_spi,0x31)==0x14 && read_status(&rx_spi,0x35)==1);
    strobe(&rx_spi,0x34); /* SRX */
    assert(cc1101_peer_rx_armed(rx));
    assert(!rx->packet_ready && !rx->rx_timer->pending && !pin_levels[16]);
    assert(!cc1101_peer_receive(rx,frame,1));
    assert(!cc1101_peer_receive(rx,frame,size-1));
    assert(!cc1101_peer_receive(rx,frame,65));

    strobe(&tx_spi,0x31); /* SFSTXON */
    assert(read_status(&tx_spi,0x35)==0x12);
    write_frame(&tx_spi,frame,size);
    strobe(&tx_spi,0x35); /* STX */
    assert(tx->peer_tx_sequence == 0 && tx->peer_tx_len == 0);
    for (unsigned i=0; i<3; i++) assert(read_status(&tx_spi,0x35)==0x13);
    assert(read_status(&tx_spi,0x35)==1);
    assert(tx->peer_tx_sequence==1 && tx->peer_tx_len==size);
    assert(memcmp(tx->peer_tx_frame,frame,size)==0);

    strobe(&tx_spi,0x34); /* TX wrapper may enter RX afterward. */
    assert(cc1101_peer_rx_armed(tx) && !tx->rx_timer->pending);
    assert(cc1101_peer_receive(rx,tx->peer_tx_frame,tx->peer_tx_len));
    assert(rx->rx_timer->clock==QEMU_CLOCK_VIRTUAL && rx->rx_timer->deadline==105);
    assert(!cc1101_peer_receive(rx,frame,size));
    assert(!pin_levels[16] && rx->peer_rx_interrupts==0);
    clocks[QEMU_CLOCK_VIRTUAL]=105;
    run_timer(rx->rx_timer);
    assert(pin_levels[16] && rx->peer_gdo0 && rx->peer_rx_interrupts==1);
    assert(read_status(&rx_spi,0x3b)==size+2);
    read_frame(&rx_spi,frame,size);
    assert(rx->peer_rx_fifo_bytes==size+2 && rx->peer_rx_completed==1);

    strobe(&rx_spi,0x3a); /* SFRX */
    assert(cc1101_peer_receive(rx,frame,size));
    strobe(&rx_spi,0x36); /* SIDLE aborts an arrival before dwell. */
    assert(!rx->rx_timer->pending && !pin_levels[16]);
    cc1101_rx_timer(rx);
    assert(rx->peer_rx_interrupts==1 && !rx->packet_ready);
    strobe(&rx_spi,0x34);
    assert(cc1101_peer_receive(rx,frame,size));
    unsigned epoch = rx->peer_reset_epoch;
    strobe(&rx_spi,0x30); /* SRES invalidates old dwell and pending data. */
    assert(rx->peer_reset_epoch==epoch+1 && !rx->rx_timer->pending);
    assert(!rx->packet_ready && !pin_levels[16] && rx->peer_rx_completed==1);
    strobe(&tx_spi,0x30);
    assert(tx->peer_tx_sequence==1 && tx->peer_tx_len==0);

    write_frame(&native_spi,frame,size);
    strobe(&native_spi,0x35);
    assert(!native->peer_enabled && native->air_pending);
    strobe(&native_spi,0x34);
    assert(native->rx_timer->clock==QEMU_CLOCK_REALTIME);
    clocks[QEMU_CLOCK_REALTIME]=native->rx_timer->deadline;
    run_timer(native->rx_timer);
    assert(pin_levels[17]);
    read_frame(&native_spi,frame,size);
    assert(native->peer_rx_completed==0);
    puts("CC1101 peer C PASS: real model SPI TX/RX/CRC, 5 ms virtual dwell, bounded ingress, no seed, reset, native loopback");
}
'''
with TemporaryDirectory(prefix='m5-cc1101-peer-') as tmp:
    path = Path(tmp)
    unit = path / 'controller.c'
    output = path / 'controller'
    unit.write_text(prelude + source + cases)
    run(['clang','-std=c11','-Wall','-Wextra','-Werror',str(unit),'-o',str(output)], check=True)
    run([str(output)], check=True)
