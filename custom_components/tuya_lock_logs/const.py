DOMAIN = "tuya_lock_logs"

CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_DEVICE_ID = "device_id"
CONF_REGION = "region"
CONF_FAST_SCAN_INTERVAL = "fast_scan_interval"
CONF_SLOW_SCAN_INTERVAL = "slow_scan_interval"
CONF_TRIGGER_DELAY = "trigger_delay"

# "Fast": last open (access log)
DEFAULT_FAST_SCAN_INTERVAL = 300  # 5 min
# "Slow": battery (changes rarely)
DEFAULT_SLOW_SCAN_INTERVAL = 3600  # 1 h
# Default delay for the refresh service triggered by an external sensor
DEFAULT_TRIGGER_DELAY = 5  # seconds

SERVICE_REFRESH = "refresh"

REGIONS = {
    "us": "https://openapi.tuyaus.com",
    "eu": "https://openapi.tuyaeu.com",
    "cn": "https://openapi.tuyacn.com",
    "in": "https://openapi.tuyain.com",
}

# Translation of status.code -> readable label when unlock_name is missing
UNLOCK_METHODS = {
    "unlock_fingerprint": "Fingerprint",
    "unlock_password": "Password",
    "unlock_card": "Card",
    "unlock_app": "App",
    "unlock_face": "Face",
    "unlock_dynamic": "Dynamic password",
    "unlock_temporary": "Temporary password",
    "unlock_key": "Mechanical key",
    "unlock_remote": "Remote",
    "unlock_voice": "Voice",
}

# Translation of common alarm codes in Tuya locks
ALARM_CODES = {
    "alarm_lock": "Lock alarm",
    "hijack": "Duress",
    "tamper_alarm": "Tamper",
    "pry_alarm": "Forced entry",
    "shock_alarm": "Shock/impact",
    "low_battery": "Low battery",
    "low_battery_alarm": "Low battery",
    "wrong_password": "Wrong password",
    "wrong_finger": "Wrong fingerprint",
    "door_open_timeout": "Door left open too long",
    "doorbell": "Doorbell",
}
