"""Tuya Lock Open Logs - who physically opened the lock."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_DEVICE_ID,
    CONF_FAST_SCAN_INTERVAL,
    CONF_REGION,
    CONF_SLOW_SCAN_INTERVAL,
    CONF_TRIGGER_DELAY,
    DEFAULT_FAST_SCAN_INTERVAL,
    DEFAULT_SLOW_SCAN_INTERVAL,
    DEFAULT_TRIGGER_DELAY,
    DOMAIN,
    REGIONS,
    SERVICE_REFRESH,
)
from .tuya_api import TuyaAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

SERVICE_REFRESH_SCHEMA = vol.Schema(
    {
        vol.Optional("delay"): vol.Coerce(float),
        vol.Optional("entry_id"): str,
    }
)


def _setting(entry: ConfigEntry, key: str, default):
    return entry.options.get(key, entry.data.get(key, default))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = entry.data

    api = TuyaAPI(
        REGIONS[data[CONF_REGION]],
        data[CONF_ACCESS_ID],
        data[CONF_ACCESS_SECRET],
    )
    device_id = data[CONF_DEVICE_ID]

    fast_interval = _setting(entry, CONF_FAST_SCAN_INTERVAL, DEFAULT_FAST_SCAN_INTERVAL)
    slow_interval = _setting(entry, CONF_SLOW_SCAN_INTERVAL, DEFAULT_SLOW_SCAN_INTERVAL)
    trigger_delay = _setting(entry, CONF_TRIGGER_DELAY, DEFAULT_TRIGGER_DELAY)

    async def async_update_fast():
        try:
            return await hass.async_add_executor_job(api.get_open_summary, device_id)
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Error querying Tuya open-logs: {err}") from err

    async def async_update_slow():
        try:
            return await hass.async_add_executor_job(api.get_status_summary, device_id)
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Error querying Tuya status: {err}") from err

    fast_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_fast",
        update_method=async_update_fast,
        update_interval=timedelta(seconds=fast_interval),
    )
    slow_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_slow",
        update_method=async_update_slow,
        update_interval=timedelta(seconds=slow_interval),
    )

    await fast_coordinator.async_config_entry_first_refresh()
    await slow_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "fast": fast_coordinator,
        "slow": slow_coordinator,
        "trigger_delay": trigger_delay,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH):
        async def _handle_refresh(call: ServiceCall) -> None:
            target_entry_id = call.data.get("entry_id")
            delay = call.data.get("delay")

            entries = hass.data.get(DOMAIN, {})
            for eid, store in entries.items():
                if target_entry_id and eid != target_entry_id:
                    continue

                use_delay = delay if delay is not None else store["trigger_delay"]
                coordinator: DataUpdateCoordinator = store["fast"]

                async def _delayed_refresh(coord=coordinator, d=use_delay):
                    if d > 0:
                        await asyncio.sleep(d)
                    await coord.async_request_refresh()

                hass.async_create_task(_delayed_refresh())

        hass.services.async_register(
            DOMAIN, SERVICE_REFRESH, _handle_refresh, schema=SERVICE_REFRESH_SCHEMA
        )

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH)
    return unloaded
