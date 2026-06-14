"""Sensores de la chapa: ultima apertura, hora, conteo diario, bateria y alarmas."""
from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ALARM_CODES, DOMAIN, UNLOCK_METHODS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = hass.data[DOMAIN][entry.entry_id]
    fast = store["fast"]
    slow = store["slow"]

    async_add_entities(
        [
            TuyaLockLastOpenSensor(fast, entry),
            TuyaLockLastOpenTimeSensor(fast, entry),
            TuyaLockTodayCountSensor(fast, entry),
            TuyaLockBatterySensor(slow, entry),
            TuyaLockAlarmSensor(slow, entry),
        ]
    )


def _method_name(code: str) -> str:
    return UNLOCK_METHODS.get(code, code or "Desconocido")


class TuyaLockLastOpenSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:account-lock-open"
    _attr_has_entity_name = True
    _attr_name = "Última apertura"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_open"

    @property
    def native_value(self):
        log = self.coordinator.data.get("last")
        if not log:
            return "Sin registros"

        name = log.get("unlock_name") or log.get("resolved_user") or ""
        if name:
            return name

        return _method_name(log.get("status", {}).get("code", ""))

    @property
    def extra_state_attributes(self):
        log = self.coordinator.data.get("last")
        if not log:
            return {}

        method = log.get("status", {}).get("code", "")
        update_time = log.get("update_time")
        hora = None
        if update_time:
            hora = datetime.fromtimestamp(
                update_time / 1000, tz=timezone.utc
            ).isoformat()

        return {
            "metodo": _method_name(method),
            "metodo_raw": method,
            "usuario": log.get("unlock_name") or log.get("resolved_user"),
            "user_id": log.get("user_id"),
            "hora": hora,
            "raw": log,
        }


class TuyaLockLastOpenTimeSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:clock-outline"
    _attr_has_entity_name = True
    _attr_name = "Hora de última apertura"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_open_time"

    @property
    def native_value(self):
        log = self.coordinator.data.get("last")
        if not log:
            return None
        update_time = log.get("update_time")
        if not update_time:
            return None
        return datetime.fromtimestamp(update_time / 1000, tz=timezone.utc)


class TuyaLockTodayCountSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:counter"
    _attr_has_entity_name = True
    _attr_name = "Aperturas hoy"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_today_count"

    @property
    def native_value(self):
        return self.coordinator.data.get("today_count", 0)


class TuyaLockBatterySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Batería de la chapa"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_battery"

    @property
    def native_value(self):
        return self.coordinator.data.get("battery")

    @property
    def available(self):
        return super().available and self.coordinator.data.get("battery") is not None


class TuyaLockAlarmSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:shield-alert-outline"
    _attr_has_entity_name = True
    _attr_name = "Última alarma de la chapa"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_alarm"

    @property
    def native_value(self):
        alarms = self.coordinator.data.get("alarms") or []
        if not alarms:
            return "Sin alarmas"

        last = alarms[0]
        status_list = last.get("status", [])
        if isinstance(status_list, dict):
            status_list = [status_list]
        if not status_list:
            return "Sin alarmas"

        code = status_list[0].get("code", "")
        return ALARM_CODES.get(code, code or "Desconocido")

    @property
    def extra_state_attributes(self):
        alarms = self.coordinator.data.get("alarms") or []
        if not alarms:
            return {}

        last = alarms[0]
        update_time = last.get("update_time")
        hora = None
        if update_time:
            hora = datetime.fromtimestamp(
                update_time / 1000, tz=timezone.utc
            ).isoformat()

        return {
            "hora": hora,
            "recientes": alarms,
        }
