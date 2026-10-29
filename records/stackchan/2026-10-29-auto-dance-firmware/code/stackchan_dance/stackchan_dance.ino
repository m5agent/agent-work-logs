/*
 * StackChan auto-dance firmware
 *
 * Target: StackChan (M5Stack CoreS3 + A180 body)
 * SDK:    M5Stack Arduino board package 3.3.10
 * BSP:    M5StackChan 1.1.1
 *
 * The routine starts automatically after boot and loops. Tap the top touch
 * sensor to restart it. Servo travel is intentionally kept away from the
 * mechanical endpoints.
 */

#include <Arduino.h>
#include <M5StackChan.h>
#include <drivers/FTServo_Arduino/src/SCSCL.h>
#include <utils/settings/settings.h>
#include <math.h>

namespace {

constexpr uint32_t kFrameIntervalMs = 66;
constexpr uint32_t kLedIntervalMs   = 50;
constexpr uint32_t kRoutineMs       = 16000;
constexpr uint32_t kRestartDelayMs  = 650;

// Servo units are 0.1 degree. These bounds stay well inside the body's travel.
constexpr int kYawLeft       = -480;
constexpr int kYawRight      = 480;
constexpr int kPitchLow      = 180;
constexpr int kPitchMid      = 450;
constexpr int kPitchHigh     = 720;
constexpr int kMaxServoSpeed = 900;
constexpr int kServoZeroXDefault = 460;
constexpr int kServoZeroYDefault = 620;
constexpr uint32_t kServoWriteIntervalMs = 50;

enum class Expression : uint8_t {
    Happy,
    Excited,
    Wink,
    Love,
    Cool,
    Finale,
};

struct Cue {
    uint32_t at;
    int yaw;
    int pitch;
    int speed;
    Expression expression;
};

static const Cue kCues[] = {
    {0,     0,          kPitchMid, 300, Expression::Happy},
    {400,   kYawLeft,   kPitchMid, 620, Expression::Excited},
    {800,   0,          kPitchHigh, 700, Expression::Wink},
    {1200,  kYawRight,  kPitchMid, 620, Expression::Love},
    {1600,  kYawLeft,   kPitchLow, 720, Expression::Cool},
    {2000,  kYawRight,  kPitchHigh, 720, Expression::Excited},
    {2400,  0,          kPitchHigh, 820, Expression::Happy},
    {2800,  0,          kPitchLow,  820, Expression::Happy},
    {3200,  kYawLeft,   kPitchMid, 680, Expression::Wink},
    {3600,  kYawRight,  kPitchMid, 680, Expression::Wink},
    {4000,  0,          kPitchMid, 620, Expression::Love},
    {4400,  kYawLeft,   kPitchHigh, 760, Expression::Cool},
    {4800,  kYawRight,  kPitchHigh, 760, Expression::Cool},
    {5200,  kYawLeft,   kPitchLow, 820, Expression::Excited},
    {5600,  kYawRight,  kPitchLow, 820, Expression::Excited},
    {6000,  kYawLeft,   kPitchMid, 700, Expression::Love},
    {6400,  kYawRight,  kPitchMid, 700, Expression::Love},
    {6800,  0,          kPitchMid, 560, Expression::Happy},
    {7200,  kYawLeft,   kPitchHigh, 840, Expression::Excited},
    {7600,  kYawRight,  kPitchHigh, 840, Expression::Excited},
    {8000,  kYawLeft,   kPitchLow, 840, Expression::Wink},
    {8400,  kYawRight,  kPitchLow, 840, Expression::Wink},
    {8800,  0,          kPitchMid, 650, Expression::Love},
    {9200,  0,          kPitchHigh, 700, Expression::Cool},
    {9600,  0,          kPitchLow, 700, Expression::Cool},
    {10000, kYawLeft,   kPitchMid, 760, Expression::Happy},
    {10400, kYawRight,  kPitchMid, 760, Expression::Happy},
    {10800, kYawLeft,   kPitchHigh, 880, Expression::Excited},
    {11200, kYawRight,  kPitchLow, 880, Expression::Excited},
    {11600, 0,          kPitchHigh, 760, Expression::Wink},
    {12000, 0,          kPitchMid, 620, Expression::Love},
    {12400, 0,          kPitchHigh, 820, Expression::Finale},
    {12800, 0,          kPitchLow, 820, Expression::Finale},
    {13200, kYawLeft,   kPitchMid, 900, Expression::Finale},
    {13600, kYawRight,  kPitchMid, 900, Expression::Finale},
    {14000, 0,          kPitchMid, 760, Expression::Excited},
    {14400, 0,          kPitchMid, 560, Expression::Love},
    {14800, 0,          kPitchMid, 460, Expression::Finale},
};

struct Rgb {
    uint8_t r;
    uint8_t g;
    uint8_t b;
};

struct Palette {
    uint16_t background;
    uint16_t panel;
    uint16_t accent;
    uint16_t secondary;
    uint16_t cheek;
};

Expression expression         = Expression::Happy;
uint32_t dance_start_ms       = 0;
uint32_t next_face_ms         = 0;
uint32_t next_led_ms          = 0;
uint32_t next_blink_ms        = 0;
uint32_t blink_end_ms         = 0;
size_t cue_index              = 0;

SCSCL servo_bus;
int servo_zero_x = kServoZeroXDefault;
int servo_zero_y = kServoZeroYDefault;
int current_yaw_raw = 0;
int current_pitch_raw = 0;
int motion_start_yaw_raw = 0;
int motion_start_pitch_raw = 0;
int motion_target_yaw_raw = 0;
int motion_target_pitch_raw = 0;
uint32_t motion_start_ms = 0;
uint32_t motion_duration_ms = 1;
uint32_t next_servo_write_ms = 0;

constexpr uint16_t rgb565(uint8_t r, uint8_t g, uint8_t b)
{
    return static_cast<uint16_t>(((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3));
}

constexpr int kCueCount = static_cast<int>(sizeof(kCues) / sizeof(kCues[0]));

Palette paletteFor(Expression value)
{
    switch (value) {
        case Expression::Excited:
            return {rgb565(18, 10, 42), rgb565(37, 19, 72), rgb565(0, 245, 255),
                    rgb565(255, 54, 188), rgb565(255, 92, 160)};
        case Expression::Wink:
            return {rgb565(12, 18, 42), rgb565(20, 38, 76), rgb565(255, 224, 76),
                    rgb565(71, 230, 255), rgb565(255, 102, 164)};
        case Expression::Love:
            return {rgb565(38, 8, 28), rgb565(70, 14, 48), rgb565(255, 82, 142),
                    rgb565(255, 210, 105), rgb565(255, 72, 130)};
        case Expression::Cool:
            return {rgb565(5, 18, 28), rgb565(7, 32, 50), rgb565(62, 242, 255),
                    rgb565(127, 100, 255), rgb565(43, 127, 151)};
        case Expression::Finale:
            return {rgb565(26, 14, 4), rgb565(58, 31, 8), rgb565(255, 217, 59),
                    rgb565(70, 244, 255), rgb565(255, 116, 117)};
        case Expression::Happy:
        default:
            return {rgb565(8, 28, 22), rgb565(13, 53, 43), rgb565(115, 255, 153),
                    rgb565(255, 213, 78), rgb565(255, 104, 156)};
    }
}

uint16_t scaleColor(uint16_t color, uint8_t percent)
{
    const uint16_t r = ((color >> 11) & 0x1F) * percent / 100;
    const uint16_t g = ((color >> 5) & 0x3F) * percent / 100;
    const uint16_t b = (color & 0x1F) * percent / 100;
    return static_cast<uint16_t>((r << 11) | (g << 5) | b);
}

uint16_t blendColor(uint16_t from, uint16_t to, uint8_t amount)
{
    const int r0 = (from >> 11) & 0x1F;
    const int g0 = (from >> 5) & 0x3F;
    const int b0 = from & 0x1F;
    const int r1 = (to >> 11) & 0x1F;
    const int g1 = (to >> 5) & 0x3F;
    const int b1 = to & 0x1F;
    const int r  = r0 + (r1 - r0) * amount / 255;
    const int g  = g0 + (g1 - g0) * amount / 255;
    const int b  = b0 + (b1 - b0) * amount / 255;
    return static_cast<uint16_t>((r << 11) | (g << 5) | b);
}

uint8_t beatPulse(uint32_t now, uint16_t period_ms)
{
    if (static_cast<int32_t>(now - dance_start_ms) < 0) {
        return 45;
    }
    const uint32_t phase = (now - dance_start_ms) % period_ms;
    if (phase < 90) {
        return static_cast<uint8_t>(255 - phase * 180 / 90);
    }
    return 45;
}

int servoRawForAngle(int zero_pos, int angle)
{
    // SCSCL position resolution is 5/16 degree per tick.
    return constrain(zero_pos + angle * 16 / 50, 0, 1000);
}

void writeServoRaw(int yaw_raw, int pitch_raw)
{
    uint8_t ids[2] = {1, 2};
    uint16_t positions[2] = {
        static_cast<uint16_t>(constrain(yaw_raw, 0, 1000)),
        static_cast<uint16_t>(constrain(pitch_raw, 0, 1000)),
    };
    uint16_t times[2] = {0, 0};
    uint16_t speeds[2] = {0, 0};

    servo_bus.SyncWritePos(ids, 2, positions, times, speeds);
    current_yaw_raw = positions[0];
    current_pitch_raw = positions[1];
}

void initDirectServoControl()
{
    // M5StackChan.begin() already installed UART1. A second driver install
    // would replace the board-owned bus, so reuse the configured port.
    servo_bus.uart_num = UART_NUM_1;
    servo_bus.IOTimeOut = 10;

    {
        Settings settings("servo", false);
        const int stored_x = settings.GetInt("zero_pos_1", kServoZeroXDefault);
        const int stored_y = settings.GetInt("zero_pos_2", kServoZeroYDefault);
        if (stored_x >= 0 && stored_x <= 1000) {
            servo_zero_x = stored_x;
        }
        if (stored_y >= 0 && stored_y <= 1000) {
            servo_zero_y = stored_y;
        }
    }

    uint8_t ids[2] = {1, 2};
    uint8_t torque_enabled[2] = {1, 1};
    servo_bus.syncWrite(ids, 2, SCSCL_TORQUE_ENABLE, torque_enabled, 1);

    current_yaw_raw = servoRawForAngle(servo_zero_x, 0);
    current_pitch_raw = servoRawForAngle(servo_zero_y, kPitchMid);
    motion_start_yaw_raw = current_yaw_raw;
    motion_start_pitch_raw = current_pitch_raw;
    motion_target_yaw_raw = current_yaw_raw;
    motion_target_pitch_raw = current_pitch_raw;
    writeServoRaw(current_yaw_raw, current_pitch_raw);

    Serial0.printf("SERVO ready zeroX=%d zeroY=%d torque=1\n", servo_zero_x, servo_zero_y);
}

void setServoMotion(int yaw, int pitch, int speed, uint32_t now)
{
    motion_start_yaw_raw = current_yaw_raw;
    motion_start_pitch_raw = current_pitch_raw;
    motion_target_yaw_raw = servoRawForAngle(servo_zero_x, yaw);
    motion_target_pitch_raw = servoRawForAngle(servo_zero_y, pitch);
    motion_start_ms = now;
    motion_duration_ms = constrain(map(constrain(speed, 0, kMaxServoSpeed), 0,
                                       kMaxServoSpeed, 900, 160),
                                   140, 900);
}

void updateServoMotion(uint32_t now)
{
    const uint32_t elapsed = now - motion_start_ms;
    const float linear = constrain(elapsed / static_cast<float>(motion_duration_ms), 0.0f, 1.0f);
    const float eased = linear * linear * (3.0f - 2.0f * linear);
    const int yaw_raw = motion_start_yaw_raw +
                        static_cast<int>((motion_target_yaw_raw - motion_start_yaw_raw) * eased);
    const int pitch_raw = motion_start_pitch_raw +
                          static_cast<int>((motion_target_pitch_raw - motion_start_pitch_raw) * eased);

    if (static_cast<int32_t>(now - next_servo_write_ms) < 0 &&
        linear < 1.0f) {
        return;
    }
    if (yaw_raw == current_yaw_raw && pitch_raw == current_pitch_raw) {
        return;
    }

    writeServoRaw(yaw_raw, pitch_raw);
    next_servo_write_ms = now + kServoWriteIntervalMs;
}

Rgb hsvColor(uint8_t hue, uint8_t value)
{
    const uint8_t region = hue / 43;
    const uint8_t remainder = (hue - region * 43) * 6;
    const uint8_t p = 0;
    const uint8_t q = static_cast<uint8_t>(value * (255 - remainder) / 255);
    const uint8_t t = static_cast<uint8_t>(value * remainder / 255);

    switch (region) {
        case 0:
            return {value, t, p};
        case 1:
            return {q, value, p};
        case 2:
            return {p, value, t};
        case 3:
            return {p, q, value};
        case 4:
            return {t, p, value};
        default:
            return {value, p, q};
    }
}

void drawHappyEye(LGFX_Device& display, int x, int y, uint16_t color)
{
    for (int line = 0; line < 5; ++line) {
        display.drawLine(x - 25, y + 7 + line, x, y - 10 + line, color);
        display.drawLine(x, y - 10 + line, x + 25, y + 7 + line, color);
    }
}

void drawStar(LGFX_Device& display, int cx, int cy, int outer, int inner, uint16_t color)
{
    int previous_x = cx;
    int previous_y = cy - outer;
    for (int point = 1; point <= 10; ++point) {
        const float angle = -HALF_PI + point * PI / 5.0f;
        const int radius = (point & 1) ? outer : inner;
        const int x = cx + static_cast<int>(cosf(angle) * radius);
        const int y = cy + static_cast<int>(sinf(angle) * radius);
        for (int width = -1; width <= 1; ++width) {
            display.drawLine(previous_x, previous_y + width, x, y + width, color);
        }
        previous_x = x;
        previous_y = y;
    }
}

void drawHeart(LGFX_Device& display, int cx, int cy, int size, uint16_t color)
{
    const int lobe = size * 45 / 100;
    display.fillCircle(cx - size / 4, cy - size / 7, lobe, color);
    display.fillCircle(cx + size / 4, cy - size / 7, lobe, color);
    display.fillTriangle(cx - size * 7 / 10, cy, cx + size * 7 / 10, cy,
                         cx, cy + size * 4 / 5, color);
}

void drawOpenEye(LGFX_Device& display, int x, int y, int radius, uint16_t accent, int gaze_x,
                 int gaze_y)
{
    display.fillCircle(x, y, radius, rgb565(245, 250, 255));
    display.fillCircle(x + gaze_x, y + gaze_y, radius * 55 / 100, rgb565(11, 18, 32));
    display.fillCircle(x + gaze_x + 7, y + gaze_y - 8, radius / 5, accent);
    display.fillCircle(x + gaze_x - 4, y + gaze_y - 2, radius / 10, rgb565(255, 255, 255));
    display.drawCircle(x, y, radius, blendColor(accent, rgb565(255, 255, 255), 110));
}

void drawSmile(LGFX_Device& display, int cx, int y, int width, int depth, uint16_t color)
{
    int px = cx - width / 2;
    int py = y;
    for (int step = 1; step <= 6; ++step) {
        const float t = step / 6.0f;
        const int x = cx - width / 2 + static_cast<int>(t * width);
        const int curve = static_cast<int>((1.0f - (2.0f * t - 1.0f) * (2.0f * t - 1.0f)) * depth);
        const int next_y = y + curve;
        for (int thickness = 0; thickness < 4; ++thickness) {
            display.drawLine(px, py + thickness, x, next_y + thickness, color);
        }
        px = x;
        py = next_y;
    }
}

void drawOpenMouth(LGFX_Device& display, int cx, int y, int width, int height, uint16_t accent)
{
    display.fillRoundRect(cx - width / 2, y - height / 2, width, height, height / 2,
                          rgb565(50, 8, 25));
    display.fillRect(cx - width / 3, y - height / 2 + 4, width * 2 / 3, 7,
                     rgb565(245, 250, 255));
    display.fillTriangle(cx - width / 4, y + height / 2 - 2, cx + width / 4,
                         y + height / 2 - 2, cx, y + height / 2 - 15,
                         blendColor(accent, rgb565(255, 80, 120), 90));
    for (int line = 0; line < 3; ++line) {
        display.drawRoundRect(cx - width / 2 - line, y - height / 2 - line,
                              width + line * 2, height + line * 2, height / 2, accent);
    }
}

void drawBeatBars(LGFX_Device& display, int width, int height, uint32_t now, uint16_t color)
{
    constexpr int kBarCount = 9;
    constexpr int kBarWidth = 8;
    constexpr int kGap      = 5;
    const int total_width   = kBarCount * kBarWidth + (kBarCount - 1) * kGap;
    const int start_x       = (width - total_width) / 2;
    const uint32_t phase    = static_cast<int32_t>(now - dance_start_ms) < 0
                                  ? 0
                                  : (now - dance_start_ms) % 500;

    for (int i = 0; i < kBarCount; ++i) {
        const float wave = (sinf((phase / 500.0f) * TWO_PI * 2.0f + i * 0.72f) + 1.0f) * 0.5f;
        const int bar_height = 5 + static_cast<int>(wave * 16);
        display.fillRoundRect(start_x + i * (kBarWidth + kGap), height - 16 - bar_height,
                              kBarWidth, bar_height, 3, color);
    }
}

void drawFace(uint32_t now)
{
    auto& display = M5StackChan.Display();
    const int width = display.width();
    const int height = display.height();
    const Palette palette = paletteFor(expression);
    const uint8_t pulse = beatPulse(now, 500);
    const uint16_t background = palette.background;
    const uint16_t panel = palette.panel;
    const int face_y = 28;
    const int face_w = width - 36;
    const int face_h = height - 56;
    static bool scene_painted = false;
    static Expression painted_expression = Expression::Happy;
    const bool repaint_scene = !scene_painted || expression != painted_expression;

    display.startWrite();
    if (repaint_scene) {
        display.fillScreen(background);

        // Soft two-tone ambience behind the face.
        for (int stripe = 0; stripe < 7; ++stripe) {
            const uint8_t amount = static_cast<uint8_t>(35 + stripe * 18);
            const uint16_t color = blendColor(background, palette.secondary, amount);
            const int y = 16 + stripe * 30;
            display.fillTriangle(width - 150 - stripe * 18, y, width, y + 20, width, y + 42,
                                 color);
        }

        display.fillRoundRect(18, face_y, face_w, face_h, 38, panel);
        display.drawRoundRect(18, face_y, face_w, face_h, 38,
                              blendColor(palette.accent, panel, 150));
        display.drawRoundRect(22, face_y + 4, face_w - 8, face_h - 8, 34,
                              blendColor(palette.secondary, panel, 195));

        display.setFont(&fonts::Font0);
        display.setTextSize(1);
        display.setTextDatum(top_left);
        display.setTextColor(palette.accent, panel);
        display.drawString("STACKCHAN  //  AUTO DANCE", 31, face_y + 13);
        display.setTextDatum(top_right);
        display.setTextColor(palette.secondary, panel);
        display.drawString("LOOP", width - 31, face_y + 13);
    } else {
        // Redraw only the animated areas. Clearing the whole screen at 15 FPS
        // produces visible tearing and slow QMP frame captures on StackChan.
        display.fillRoundRect(34, face_y + 40, width - 68, face_h - 56, 26, panel);
        display.fillRect(0, height - 28, width, 28, background);
    }
    scene_painted = true;
    painted_expression = expression;

    const bool blinking = static_cast<int32_t>(now - blink_end_ms) < 0;
    const int gaze_x = static_cast<int>(sinf(now / 610.0f) * 7.0f);
    const int gaze_y = static_cast<int>(cosf(now / 790.0f) * 4.0f);
    const int eye_y = face_y + 82;
    const int left_eye_x = width / 2 - 61;
    const int right_eye_x = width / 2 + 61;

    switch (expression) {
        case Expression::Happy:
            drawHappyEye(display, left_eye_x, eye_y, palette.accent);
            drawHappyEye(display, right_eye_x, eye_y, palette.accent);
            drawSmile(display, width / 2, eye_y + 45, 92, 23, palette.secondary);
            break;

        case Expression::Excited:
            if (blinking) {
                drawHappyEye(display, left_eye_x, eye_y, palette.accent);
                drawHappyEye(display, right_eye_x, eye_y, palette.accent);
            } else {
                const int bounce = (pulse > 150) ? -3 : 2;
                drawOpenEye(display, left_eye_x, eye_y + bounce, 27, palette.accent, gaze_x, gaze_y);
                drawOpenEye(display, right_eye_x, eye_y + bounce, 27, palette.accent, gaze_x,
                            gaze_y);
            }
            drawOpenMouth(display, width / 2, eye_y + 53, 82, 40, palette.accent);
            break;

        case Expression::Wink:
            if (blinking) {
                drawHappyEye(display, left_eye_x, eye_y, palette.accent);
            } else {
                drawOpenEye(display, left_eye_x, eye_y, 27, palette.accent, gaze_x, gaze_y);
            }
            drawHappyEye(display, right_eye_x, eye_y + 2, palette.secondary);
            drawSmile(display, width / 2 + 8, eye_y + 49, 68, 17, palette.accent);
            display.drawLine(right_eye_x + 31, eye_y - 35, right_eye_x + 46, eye_y - 44,
                             palette.secondary);
            display.drawLine(right_eye_x + 40, eye_y - 50, right_eye_x + 46, eye_y - 44,
                             palette.secondary);
            break;

        case Expression::Love: {
            const int heart_size = 48 + pulse / 18;
            drawHeart(display, left_eye_x, eye_y + 2, heart_size, palette.accent);
            drawHeart(display, right_eye_x, eye_y + 2, heart_size, palette.accent);
            display.fillEllipse(width / 2, eye_y + 53, 15, 10, rgb565(54, 7, 22));
            display.drawEllipse(width / 2, eye_y + 53, 16, 11, palette.secondary);
            break;
        }

        case Expression::Cool: {
            const int visor_x = 50;
            const int visor_w = width - 100;
            display.fillRoundRect(visor_x, eye_y - 34, visor_w, 68, 22, rgb565(4, 12, 28));
            display.drawRoundRect(visor_x, eye_y - 34, visor_w, 68, 22, palette.accent);
            const int scan_x = visor_x + 10 + ((now / 8) % (visor_w - 20));
            display.fillRoundRect(scan_x, eye_y - 24, 8, 48, 4, palette.accent);
            display.fillRoundRect(visor_x + 20, eye_y + 13, visor_w / 3, 4, 2,
                                  palette.secondary);
            display.drawLine(width / 2 - 30, eye_y + 48, width / 2 + 36, eye_y + 39,
                             palette.secondary);
            display.drawLine(width / 2 + 36, eye_y + 39, width / 2 + 47, eye_y + 42,
                             palette.secondary);
            break;
        }

        case Expression::Finale:
            drawStar(display, left_eye_x, eye_y, 31 + pulse / 25, 13, palette.accent);
            drawStar(display, right_eye_x, eye_y, 31 + pulse / 25, 13, palette.secondary);
            drawOpenMouth(display, width / 2, eye_y + 54, 92, 44, palette.accent);
            for (int spark = 0; spark < 5; ++spark) {
                const int x = 55 + (spark * 53 + ((now / 60) % 50));
                const int y = face_y + 52 + ((spark * 23) % 78);
                display.fillCircle(x % width, y, 2 + spark % 2,
                                   (spark & 1) ? palette.accent : palette.secondary);
            }
            break;
    }

    display.fillEllipse(left_eye_x - 35, eye_y + 43, 18, 9, palette.cheek);
    display.fillEllipse(right_eye_x + 35, eye_y + 43, 18, 9, palette.cheek);

    drawBeatBars(display, width, height, now, palette.accent);
    display.endWrite();
}

void showBootScreen()
{
    auto& display = M5StackChan.Display();
    const int width = display.width();
    const int height = display.height();

    display.startWrite();
    display.fillScreen(rgb565(7, 11, 28));
    display.fillRoundRect(24, 34, width - 48, height - 68, 32, rgb565(16, 29, 62));
    display.drawRoundRect(24, 34, width - 48, height - 68, 32, rgb565(61, 238, 255));

    drawHappyEye(display, width / 2 - 57, 102, rgb565(255, 220, 71));
    drawHappyEye(display, width / 2 + 57, 102, rgb565(61, 238, 255));
    drawSmile(display, width / 2, 142, 90, 20, rgb565(255, 94, 180));

    display.setFont(&fonts::Font0);
    display.setTextDatum(middle_center);
    display.setTextColor(rgb565(255, 255, 255));
    display.setTextSize(2);
    display.drawString("STACKCHAN DANCE", width / 2, 193);
    display.setTextColor(rgb565(61, 238, 255));
    display.setTextSize(1);
    display.drawString("AUTO START IN 1.5 s", width / 2, 216);
    display.endWrite();
}

void setLeds(uint32_t now)
{
    const uint32_t phase = static_cast<int32_t>(now - dance_start_ms) < 0
                               ? 0
                               : (now - dance_start_ms) % 1000;
    const uint8_t pulse = beatPulse(now, 500);
    const uint8_t base_value = static_cast<uint8_t>(45 + pulse * 65 / 255);

    for (int i = 0; i < 12; ++i) {
        Rgb color{0, 0, 0};

        switch (expression) {
            case Expression::Happy: {
                const uint8_t hue = static_cast<uint8_t>((i * 23) + phase / 8 + 110);
                color = hsvColor(hue, base_value);
                break;
            }
            case Expression::Excited: {
                const uint8_t hue = static_cast<uint8_t>((i * 28) + phase / 4);
                color = hsvColor(hue, base_value);
                break;
            }
            case Expression::Wink: {
                if (i < 6) {
                    const uint8_t v = static_cast<uint8_t>(45 + ((phase + i * 70) % 300) / 8);
                    color = hsvColor(190, v);
                } else {
                    color = hsvColor(48, static_cast<uint8_t>(20 + pulse / 12));
                }
                break;
            }
            case Expression::Love: {
                const uint8_t pair = (i & 1) ? base_value : static_cast<uint8_t>(base_value * 7 / 10);
                color = {pair, 0, static_cast<uint8_t>(pair * 3 / 5)};
                if (phase < 120) {
                    color = {static_cast<uint8_t>(pair + 20), 8, static_cast<uint8_t>(pair * 4 / 5)};
                }
                break;
            }
            case Expression::Cool: {
                const int head = static_cast<int>((now / 25) % 16);
                const int distance = head > i ? head - i : i - head;
                if (distance < 3) {
                    const uint8_t v = static_cast<uint8_t>(95 - distance * 22);
                    color = {static_cast<uint8_t>(v * 2 / 5), v, v};
                } else {
                    color = {6, 12, 28};
                }
                break;
            }
            case Expression::Finale: {
                const uint8_t hue = static_cast<uint8_t>((i * 21) + phase / 2 + 35);
                color = hsvColor(hue, static_cast<uint8_t>(55 + pulse * 7 / 25));
                break;
            }
        }

        M5StackChan.setRgbColor(i, color.r, color.g, color.b);
    }
    M5StackChan.refreshRgb();
}

const char* expressionName(Expression value)
{
    switch (value) {
        case Expression::Happy:
            return "HAPPY";
        case Expression::Excited:
            return "EXCITED";
        case Expression::Wink:
            return "WINK";
        case Expression::Love:
            return "LOVE";
        case Expression::Cool:
            return "COOL";
        case Expression::Finale:
            return "FINALE";
    }
    return "UNKNOWN";
}

void restartDance(uint32_t now, uint32_t delay_ms = kRestartDelayMs)
{
    expression = Expression::Happy;
    cue_index = 0;
    dance_start_ms = now + delay_ms;
    setServoMotion(0, kPitchMid, 420, now);
    next_blink_ms = now + 1800;
    blink_end_ms = 0;
    Serial0.printf("DANCE restart in %lu ms\n", static_cast<unsigned long>(delay_ms));
}

void updateTimeline(uint32_t now)
{
    if (static_cast<int32_t>(now - dance_start_ms) < 0) {
        return;
    }

    const uint32_t elapsed = now - dance_start_ms;
    while (cue_index < static_cast<size_t>(kCueCount) && elapsed >= kCues[cue_index].at) {
        const Cue& cue = kCues[cue_index];
        expression = cue.expression;
        setServoMotion(cue.yaw, cue.pitch, cue.speed, now);
        if (cue_index == 0 || expression != kCues[cue_index - 1].expression) {
            Serial0.printf("DANCE cue=%lu expr=%s yaw=%d pitch=%d\n",
                           static_cast<unsigned long>(cue_index),
                           expressionName(cue.expression), cue.yaw, cue.pitch);
        }
        ++cue_index;
    }

    if (elapsed >= kRoutineMs) {
        restartDance(now);
    }
}

void updateBlink(uint32_t now)
{
    if (static_cast<int32_t>(now - next_blink_ms) >= 0) {
        blink_end_ms = now + 115;
        next_blink_ms = now + random(2400, 4700);
    }
}

}  // namespace

void setup()
{
    Serial0.begin(115200);
    Serial.begin(115200);
    M5StackChan.begin();
    Serial0.begin(115200);

    auto& display = M5StackChan.Display();
    if (display.width() < display.height()) {
        display.setRotation(1);
    }
    display.setBrightness(82);

    M5StackChan.Motion.setAutoTorqueReleaseEnabled(false);
    M5StackChan.Motion.setAutoAngleSyncEnabled(false);
    initDirectServoControl();

    showBootScreen();
    M5StackChan.showRgbColor(16, 64, 92);

    randomSeed(static_cast<uint32_t>(micros()));
    const uint32_t now = millis();
    restartDance(now, 1500);
    // Leave the boot card visible until just before the first cue.
    next_face_ms = now + 1250;
    next_led_ms = now;
    next_blink_ms = now + 1600;

    Serial.println("StackChan auto-dance started");
    Serial0.println("StackChan auto-dance started");
}

void loop()
{
    const uint32_t now = millis();
    M5StackChan.update();

    if (M5StackChan.TouchSensor.wasPressed()) {
        restartDance(now);
        drawFace(now);
    }

    updateTimeline(now);
    updateServoMotion(now);
    updateBlink(now);

    if (static_cast<int32_t>(now - next_led_ms) >= 0) {
        setLeds(now);
        next_led_ms = now + kLedIntervalMs;
    }

    if (static_cast<int32_t>(now - next_face_ms) >= 0) {
        drawFace(now);
        next_face_ms = now + kFrameIntervalMs;
    }

    delay(1);
}
