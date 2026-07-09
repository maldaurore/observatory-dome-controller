# Shutter Controller Firmware

This document describes how to install and update the firmware of the shutter controller ESP32.

> **Important**
>
> The shutter controller uses the official MicroPython firmware for the ESP32.
>
> The latest firmware can be downloaded from:
>
> https://micropython.org/download/ESP32_GENERIC/

---

## Flash the Firmware

This procedure is only required when:

- Replacing the ESP32 board.
- Recovering a corrupted firmware installation.

Routine software updates do **not** require reflashing the firmware. In those cases, only the MicroPython source files need to be copied to the ESP32 filesystem as described in the next section.

Connect the ESP32 to the computer using a USB cable.

Open a terminal in the `firmware/shutter-controller` directory.

First, erase the flash memory:

```bash
esptool.py erase_flash
```

If the serial port cannot be detected automatically, specify it explicitly:

```bash
esptool.py --port PORTNAME erase_flash
```

Once the flash memory has been erased, install the downloaded MicroPython firmware:

```bash
esptool.py --baud 460800 write_flash 0x1000 ESP32_GENERIC.bin
```

If necessary, specify the serial port:

```bash
esptool.py --port PORTNAME --baud 460800 write_flash 0x1000 ESP32_GENERIC.bin
```

---

## Upload the Source Files

After flashing the firmware, copy the project files to the ESP32 filesystem.

The following files must be uploaded:

- `boot.py`
- `main.py`
- `shutter.py`
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
Conectando a red Astrobio...
Conexión exitosa
Configuración IP: (...)
Conectando al broker MQTT en 192.168.40.xx...
Conectado al broker MQTT
Suscrito a b'dome/shutter/commands'
Dispositivo listo.
```

The controller is ready for operation once the message:

```text
Dispositivo listo.
```

is displayed.

---

## Next Step

Continue with **03-configuration.md**.