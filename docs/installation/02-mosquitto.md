# Mosquitto Configuration

This document describes the configuration required for Eclipse Mosquitto to allow communication between the control computer and the ESP32 controllers.

## Configure the Broker

The default Mosquitto configuration must be modified to allow the ESP32 controllers to connect to the broker.

Open **Notepad** as Administrator.

Open the Mosquitto configuration file:

```text
C:\Program Files\mosquitto\mosquitto.conf
```

Scroll to the end of the file and add the following lines:

```text
listener 1883
allow_anonymous true
```

These settings enable the MQTT broker to listen on the default MQTT port and allow connections from the ESP32 controllers without authentication.

Save the file.

---

## Restart the Mosquitto Service

The service must be restarted for the configuration changes to take effect.

### PowerShell

```powershell
Restart-Service mosquitto
```

---

## Configure Windows Firewall

Allow inbound TCP connections on port **1883**.

### PowerShell

```powershell
New-NetFirewallRule -DisplayName "Mosquitto MQTT 1883" -Direction Inbound -Protocol TCP -LocalPort 1883 -Action Allow
```

---

## Verify the Service

Verify the service is running and listening on port **1883**.

### PowerShell

```powershell
Test-NetConnection localhost -Port 1883
```

If the broker is running correctly, the output should indicate:

```text
TcpTestSucceeded : True
```

Alternatively, the service status can be verified from PowerShell:

```powershell
Get-Service mosquitto
```

The service should be in the **Running** state.

---

## Next Step

Continue with **03-computer-configuration.md**.