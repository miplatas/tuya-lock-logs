"""Minimal client for the Tuya Open API (sign_method 2.0, HMAC-SHA256).

It does not depend on the official Tuya SDK. It only implements the pieces
needed to authenticate and perform GET requests (lock open-log queries).
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
        self._users_cache = None
        self._users_cache_time = 0

    def _build_path(self, path: str, params: dict | None) -> str:
        if not params:
            return path
        items = sorted(params.items())
        query = "&".join(f"{k}={v}" for k, v in items)
        return f"{path}?{query}"

    def _sign(self, method: str, full_path: str, access_token: str = "") -> tuple[str, str]:
        t = str(int(time.time() * 1000))
        content_sha256 = hashlib.sha256(b"").hexdigest()
        # method \n content-sha256 \n headers(empty) \n url
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

    def get_users(self, device_id: str, ttl: int = 3600) -> list:
        """List the home users and their unlock methods (cached)."""
        if self._users_cache is not None and time.time() - self._users_cache_time < ttl:
            return self._users_cache

        records: list = []
        page_no = 1
        while True:
            data = self.get(
                f"/v1.0/smart-lock/devices/{device_id}/users",
                {"page_no": str(page_no), "page_size": "50"},
            )
            if not data.get("success"):
                raise RuntimeError(f"Tuya API error (users): {data}")
            result = data.get("result", {})
            page = result.get("records", [])
            records.extend(page)
            if not result.get("has_more"):
                break
            page_no += 1

        self._users_cache = records
        self._users_cache_time = time.time()
        return records

    def resolve_user_name(self, device_id: str, log: dict) -> str | None:
        """Try to map an open-log record to a user name."""
        try:
            users = self.get_users(device_id)
        except Exception:
            return None

        user_id = str(log.get("user_id", "0"))
        if user_id and user_id != "0":
            for user in users:
                if str(user.get("user_id")) == user_id:
                    return user.get("nick_name")

        status = log.get("status", {})
        code = status.get("code")
        value = str(status.get("value"))
        for user in users:
            for detail in user.get("unlock_detail", []):
                if detail.get("dp_code") != code:
                    continue
                for item in detail.get("unlock_list", []):
                    if str(item.get("unlock_sn")) == value:
                        return user.get("nick_name")
        return None

    def get_open_logs(self, device_id: str, start_time_ms: int, end_time_ms: int, page_size: int = 10):
        """Return (logs, total) sorted from newest to oldest."""
        path = f"/v1.1/devices/{device_id}/door-lock/open-logs"
        params = {
            "page_no": "1",
            "page_size": str(page_size),
            "start_time": str(start_time_ms),
            "end_time": str(end_time_ms),
        }
        data = self.get(path, params)
        if not data.get("success"):
            raise RuntimeError(f"Tuya API error (open-logs): {data}")
        result = data.get("result", {})
        logs = result.get("logs", [])
        logs.sort(key=lambda x: x.get("update_time", 0), reverse=True)
        return logs, result.get("total", len(logs))

    def get_alarm_logs(self, device_id: str, page_size: int = 5) -> list:
        """Latest lock alarms (tamper, forced entry, low battery, etc.)."""
        path = f"/v1.1/devices/{device_id}/door-lock/alarm-logs"
        params = {"page_no": "1", "page_size": str(page_size)}
        data = self.get(path, params)
        if not data.get("success"):
            raise RuntimeError(f"Tuya API error (alarm-logs): {data}")
        records = data.get("result", {}).get("records", [])
        records.sort(key=lambda x: x.get("update_time", 0), reverse=True)
        return records

    def get_device_status(self, device_id: str) -> dict:
        """Current device DPs (for battery, etc.)."""
        data = self.get(f"/v1.0/devices/{device_id}/status")
        if not data.get("success"):
            raise RuntimeError(f"Tuya API error (status): {data}")
        return {item["code"]: item["value"] for item in data.get("result", [])}

    def get_open_summary(self, device_id: str) -> dict:
        """Fast summary: last open event (with resolved user)."""
        now_ms = int(time.time() * 1000)
        week_ago_ms = now_ms - 7 * 24 * 60 * 60 * 1000

        logs, _ = self.get_open_logs(device_id, week_ago_ms, now_ms, page_size=10)
        last = logs[0] if logs else None
        if last:
            last["resolved_user"] = self.resolve_user_name(device_id, last)

        return {"last": last}

    _BATTERY_STATE_MAP = {
        "high": 100,
        "medium": 50,
        "low": 20,
        "power_low": 5,
        "strong": 100,
        "normal": 60,
    }

    def get_status_summary(self, device_id: str) -> dict:
        """Slow summary: battery and recent alarms (change infrequently)."""
        import logging
        _log = logging.getLogger(__name__)
        battery = None
        try:
            status = self.get_device_status(device_id)
            _log.debug("[tuya_lock_logs] device status DPs: %s", status)
            for code in (
                "battery_percentage",
                "residual_electricity",
                "battery",
                "battery_level",
                "va_battery",
            ):
                if code in status:
                    battery = int(status[code])
                    break
            if battery is None and "battery_state" in status:
                raw = status["battery_state"]
                battery = self._BATTERY_STATE_MAP.get(raw)
                if battery is None:
                    _log.warning("[tuya_lock_logs] Unknown battery_state: %r", raw)
            if battery is None:
                _log.warning(
                    "[tuya_lock_logs] No battery DP found. Available DPs: %s",
                    list(status.keys()),
                )
        except Exception as exc:  # noqa: BLE001
            _log.warning("[tuya_lock_logs] Error getting device status: %s", exc)

        return {"battery": battery}
