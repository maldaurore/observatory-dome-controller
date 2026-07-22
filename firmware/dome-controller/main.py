import json
import time
from base import Base
from mqtt_client import client

device = Base(client)

COMMANDS = {
    "abortslew": device.abortSlew,
    "findhome": device.findHome,
    "park": device.park,
    "slewtoazimuth": device.slewToAzimuth,
    "get_state": device.getState
}

def on_message(client, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        cmd = payload.get("cmd")
    
        if cmd in COMMANDS:
            handler = COMMANDS[cmd]
            return handler(payload)
    
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
    
def main():
    client.on_message = on_message

    print("Dispositivo listo.")

    try:
        while True:
            try:
                client.loop_once()
                device.update()
            except OSError as e:
                print("OSError:", e)
                client.reconnect()

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Cerrando...")
        device.abortSlew()

    except Exception:
        pass

if __name__ == "__main__":
    main()
