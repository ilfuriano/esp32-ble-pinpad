#pragma once

#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/esp32_ble_server/ble_characteristic.h"
#include "esphome/components/esp32_ble_server/ble_server.h"
#include "esphome/components/output/binary_output.h"
#include "esphome/core/component.h"
#include "esphome/core/helpers.h"
#include "esphome/core/preferences.h"

#include <vector>

#ifdef USE_ESP32

namespace esphome {
namespace esp32_ble_pinpad {

using namespace esp32_ble_server;

static const char *const TAG = "esp32_ble_pinpad.component";

static const size_t INPUT_MAX_LEN = 255;

static const char *const PINPAD_SERVICE_UUID = "909e937a-e826-11ee-bd3d-0242ac120000";
static const char *const PINPAD_STATUS_CHR_UUID = "909e937a-e826-11ee-bd3d-0242ac120001";
static const char *const PINPAD_RPC_COMMAND_CHR_UUID = "909e937a-e826-11ee-bd3d-0242ac120002";
static const char *const PINPAD_SECURITY_MODE_CHR_UUID = "909e937a-e826-11ee-bd3d-0242ac120003";
static const char *const PINPAD_HOTP_COUNTER_CHR_UUID = "909e937a-e826-11ee-bd3d-0242ac120004";
static const char *const PINPAD_USERID_CHR_UUID = "909e937a-e826-11ee-bd3d-0242ac120005";
static const char *const PINPAD_CMD_CHR_UUID = "909e937a-e826-11ee-bd3d-0242ac120006";
static const char *const PINPAD_USER_CMD_CHR_UUID = "909e937a-e826-11ee-bd3d-0242ac120007";




static const uint32_t VALIDATION_STATE_HOLD_MILLIS = 500;

enum State : uint8_t {
  STATE_STOPPED = 0x00,
  STATE_IDLE = 0x01,
  STATE_PIN_ACCEPTED = 0x02,
  STATE_PIN_REJECTED = 0x03,
};

enum SecurityMode : uint8_t {
  SECURITY_MODE_NONE = 0x00,
  SECURITY_MODE_HOTP = 0x01,
  SECURITY_MODE_TOTP = 0x02,
};

class ESP32BLEPinpadComponent : public Component, public BLEServiceComponent {
 public:
  ESP32BLEPinpadComponent();
  void dump_config() override;
  void loop() override;
  void setup() override;
  void setup_characteristics();
  void on_client_disconnect() override;

  float get_setup_priority() const override;
  void start() override;
  void stop() override;



  // Setup code.
  void set_security_mode(SecurityMode mode, const std::string &secret_passcode);

  bool is_active() const { return this->state_ != STATE_STOPPED; }
  bool is_accepted() const { return this->state_ == STATE_PIN_ACCEPTED; }
  bool is_rejected() const { return this->state_ == STATE_PIN_REJECTED; }
  void add_on_state_callback(std::function<void()> &&f) { this->state_callback_.add(std::move(f)); }
  void add_on_user_selected_callback(std::function<void(std::string)> callback) {
    this->user_selected_callback_.add(std::move(callback));
  }
  void add_on_user_command_callback(std::function<void(std::string)> callback) {
      this->user_command_callback_.add(std::move(callback));
  }  
  std::string get_userid() const { return this->user_id_; };
  std::string get_cmd() const { return this->cmd_id_; };

  void set_status_indicator(output::BinaryOutput *status_indicator) { this->status_indicator_ = status_indicator; }
  void set_user_commands(const std::string &commands);


 protected:
  bool should_start_{false};
  bool setup_complete_{false};

  SecurityMode security_mode_;
  std::string secret_passcode_;

  State state_{STATE_STOPPED};

  std::vector<uint8_t> incoming_data_;

  std::string user_id_;
  std::string cmd_id_;

  BLEService *service_;
  BLECharacteristic *status_;
  BLECharacteristic *rpc_;
  BLECharacteristic *security_mode_characteristic_;
  BLECharacteristic *hotp_counter_characteristic_;
  BLECharacteristic *user_id_characteristic_;
  BLECharacteristic *cmd_characteristic_;
  BLECharacteristic *user_cmd_characteristic_;

  CallbackManager<void()> state_callback_{};
  CallbackManager<void(std::string)> user_selected_callback_;


  ESPPreferenceObject hotp_counter_;

  // Timestamp we entered current state, in millis
  uint32_t current_state_start_{0};

  output::BinaryOutput *status_indicator_{nullptr};

  uint32_t get_current_hotp_counter();
  uint32_t increment_hotp_counter();

  void set_state_(State state);
  void process_incoming_data_();
  void validate_pin_(std::string pin);
  void clear_data();

};

}  // namespace esp32_ble_pinpad
}  // namespace esphome

#endif
