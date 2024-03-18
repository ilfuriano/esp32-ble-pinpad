#pragma once

#include "esphome/core/component.h"
#include "esphome/core/automation.h"
#include "esp32_ble_pinpad_component.h"

namespace esphome {
namespace esp32_ble_pinpad {

class PinpadAcceptedTrigger : public Trigger<std::string, std::string> {
 public:
  PinpadAcceptedTrigger(ESP32BLEPinpadComponent *pinpad) {
    pinpad->add_on_state_callback([this, pinpad]() {
      if (pinpad->is_accepted()) {
        this->trigger(pinpad->get_userid(), pinpad->get_cmd());
      }
    });
  }
};

class PinpadRejectedTrigger : public Trigger<std::string, std::string> {
 public:
  PinpadRejectedTrigger(ESP32BLEPinpadComponent *pinpad) {
    pinpad->add_on_state_callback([this, pinpad]() {
      if (pinpad->is_rejected()) {
        this->trigger(pinpad->get_userid(), pinpad->get_cmd());
      }
    });
  }
};

class PinpadUserSelectedTrigger : public Trigger<std::string> {
 public:
  PinpadUserSelectedTrigger(ESP32BLEPinpadComponent *pinpad) {
    pinpad->add_on_user_selected_callback([this](const std::string &user_id) {
        this->trigger(user_id);
    });
  }
};

}  // namespace esp32_ble_pinpad
}  // namespace esphome
