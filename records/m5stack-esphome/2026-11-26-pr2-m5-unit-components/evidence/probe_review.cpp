#include <gtest/gtest.h>

#include "esphome/components/m5_unit_ncir2/m5_unit_ncir2.h"
#include "esphome/core/application.h"
#include "ncir2_bus.h"

namespace esphome::m5_unit_ncir2::testing {

class ReviewHub : public M5UnitNCIR2 {
 public:
  using M5UnitNCIR2::write_settings_;
};

class ReviewProbe : public ::testing::Test {
 protected:
  void SetUp() override {
    this->hub_.set_i2c_bus(&this->bus_);
    this->hub_.set_i2c_address(0x5A);
  }
  NCIR2Bus bus_;
  ReviewHub hub_;
};

// A unit that answers a moment after the ESP started must not stay failed forever.
TEST_F(ReviewProbe, LateUnitAfterFailedSetup) {
  this->bus_.absent = true;
  this->hub_.setup();
  EXPECT_TRUE(this->hub_.is_failed());

  this->bus_.absent = false;
  this->hub_.update();
  this->hub_.loop();
  EXPECT_TRUE(this->hub_.is_failed());  // no recovery path
}

// YAML alarm settings are written to the registers but never stored in the unit's flash.
TEST_F(ReviewProbe, YamlSettingsAreNotSavedToFlash) {
  this->hub_.set_alarm_temperature(1, 4000);
  this->hub_.setup();
  EXPECT_FALSE(this->hub_.is_failed());
  EXPECT_EQ(this->bus_.get_uint16(0x22), 4000);  // register written
  EXPECT_EQ(this->bus_.regs[0x80], 0);           // but no save command
}

}  // namespace esphome::m5_unit_ncir2::testing
