DOMAIN = "tuya_lock_logs"

CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_DEVICE_ID = "device_id"
CONF_REGION = "region"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 300  # segundos

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
