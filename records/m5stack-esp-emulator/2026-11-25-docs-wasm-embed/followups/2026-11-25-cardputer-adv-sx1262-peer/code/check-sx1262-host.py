from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

lab = Path(__file__).resolve().parent
source = (lab / "source/hw/m5stopwatch/m5_sx1262.c").read_text()
core = source[source.index("#define SX1262_MAX_PACKET"):source.index("static const M5SpiSlaveOps sx1262_ops")]
receive = source[source.index("static void sx1262_cap_receive("):source.index("void m5_sx1262_attach_cardputer_adv(")]
shim = r"""
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#define MIN(a,b) ((a)<(b)?(a):(b))
#define g_autofree
#define QEMU_CLOCK_VIRTUAL 0
typedef struct { int64_t deadline; } QEMUTimer;
typedef struct {} M5SpiSlaveOps;
typedef struct {} Object;
typedef struct { char *text; } Visitor;
typedef struct { const char *message; } Error;
static bool levels[8];
static int64_t now;
static void esp32_gpio_set_input(int pin,bool value) { assert(pin<8); levels[pin]=value; }
static int64_t qemu_clock_get_ns(int unused) { return now; }
static void timer_mod_ns(QEMUTimer *timer,int64_t deadline) { timer->deadline=deadline; }
static void timer_del(QEMUTimer *timer) { timer->deadline=0; }
static bool visit_type_str(Visitor *v,const char *name,char **out,Error **errp) { *out=v->text; return true; }
static void error_setg(Error **errp,const char *message) {
    static Error error; error.message=message; *errp=&error;
}
static unsigned ldl_be_p(const uint8_t *b) {
    return (unsigned)b[0]<<24|(unsigned)b[1]<<16|(unsigned)b[2]<<8|b[3];
}
static int g_ascii_xdigit_value(char c) {
    if(c>='0'&&c<='9')return c-'0';
    c=tolower((unsigned char)c);
    return c>='a'&&c<='f'?c-'a'+10:-1;
}
"""
test = r"""
static void advance(M5Sx1262State *s,int64_t ns) {
    now+=ns;
    if(s->busy_timer->deadline>0&&now>=s->busy_timer->deadline) {
        timer_del(s->busy_timer); sx1262_cap_busy_ready(s);
    }
    if(s->tx_timer->deadline>0&&now>=s->tx_timer->deadline) {
        timer_del(s->tx_timer); sx1262_cap_complete_tx(s);
    }
}
static void command(M5Sx1262State *s,const uint8_t *bytes,uint8_t *reply,size_t length) {
    assert(!levels[ADV_SX1262_BUSY]);
    sx1262_set_cs(s,0);
    for(size_t index=0;index<length;index++)reply[index]=sx1262_transfer(s,bytes[index]);
    sx1262_set_cs(s,1);
    assert(levels[ADV_SX1262_BUSY]);
    advance(s,100000);
    assert(!levels[ADV_SX1262_BUSY]);
}
#define CMD(...) do { const uint8_t data[]={__VA_ARGS__}; command(&s,data,response,sizeof(data)); } while(0)
int main(void) {
    uint8_t registers[65536]={0}, response[32];
    QEMUTimer busy={0},tx={0};
    M5Sx1262State s={.cap=true,.cap_registers=registers,.busy_timer=&busy,.tx_timer=&tx};
    sx1262_cap_machine_reset(&s,3,1);
    sx1262_cap_reset_pin(&s,3,0);
    assert(levels[6] && s.reset_edges==1);
    sx1262_cap_reset_pin(&s,3,1);
    advance(&s,1000000);
    assert(!levels[6] && !s.reset);
    CMD(0x12,0,0,0);
    assert(response[1]==0x20 && response[2]==0 && response[3]==0);
    CMD(0x0d,7,0x40,0x14,0x24);
    CMD(0x1d,7,0x40,0,0,0);
    assert(response[4]==0x14 && response[5]==0x24);
    CMD(0x08,0,3,0,3,0,0,0,0);
    CMD(0x86,0x36,0x40,0,0);
    assert(s.frequency==0x36400000);
    CMD(0x0e,0,'w','a','s','m');
    CMD(0x83,0,0,0);
    assert(s.tx_pending && !s.tx_sequence && !levels[4] && !s.rx_len);
    advance(&s,1000000);
    assert(!s.tx_pending && s.tx_sequence==1 && levels[4] && !s.rx_len);
    assert(s.committed_len==4&&!memcmp(s.committed_tx,"wasm",4));
    CMD(0x02,0xff,0xff);
    assert(!levels[4]);
    Visitor packet={.text="7761736d"};
    Error *err=NULL;
    sx1262_cap_receive(NULL,&packet,"rx-packet",&s,&err);
    assert(err&&!s.rx_sequence);
    CMD(0x82,0xff,0xff,0xff);
    assert(s.receiving&&s.continuous&&!s.rx_sequence&&!levels[4]);
    err=NULL; packet.text="77zz";
    sx1262_cap_receive(NULL,&packet,"rx-packet",&s,&err);
    assert(err&&!s.rx_sequence);
    err=NULL; packet.text="7761736d";
    sx1262_cap_receive(NULL,&packet,"rx-packet",&s,&err);
    assert(!err&&s.rx_sequence==1&&levels[4]);
    CMD(0x12,0,0,0);
    assert(response[3]==SX1262_RX_DONE);
    CMD(0x13,0,0,0);
    assert(response[2]==4 && response[3]==0);
    CMD(0x1e,0,0,0,0,0,0);
    assert(!memcmp(response+3,"wasm",4)&&s.rx_bytes_read==4);
    CMD(0x02,0xff,0xff);
    assert(!levels[4]);
    CMD(0x80,0);
    assert(!s.receiving);
    puts("SX1262_CARDPUTER_ADV_HOST_OK busy/reset/SPI/TX/DIO1/explicit_RX");
}
"""
with TemporaryDirectory(dir=lab) as directory:
    path = Path(directory)
    model = path / "sx1262.c"
    program = path / "check"
    model.write_text(shim + core + receive + test)
    subprocess.run(["clang", "-std=c11", "-Wall", "-Werror", str(model), "-o", str(program)], check=True)
    subprocess.run([str(program)], check=True)
