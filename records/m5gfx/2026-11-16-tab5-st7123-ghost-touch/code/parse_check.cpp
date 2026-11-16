// Host-side reproduction of Touch_ST7123::getTouchRaw() parsing, copied from
// M5GFX 28d4794 src/lgfx/v1/platforms/esp32p4/Touch_ST7123.inl:109-157.
#include <cstdint>
#include <cstddef>
#include <cstdio>
#include <cstring>

struct touch_point_t { int16_t x = -1; int16_t y = -1; uint16_t size = 0; uint16_t id = 0; };

struct touch_report_t {
    uint8_t x_h: 6;
    uint8_t reserved_6: 1;
    uint8_t valid: 1;
    uint8_t x_l;
    uint8_t y_h;
    uint8_t y_l;
    uint8_t area;
    uint8_t intensity;
    uint8_t reserved_49_55;
};

static constexpr uint8_t kMaxPoints = 10;
static constexpr uint8_t kCount = 5;   // M5Unified TOUCH_MAX_POINTS

enum rule_t { RULE_NONE, RULE_AREA_INTENSITY, RULE_INTENSITY_ONLY };

static int parse(touch_point_t* tp, const touch_report_t* r, uint8_t max_touches, rule_t rule)
{
    int valid_count = 0;
    for (uint8_t i = 0; i < max_touches; i++) {
        if (!r[i].valid) continue;
        if (rule == RULE_AREA_INTENSITY && !(r[i].area >= 30 && r[i].intensity < 25)) { /* keep */ }
        else if (rule == RULE_AREA_INTENSITY) continue;
        if (rule == RULE_INTENSITY_ONLY && r[i].intensity < 25) continue;
        tp[valid_count].id = i;
        tp[valid_count].x = (uint16_t)(r[i].x_h << 8 | r[i].x_l);
        tp[valid_count].y = (uint16_t)(r[i].y_h << 8 | r[i].y_l);
        tp[valid_count].size = r[i].area;
        if (++valid_count >= kCount) break;
    }
    return valid_count;
}

static void dump(const char* name, int n, const touch_point_t* tp)
{
    printf("%s: %d point(s)\n", name, n);
    for (int i = 0; i < n; i++)
        printf("  id=%u x=%d y=%d area(size)=%u intensity=<not in touch_point_t>\n",
               tp[i].id, tp[i].x, tp[i].y, tp[i].size);
}

int main()
{
    printf("sizeof(touch_report_t)=%zu offsetof(intensity)=%zu offsetof(area)=%zu\n",
           sizeof(touch_report_t), offsetof(touch_report_t, intensity), offsetof(touch_report_t, area));

    touch_report_t frame[kMaxPoints] = {};
    // Ghost frame measured by the reporter: one point on each long edge, same height.
    frame[0].valid = 1; frame[0].x_h = 0;   frame[0].x_l = 0;   frame[0].y_h = 2; frame[0].y_l = 123; frame[0].area = 34; frame[0].intensity = 18;
    frame[1].valid = 1; frame[1].x_h = 2;   frame[1].x_l = 207; frame[1].y_h = 2; frame[1].y_l = 121; frame[1].area = 36; frame[1].intensity = 18;
    touch_point_t tp[kCount];
    int n = parse(tp, frame, 10, RULE_NONE); dump("driver as shipped, ghost frame", n, tp);
    n = parse(tp, frame, 10, RULE_AREA_INTENSITY);      dump("area>=30&&intensity<25 filter, same frame", n, tp);

    touch_report_t tap[kMaxPoints] = {};
    tap[0].valid = 1; tap[0].x_h = 1; tap[0].x_l = 94; tap[0].y_h = 1; tap[0].y_l = 244; tap[0].area = 8; tap[0].intensity = 45;
    n = parse(tp, tap, 10, RULE_AREA_INTENSITY); dump("real tap (area 8, intensity 45) under same filter", n, tp);

    touch_report_t narrow[kMaxPoints] = {};
    narrow[0].valid = 1; narrow[0].x_h = 0; narrow[0].x_l = 0; narrow[0].y_h = 0; narrow[0].y_l = 58; narrow[0].area = 1; narrow[0].intensity = 10;
    n = parse(tp, narrow, 10, RULE_NONE); dump("narrow ghost (area 1, intensity 10), driver as shipped", n, tp);
    n = parse(tp, narrow, 10, RULE_INTENSITY_ONLY);  dump("narrow ghost under intensity<25 rule", n, tp);
    return 0;
}
