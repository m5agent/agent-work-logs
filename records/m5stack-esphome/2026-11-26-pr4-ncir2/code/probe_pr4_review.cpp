#include <gtest/gtest.h>

#include "esphome/components/m5_unit_ncir2/m5_unit_ncir2.h"
#include "esphome/core/application.h"
#include "ncir2_bus.h"

namespace esphome::m5_unit_ncir2::testing {

class Pr4Probe : public ::testing::Test {
 protected:
  void SetUp() override {
    this->bus_.regs[REG_FIRMWARE_VERSION] = 2;
    this->bus_.regs[REG_BUTTON] = 1;
    this->device_.set_i2c_bus(&this->bus_);
    this->device_.set_i2c_address(0x5A);
  }
  void TearDown() override {
    App.scheduler.cancel_timeout(&this->device_, uint32_t{0});
    App.scheduler.cancel_timeout(&this->device_, uint32_t{1});
    App.scheduler.call(millis());
  }
  NCIR2Bus bus_;
  M5UnitNCIR2 device_;
};

// Point from the #2 review: YAML writes reach the registers but the flash
// save command (0x80) is never sent by setup().
TEST_F(Pr4Probe, YamlSettingsAreNotSavedToFlash) {
  this->device_.set_alarm_temperature(1, 4000);
  this->device_.setup();
  EXPECT_FALSE(this->device_.is_failed());
  EXPECT_EQ(this->bus_.get_uint16(REG_ALARM_TEMPERATURE + 2), 4000u);
  EXPECT_EQ(this->bus_.regs[REG_SAVE_SETTINGS], 0u);
}

// Point from the #2 review: a failed setup() has no recovery path.
TEST_F(Pr4Probe, LateUnitAfterFailedSetupStaysFailed) {
  this->bus_.absent = true;
  this->device_.setup();
  ASSERT_TRUE(this->device_.is_failed());
  this->bus_.absent = false;
  this->device_.update();
  this->device_.loop();
  EXPECT_TRUE(this->device_.is_failed());
}

// New: the alarm temperature registers are int16 0.01 C in the unit firmware,
// but the number/YAML schemas allow up to 380 C.
TEST_F(Pr4Probe, AlarmTemperatureAboveInt16RangeWraps) {
  this->device_.setup();
  ASSERT_FALSE(this->device_.is_failed());
  EXPECT_TRUE(this->device_.control_setting(Setting::SETTING_HIGH_ALARM_TEMPERATURE, 380.0f));
  EXPECT_EQ(this->bus_.get_uint16(REG_ALARM_TEMPERATURE + 2), 0x9470u);
  int16_t stored = static_cast<int16_t>(this->bus_.get_uint16(REG_ALARM_TEMPERATURE + 2));
  EXPECT_EQ(stored, -27536);
}

}  // namespace esphome::m5_unit_ncir2::testing
