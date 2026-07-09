# Prerequisites

This document lists the software required to install, configure, and maintain the Observatory Dome Controller.

Before continuing with the installation, ensure that the following software is installed on the control computer.

## Required Software

### Git

Git is required to clone the project repository and obtain future updates.

> Installation: *https://git-scm.com/install/*

---

### Python

Install the latest stable version of Python.

During installation, make sure to enable the "**Add Python to PATH**" option.

> Installation: *https://www.python.org/downloads/*

To verify the installation, open a terminal and run:

```bash
python --version
```

---

### ASCOM Platform

Install the latest version of the ASCOM Platform.

This provides the ASCOM Device Hub, which is a useful tool to control the dome.

> Installation: *https://ascom-standards.org/Downloads/Index.htm*

---

### Eclipse Mosquitto

Install the latest version of Eclipse Mosquitto.

**Important:** During installation, enable the option to install Mosquitto as a Windows service.

> Installation: *https://mosquitto.org/download/*

---

## Firmware Maintenance Tools

The following tools are only required when installing or updating the firmware on the ESP32 controllers.

### esptool

`esptool` is used to flash MicroPython firmware onto the ESP32 boards.

The latest stable esptool release can be installed from PyPI via pip:

```bash
pip install esptool
```

After installation, verify that the tool is available by running:

```bash
esptool version
```

or

```bash
python -m esptool version
```

---

### mpremote

`mpremote` is used to copy files to the ESP32 filesystem and interact with a MicroPython device from the host computer.

It can be installed from PyPI via pip:

```bash
pip install --user mpremote
```

After installation, verify that the tool is available by running:

```bash
mpremote
```

---

## Next Step

Continue with: **02-mosquitto.md** to configure the MQTT broker used by the dome controller.