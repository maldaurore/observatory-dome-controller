# Dome Controller Firmware

This document describes how to install and update the firmware of the dome controller ESP32.

> **Important**
>
> The dome controller requires a custom MicroPython firmware included in this repository. The official MicroPython firmware does not include the encoder driver required by the dome controller.
>
> The custom firmware binary is located in this directory:
>
> ```text
> firmware/dome-controller/firmware-dome.bin
> ```

---

## Flash the Firmware

This procedure is only required when:

- Replacing the ESP32 board.
- Recovering a corrupted firmware installation.

Routine software updates do **not** require reflashing the firmware. In those cases, only the MicroPython source files need to be copied to the ESP32 filesystem as described in the next section.


Connect the ESP32 to the computer using a USB cable.

Open a terminal in the `firmware/dome-controller` directory.

First, erase the flash memory:

```bash
esptool.py erase_flash
```

If the serial port cannot be detected automatically, specify it explicitly:

```bash
esptool.py --port PORTNAME erase_flash
```

Once the flash memory has been erased, install the custom firmware:

```bash
esptool.py --baud 460800 write_flash 0x1000 firmware-dome.bin
```

If necessary, specify the serial port:

```bash
esptool.py --port PORTNAME --baud 460800 write_flash 0x1000 firmware-dome.bin
```

For additional information about MicroPython on the ESP32, refer to the official documentation:

https://micropython.org/download/ESP32_GENERIC/

---

## Upload the Source Files

After flashing the firmware, copy the project files to the ESP32 filesystem.

The following files must be uploaded:

- `boot.py`
- `main.py`
- `base.py`
- `config.py`
- `config.json`
- `mqtt_client.py`

Each file can be copied using:

```bash
mpremote connect PORTNAME fs cp filename.py :
```

For example:

```bash
mpremote connect COM5 fs cp main.py :
```

Repeat the procedure until all required files have been copied.

---

## Restart the Controller

After modifying any file on the ESP32 filesystem, restart the board.

This can be done by:

- Pressing the **RESET** button on the ESP32.
- Disconnecting and reconnecting its power supply.

The new firmware or updated files will not take effect until the controller has been restarted.

---

## Verify the Installation

Open a MicroPython REPL:

```bash
mpremote connect PORTNAME
```

Restart the controller.

The boot log should display messages similar to:

```text
Conectando a red Wi.Fi...
Conexión exitosa
Configuración IP: (...)
Conectando al broker MQTT en <broker_ip>...
Conectado al broker MQTT
Suscrito a b'dome/base/commands'
Dispositivo listo.
```

The controller is ready for operation once the message:

```text
Dispositivo listo.
```

is displayed.

---

## Next Step

Continue with **02-shutter-controller.md**.