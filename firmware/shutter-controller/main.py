import json
import time
from shutter import Shutter
from mqtt_client import client
import sys

LOG_FILE = "error.log"

device = Shutter(client)

COMMANDS = {
    "getstate": device.getState,
    "abortslew": device.abortSlew,
    "openwithoutflap": device.openWithoutFlap,
    "closeshutter": device.close,
    "openshutter": device.open,
    "clearerror": device.clearError,
}

def log_error(context, exc):
    try:
        with open(LOG_FILE, "a") as f:
            f.write("\n")
            f.write("[{}] ERROR: {}\n".format(time.time(), context))
            sys.print_exception(exc, f)

    except Exception:
        pass

def on_message(client, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        cmd = payload.get("cmd")

        print(cmd)
        if cmd in COMMANDS:
            if device.hasError() and cmd not in ("clearerror", "getstate", "abortslew"):
                return
            handler = COMMANDS[cmd]
            return handler()
    
    except Exception as e:
        log_error("on_message", e)

def main():
    client.on_message = on_message

    print("Dispositivo listo.")

    try:
        while True:

            try:
                client.loop_once()

            except OSError as e:
                print("MQTT desconectado: ", e)
                client.connected = False

            except Exception as e:
                log_error("mqtt/loop", e)

            try:
                device.update()

            except Exception as e:
                device.setError(1284)
                log_error("main/update", e)

            if not client.connected and not device.isSlewing():
                client.reconnect()

            time.sleep(0.01)
        
    except KeyboardInterrupt:
        print("Cerrando...")
        device.abortSlew()
    
    except Exception as e:
        log_error("main", e)

if __name__ == "__main__":
    main()
