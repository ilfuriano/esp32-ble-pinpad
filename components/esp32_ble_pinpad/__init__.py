from esphome import automation
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import output, esp32_ble_server
from esphome.const import CONF_ID, CONF_TRIGGER_ID


AUTO_LOAD = ["binary_sensor", "output", "esp32_ble_server"]
CODEOWNERS = ["@mik3y"]
CONFLICTS_WITH = ["esp32_ble_tracker", "esp32_ble_beacon"]
DEPENDENCIES = ["esp32"]

CONF_BLE_SERVER_ID = "ble_server_id"
CONF_STATUS_INDICATOR = "status_indicator"
CONF_SECURITY_MODE = "security_mode"
CONF_SECRET_PASSCODE = "secret_passcode"
CONF_ON_PINPAD_ACCEPTED = "on_pinpad_accepted"
CONF_ON_PINPAD_REJECTED = "on_pinpad_rejected"
CONF_ON_USER_COMMAND = "on_user_command_received"
CONF_ON_USER_SELECTED = "on_user_selected"
CONF_START_ADVERTISING = "start_advertising"
CONF_STOP_ADVERTISING = "stop_advertising"
SECURITY_MODE_NONE = "none"
SECURITY_MODE_HOTP = "hotp"
SECURITY_MODE_TOTP = "totp"


esp32_ble_pinpad_ns = cg.esphome_ns.namespace("esp32_ble_pinpad")
ESP32BLEPinpadComponent = esp32_ble_pinpad_ns.class_(
    "ESP32BLEPinpadComponent", cg.Component, esp32_ble_server.BLEServiceComponent
)

SecurityMode = esp32_ble_pinpad_ns.enum("SecurityMode")
SECURITY_MODES = {
    SECURITY_MODE_NONE: SecurityMode.SECURITY_MODE_NONE,
    SECURITY_MODE_HOTP: SecurityMode.SECURITY_MODE_HOTP,
    SECURITY_MODE_TOTP: SecurityMode.SECURITY_MODE_TOTP,
}


def validate_secret_pin(value):
    value = cv.string_strict(value)
    if not value:
        return value
    try:
        value.encode('ascii')
    except UnicodeEncodeError:
        raise cv.Invalid("pin must consist of only ascii characters")
    return value

validate_security_mode = cv.one_of(*SECURITY_MODES.keys(), lower=True)

# Triggers
PinpadAcceptedTrigger = esp32_ble_pinpad_ns.class_("PinpadAcceptedTrigger", automation.Trigger.template())
PinpadRejectedTrigger = esp32_ble_pinpad_ns.class_("PinpadRejectedTrigger", automation.Trigger.template())
PinpadUserSelectedTrigger = esp32_ble_pinpad_ns.class_("PinpadUserSelectedTrigger", automation.Trigger.template())
PinpadUserCommandTrigger = esp32_ble_pinpad_ns.class_("PinpadUserCommandTrigger", automation.Trigger.template())

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(ESP32BLEPinpadComponent),
        cv.GenerateID(CONF_BLE_SERVER_ID): cv.use_id(esp32_ble_server.BLEServer),
        cv.Required(CONF_SECURITY_MODE): validate_security_mode,
        cv.Required(CONF_SECRET_PASSCODE): cv.string_strict,
        cv.Optional(CONF_ON_PINPAD_ACCEPTED): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(PinpadAcceptedTrigger),
            }
        ),
        cv.Optional(CONF_ON_PINPAD_REJECTED): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(PinpadRejectedTrigger),
            }
        ),
        cv.Optional(CONF_ON_USER_SELECTED): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(PinpadUserSelectedTrigger),
            }
        ),
        cv.Optional(CONF_ON_USER_COMMAND): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(PinpadUserCommandTrigger),
            }
        ),        
        cv.Optional(CONF_STATUS_INDICATOR): cv.use_id(output.BinaryOutput),
        cv.Optional(CONF_START_ADVERTISING, default=True): cv.boolean,  # Add this line
        cv.Optional(CONF_STOP_ADVERTISING, default=False): cv.boolean,  # Add this line
    }
).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    ble_server = await cg.get_variable(config[CONF_BLE_SERVER_ID])
    cg.add(ble_server.register_service_component(var))


    cg.add(var.set_security_mode(
        SECURITY_MODES[config[CONF_SECURITY_MODE]],
        config[CONF_SECRET_PASSCODE]
    ))

    for conf in config.get(CONF_ON_PINPAD_ACCEPTED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [(cg.std_string, "user"), (cg.std_string, "cmd")], conf)

    for conf in config.get(CONF_ON_PINPAD_REJECTED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [(cg.std_string, "user"), (cg.std_string, "cmd")], conf)
    
    for conf in config.get(CONF_ON_USER_SELECTED, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [(cg.std_string, "user")], conf)

    for conf in config.get(CONF_ON_USER_COMMAND, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(trigger, [(cg.std_string, "cmd")], conf)

    if CONF_STATUS_INDICATOR in config:
        status_indicator = await cg.get_variable(config[CONF_STATUS_INDICATOR])
        cg.add(var.set_status_indicator(status_indicator))
        
    # Handle start/stop advertising configuration
    if config[CONF_START_ADVERTISING]:
        cg.add(var.start_advertising())
    if config[CONF_STOP_ADVERTISING]:
        cg.add(var.stop_advertising())
