# Computer Configuration

This document describes the required network configuration for the control computer.

## Static IP Address

The computer running the MQTT broker and the Alpaca server **must** be assigned the following static IPv4 address:

```text
192.168.40.28
```

The ESP32 controllers are configured to connect to the MQTT broker at this address. Assigning a different IP address will prevent them from connecting to the broker.

Refer to the Windows documentation if you need assistance assigning a static IP address.

---

## Using a Different IP Address

If a different IP address is required, the MQTT broker address stored on each ESP32 controller must also be updated.

Each firmware directory contains a file named:

```text
config.example.json
```

Create a copy of this file named:

```text
config.json
```

Then replace the placeholder values with the appropriate network configuration.

Example:

```json
{
    "ssid": "SSID",
    "password": "password",
    "mqtt_broker_host": "255.255.255.255",
    "mqtt_broker_port": 1883
}
```

The `mqtt_broker_host` field must contain the IP address of the computer running the MQTT broker.

After updating the configuration, upload the new `config.json` file to each ESP32 controller. The upload procedure is described in the firmware documentation.

---

## Next Step

Continue with **04-project-installation.md**.