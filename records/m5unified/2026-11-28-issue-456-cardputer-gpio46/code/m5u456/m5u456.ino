// Reproduce check for m5stack/M5Unified#456 on Cardputer ADV.
// After M5.begin(), GPIO46 must not remain output-enabled (it is the ES8311 ASDOUT).
#include <M5Unified.h>
#include <soc/gpio_reg.h>

static void dump46(const char* tag)
{
  uint32_t en1  = REG_READ(GPIO_ENABLE1_REG);
  uint32_t out1 = REG_READ(GPIO_OUT1_REG);
  uint32_t in1  = REG_READ(GPIO_IN1_REG);
  printf("M5U456 %s EN1=%08lx OUT1=%08lx IN1=%08lx en46=%lu out46=%lu in46=%lu board=%d\n",
         tag, (unsigned long)en1, (unsigned long)out1, (unsigned long)in1,
         (unsigned long)((en1 >> 14) & 1), (unsigned long)((out1 >> 14) & 1),
         (unsigned long)((in1 >> 14) & 1), (int)M5.getBoard());
}

static void recordStats(const char* tag)
{
  static int16_t buf[512];
  for (auto& s : buf) { s = 0; }
  if (!M5.Mic.record(buf, 512, 16000)) {
    printf("M5U456 mic-%s record-start-failed enabled=%d\n", tag, (int)M5.Mic.isEnabled());
    return;
  }
  uint32_t t0 = millis();
  while (M5.Mic.isRecording() && (millis() - t0) < 3000) { delay(1); }
  int16_t mn = 32767, mx = -32768;
  uint32_t changes = 0;
  for (size_t i = 0; i < 512; ++i) {
    if (buf[i] < mn) mn = buf[i];
    if (buf[i] > mx) mx = buf[i];
    if (i && buf[i] != buf[i - 1]) { ++changes; }
  }
  printf("M5U456 mic-%s first=%d %d %d %d min=%d max=%d changes=%lu\n",
         tag, buf[0], buf[1], buf[2], buf[3], (int)mn, (int)mx, (unsigned long)changes);
}

void setup()
{
  Serial0.begin(115200, SERIAL_8N1, -1, 1);
  delay(100);
  printf("M5U456 boot\n");

  auto cfg = M5.config();
  M5.begin(cfg);
  delay(200);

  dump46("after-begin");

  M5.Speaker.end();
  M5.Mic.begin();
  printf("M5U456 mic-enabled=%d\n", (int)M5.Mic.isEnabled());
  recordStats("output46");
  dump46("after-mic-begin");

  // Workaround from the issue: release GPIO46 back to input.
  gpio_set_direction(GPIO_NUM_46, GPIO_MODE_INPUT);
  delay(50);
  dump46("after-set-input");
  recordStats("input46");
  dump46("final");

  printf("M5U456 done\n");
}

void loop()
{
  delay(1000);
}
