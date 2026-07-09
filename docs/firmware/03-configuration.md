# Firmware Configuration

This document describes how to configure the ESP32 controllers.

---

## Configuration File

Both the dome and shutter controllers use a configuration file named:

```text
config.json
```

This file is intentionally excluded from the repository because it contains network-specific settings.

Instead, each firmware directory contains a template file named:

```text
config.example.json
```

Create a copy of this file and rename it to:

```text
config.json
```

The file has the following structure:

```json
{
    "ssid": "SSID",
    "password": "password",
    "mqtt_broker_host": "255.255.255.255",
    "mqtt_broker_port": 1883
}
```

Replace the placeholder values with the appropriate network configuration.

| Field | Description |
|------|------|
| `ssid` | Wi-Fi network name. |
| `password` | Wi-Fi network password. |
| `mqtt_broker_host` | IP address of the computer running the MQTT broker. |
| `mqtt_broker_port` | MQTT broker port. The default value is `1883`. |

---

## Upload the Configuration

After editing `config.json`, copy it to the ESP32 using `mpremote`:

```bash
mpremote connect PORTNAME fs cp config.json :
```

Repeat this procedure for both controllers.

Restart each ESP32 after copying the file for the changes to take effect.

---

## Updating the Configuration

Whenever the Wi-Fi network, MQTT broker address, or MQTT port changes, the `config.json` file must be updated and uploaded again to each controller.

Reflashing the firmware is **not** required when only the configuration changes.