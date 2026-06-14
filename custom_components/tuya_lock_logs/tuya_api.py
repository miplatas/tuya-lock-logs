"""Cliente minimo para la Tuya Open API (sign_method 2.0, HMAC-SHA256).

No depende del SDK oficial de Tuya. Solo implementa lo necesario para
autenticarse y hacer peticiones GET (consulta de open-logs de la chapa).
"""
import hashlib
import hmac
import time

import requests


class TuyaAPI:
    def __init__(self, base_url: str, access_id: str, access_secret: str):
        self.base_url = base_url.rstrip("/")
        self.access_id = access_id
        self.access_secret = access_secret
        self._token = None
        self._token_expire = 0

    def _build_path(self, path: str, params: dict | None) -> str:
        if not params:
            return path
        items = sorted(params.items())
        query = "&".join(f"{k}={v}" for k, v in items)
        return f"{path}?{query}"

    def _sign(self, method: str, full_path: str, access_token: str = "") -> tuple[str, str]:
        t = str(int(time.time() * 1000))
        content_sha256 = hashlib.sha256(b"").hexdigest()
        # method \n content-sha256 \n headers(vacio) \n url
        string_to_sign = f"{method}\n{content_sha256}\n\n{full_path}"
        sign_str = self.access_id + access_token + t + string_to_sign
        sign = hmac.new(
            self.access_secret.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()
        return t, sign

    def _ensure_token(self):
        if self._token and time.time() < self._token_expire:
            return
        path = "/v1.0/token?grant_type=1"
        t, sign = self._sign("GET", path)
        headers = {
            "client_id": self.access_id,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256",
        }
        resp = requests.get(self.base_url + path, headers=headers, timeout=10)
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError(f"Tuya auth error: {data}")
        result = data["result"]
        self._token = result["access_token"]
        self._token_expire = time.time() + result["expire_time"] - 60

    def get(self, path: str, params: dict | None = None) -> dict:
        self._ensure_token()
        full_path = self._build_path(path, params)
        t, sign = self._sign("GET", full_path, self._token)
        headers = {
            "client_id": self.access_id,
            "access_token": self._token,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256",
        }
        resp = requests.get(self.base_url + full_path, headers=headers, timeout=10)
        return resp.json()

    def get_last_open_log(self, device_id: str) -> dict | None:
        """Devuelve el registro mas reciente de apertura fisica de la chapa."""
        now_ms = int(time.time() * 1000)
        week_ago_ms = now_ms - 7 * 24 * 60 * 60 * 1000
        path = f"/v1.1/devices/{device_id}/door-lock/open-logs"
        params = {
            "page_no": "1",
            "page_size": "10",
            "start_time": str(week_ago_ms),
            "end_time": str(now_ms),
        }
        data = self.get(path, params)
        if not data.get("success"):
            raise RuntimeError(f"Tuya API error: {data}")
        logs = data.get("result", {}).get("logs", [])
        if not logs:
            return None
        logs.sort(key=lambda x: x.get("update_time", 0), reverse=True)
        return logs[0]
