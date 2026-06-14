"""Config flow para Tuya Lock Open Logs."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_DEVICE_ID,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    REGIONS,
)
from .tuya_api import TuyaAPI


class TuyaLockLogsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            api = TuyaAPI(
                REGIONS[user_input[CONF_REGION]],
                user_input[CONF_ACCESS_ID],
                user_input[CONF_ACCESS_SECRET],
            )
            try:
                await self.hass.async_add_executor_job(
                    api.get_last_open_log, user_input[CONF_DEVICE_ID]
                )
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Tuya Lock Open Logs", data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_ACCESS_ID): str,
                vol.Required(CONF_ACCESS_SECRET): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_REGION, default="us"): vol.In(list(REGIONS.keys())),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.Coerce(int),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
