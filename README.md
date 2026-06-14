# Tuya Lock Open Logs

Integración para Home Assistant (instalable vía HACS como repositorio personalizado)
que crea un sensor con el **último registro de apertura física** de una chapa Tuya
(huella, tarjeta, contraseña, llave, app, etc.).

No usa ni habilita el desbloqueo remoto: solo consulta el endpoint de
`open-logs` (historial de aperturas) de la Tuya Cloud API.

## Requisitos

1. Proyecto creado en [Tuya IoT Platform](https://iot.tuya.com/) (Cloud Development).
2. **Access ID / Client ID** y **Access Secret** del proyecto.
3. El dispositivo (chapa) vinculado a tu cuenta y autorizado en el proyecto
   (pestaña *Devices* → *Link Tuya App Account*, o *Asset* → vincular el activo).
4. Suscripción a la API **Smart Lock Open API** dentro del proyecto
   (en "Service API" / "Subscribe API"), si no está habilitada por defecto.
5. El **Device ID** de la chapa (se ve en *Devices* dentro del proyecto).
6. Centro de datos: **América (Western America)**.

## Instalación

1. En HACS → Integraciones → menú (⋮) → *Repositorios personalizados* → agrega
   la URL de este repositorio.
2. Instala "Tuya Lock Open Logs" y reinicia Home Assistant.
3. Ajustes → Dispositivos y servicios → Agregar integración → "Tuya Lock Open Logs".
4. Captura `Access ID`, `Access Secret`, `Device ID` y selecciona región
   (América / us).

## Entidad creada

- `sensor.<entrada>_ultima_apertura`
  - **Estado**: nombre configurado para el método de apertura (ej. "Miguel"),
    o el nombre genérico del método si no tiene nombre (ej. "Huella").
  - **Atributos**: `metodo`, `metodo_raw`, `user_id`, `hora` (UTC ISO 8601),
    `raw` (registro completo devuelto por Tuya).

## Notas

- Por defecto consulta cada 5 minutos (`scan_interval`, configurable durante
  el alta de la integración).
- Solo lee `open-logs`; no se solicitan permisos de control remoto.
- Si la API responde error de credenciales o "permission deny", revisa que la
  API "Smart Lock" esté suscrita en el proyecto y que el dispositivo esté
  vinculado/autorizado.
