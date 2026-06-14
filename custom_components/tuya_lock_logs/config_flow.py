"""Config flow para Tuya Lock Open Logs."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

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
)
from .tuya_api import TuyaAPI


def _options_schema(current: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_FAST_SCAN_INTERVAL,
                default=current.get(CONF_FAST_SCAN_INTERVAL, DEFAULT_FAST_SCAN_INTERVAL),
            ): vol.Coerce(int),
            vol.Optional(
                CONF_SLOW_SCAN_INTERVAL,
                default=current.get(CONF_SLOW_SCAN_INTERVAL, DEFAULT_SLOW_SCAN_INTERVAL),
            ): vol.Coerce(int),
            vol.Optional(
                CONF_TRIGGER_DELAY,
                default=current.get(CONF_TRIGGER_DELAY, DEFAULT_TRIGGER_DELAY),
            ): vol.Coerce(int),
        }
    )


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
                from homeassistant.util import dt as dt_util

                today_start_ms = int(dt_util.start_of_local_day().timestamp() * 1000)
                await self.hass.async_add_executor_job(
                    api.get_open_summary, user_input[CONF_DEVICE_ID], today_start_ms
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
            }
        ).extend(_options_schema({}).schema)

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TuyaLockLogsOptionsFlow()


class TuyaLockLogsOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init", data_schema=_options_schema(current)
        )
