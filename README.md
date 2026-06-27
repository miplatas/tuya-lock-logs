# Tuya Lock Open Logs

Home Assistant integration (installable via HACS as a custom repository) that
creates a sensor with the **latest physical unlock event** from a Tuya lock
(fingerprint, card, password, mechanical key, app, etc.).

It does not use or enable remote unlocking: it only queries the Tuya Cloud API
`open-logs` endpoint (unlock history).

## Image examples

These images are included in the repository as visual references for the integration:

| File | Description | Preview |
|---|---|---|
| `images/test1.png` | Example of the Home Assistant sensors created by the integration. | <img src="https://raw.githubusercontent.com/miplatas/tuya-lock-logs/main/images/test1.png" alt="Sensors example" width="220" /> |


## Requirements

1. A project created in [Tuya IoT Platform](https://iot.tuya.com/) (Cloud Development).
2. **Access ID / Client ID** and **Access Secret** for the project.
3. The lock device linked to your account and authorized in the project
   (*Devices* → *Link Tuya App Account*, or *Asset* → link the asset).
4. Subscription to the **Smart Lock Open API** within the project
   (in "Service API" / "Subscribe API"), if it is not enabled by default.
5. The lock **Device ID** (visible under *Devices* in the project).
6. Data center: **America (Western America)**.

## Installation

1. In HACS → Integrations → menu (⋮) → *Custom repositories* → add the URL of
   this repository.
2. Install "Tuya Lock Open Logs" and restart Home Assistant.
3. Settings → Devices & services → Add integration → "Tuya Lock Open Logs".
4. Enter `Access ID`, `Access Secret`, `Device ID`, and select the region
   (America / us).

## Created entities

- `sensor.<entry>_last_open`
   - **State**: the configured name for the unlock method (e.g. "Michael"), or
      the generic method name if it has no custom name (e.g. "Fingerprint", "Password").
   - **Attributes**: `method`, `method_raw`, `user`, `user_id`, `time` (UTC ISO
      8601), `raw` (full record returned by Tuya).
- `sensor.<entry>_last_open_time`
   - **State**: the timestamp of the most recent unlock event.
- `sensor.<entry>_battery`
   - **State**: the lock battery level as a percentage when Tuya exposes a
      numeric battery value, or a mapped percentage when it exposes a battery
      state such as `high`, `medium`, or `low`.

## Notes

- By default it polls every 5 minutes (`scan_interval`, configurable during
  setup).
- It only reads `open-logs`; no remote control permissions are requested.
- If the API returns a credentials error or "permission deny", make sure the
  "Smart Lock" API is subscribed in the project and that the device is linked
  and authorized.
