DOMAIN = "tuya_lock_logs"

CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_DEVICE_ID = "device_id"
CONF_REGION = "region"
CONF_FAST_SCAN_INTERVAL = "fast_scan_interval"
CONF_SLOW_SCAN_INTERVAL = "slow_scan_interval"
CONF_TRIGGER_DELAY = "trigger_delay"

# "Rapido": ultima apertura + conteo de hoy (lo que importa para el log de accesos)
DEFAULT_FAST_SCAN_INTERVAL = 300  # 5 min
# "Lento": bateria + alarmas (cambia poco)
DEFAULT_SLOW_SCAN_INTERVAL = 3600  # 1 h
# Retraso por defecto del servicio de refresh por trigger (sensor de puerta/presencia)
DEFAULT_TRIGGER_DELAY = 5  # segundos

SERVICE_REFRESH = "refresh"

REGIONS = {
    "us": "https://openapi.tuyaus.com",
    "eu": "https://openapi.tuyaeu.com",
    "cn": "https://openapi.tuyacn.com",
    "in": "https://openapi.tuyain.com",
}

# Traduccion de status.code -> nombre legible cuando no hay unlock_name
UNLOCK_METHODS = {
    "unlock_fingerprint": "Huella",
    "unlock_password": "Contraseña",
    "unlock_card": "Tarjeta",
    "unlock_app": "App",
    "unlock_face": "Rostro",
    "unlock_dynamic": "Contraseña dinámica",
    "unlock_temporary": "Contraseña temporal",
    "unlock_key": "Llave mecánica",
    "unlock_remote": "Remoto",
    "unlock_voice": "Voz",
}

# Traduccion de codigos de alarma comunes en chapas Tuya
ALARM_CODES = {
    "alarm_lock": "Alarma de chapa",
    "hijack": "Coacción (duress)",
    "tamper_alarm": "Sabotaje",
    "pry_alarm": "Forzado",
    "shock_alarm": "Golpe/impacto",
    "low_battery": "Batería baja",
    "low_battery_alarm": "Batería baja",
    "wrong_password": "Contraseña incorrecta",
    "wrong_finger": "Huella incorrecta",
    "door_open_timeout": "Puerta abierta mucho tiempo",
    "doorbell": "Timbre",
}
