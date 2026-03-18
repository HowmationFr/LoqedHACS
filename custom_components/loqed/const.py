"""Constants for the LOQED Smart Lock integration."""

DOMAIN = "loqed"
MANUFACTURER = "LOQED"

CONF_IP_ADDRESS = "ip_address"
CONF_LOCAL_KEY_ID = "local_key_id"
CONF_SECRET = "secret"
CONF_LOCK_NAME = "lock_name"

# Bolt states returned by /status
BOLT_STATE_OPEN = "open"
BOLT_STATE_DAY_LOCK = "day_lock"
BOLT_STATE_NIGHT_LOCK = "night_lock"
BOLT_STATE_UNKNOWN = "unknown"

BOLT_STATE_NUMERIC = {
    1: BOLT_STATE_OPEN,
    2: BOLT_STATE_DAY_LOCK,
    3: BOLT_STATE_NIGHT_LOCK,
}

# Commands for /state endpoint
COMMAND_OPEN = "OPEN"
COMMAND_DAY_LOCK = "DAY_LOCK"
COMMAND_NIGHT_LOCK = "NIGHT_LOCK"

DEFAULT_SCAN_INTERVAL = 10  # seconds
