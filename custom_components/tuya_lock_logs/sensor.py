"""Sensor: ultima persona/metodo que abrio la chapa fisicamente."""
from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, UNLOCK_METHODS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TuyaLockLastOpenSensor(coordinator, entry)])


class TuyaLockLastOpenSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:account-lock-open"
    _attr_has_entity_name = True
    _attr_name = "Última apertura"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_last_open"

    @property
    def native_value(self):
        log = self.coordinator.data
        if not log:
            return "Sin registros"

        name = log.get("unlock_name") or ""
        if name:
            return name

        method = log.get("status", {}).get("code", "")
        return UNLOCK_METHODS.get(method, method or "Desconocido")

    @property
    def extra_state_attributes(self):
        log = self.coordinator.data
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
            "metodo": UNLOCK_METHODS.get(method, method),
            "metodo_raw": method,
            "user_id": log.get("user_id"),
            "hora": hora,
            "raw": log,
        }
