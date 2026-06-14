"""Lock sensors: last open, open time, and battery."""
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
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DOMAIN, UNLOCK_METHODS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = hass.data[DOMAIN][entry.entry_id]
    fast = store["fast"]
    slow = store["slow"]

    async_add_entities(
        [
            TuyaLockLastOpenSensor(fast, entry),
            TuyaLockLastOpenTimeSensor(fast, entry),
            TuyaLockBatterySensor(slow, entry),
        ]
    )


def _method_name(code: str) -> str:
    return UNLOCK_METHODS.get(code, code or "Unknown")


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
        name=entry.title,
        manufacturer="Tuya",
    )


class TuyaLockLastOpenSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:account-lock-open"
    _attr_has_entity_name = True
    _attr_name = "Last open by"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_open"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self):
        log = self.coordinator.data.get("last")
        if not log:
            return "No records"

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
        time_value = None
        if update_time:
            time_value = datetime.fromtimestamp(
                update_time / 1000, tz=timezone.utc
            ).isoformat()

        return {
            "method": _method_name(method),
            "method_raw": method,
            "user": log.get("unlock_name") or log.get("resolved_user"),
            "user_id": log.get("user_id"),
            "time": time_value,
            "raw": log,
        }


class TuyaLockLastOpenTimeSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:clock-outline"
    _attr_has_entity_name = True
    _attr_name = "Last open time"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_open_time"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self):
        log = self.coordinator.data.get("last")
        if not log:
            return None
        update_time = log.get("update_time")
        if not update_time:
            return None
        return datetime.fromtimestamp(update_time / 1000, tz=timezone.utc)


class TuyaLockBatterySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_battery"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self):
        return self.coordinator.data.get("battery")
