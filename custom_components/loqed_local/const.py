"""Constants for the LOQED Local integration."""

DOMAIN = "loqed_local"
MANUFACTURER = "LOQED"

CONF_IP_ADDRESS = "ip_address"
CONF_LOCAL_KEY_ID = "local_key_id"
CONF_SECRET = "secret"
CONF_LOCK_NAME = "lock_name"
CONF_WEBHOOK_ID = "webhook_id"

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

# Webhook: map requested_state string to internal bolt_state
REQUESTED_STATE_MAP = {
    "OPEN": BOLT_STATE_OPEN,
    "DAY_LOCK": BOLT_STATE_DAY_LOCK,
    "NIGHT_LOCK": BOLT_STATE_NIGHT_LOCK,
}

# Webhook: go_to_state string to internal bolt_state
GO_TO_STATE_MAP = {
    "OPEN": BOLT_STATE_OPEN,
    "DAY_LOCK": BOLT_STATE_DAY_LOCK,
    "NIGHT_LOCK": BOLT_STATE_NIGHT_LOCK,
}

# Webhook event type prefixes
EVENT_PREFIX_STATE_CHANGED = "STATE_CHANGED_"
EVENT_PREFIX_GO_TO_STATE = "GO_TO_STATE_"

# Commands for /state endpoint
COMMAND_OPEN = "OPEN"
COMMAND_DAY_LOCK = "DAY_LOCK"
COMMAND_NIGHT_LOCK = "NIGHT_LOCK"

# Polling interval (fallback — webhook is primary)
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
