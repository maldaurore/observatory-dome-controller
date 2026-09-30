import json
import time
from base import Base
from mqtt_client import client
from machine import Pin, Encoder
import sys

LOG_FILE = "error.log"

device = Base(client)

COMMANDS = {
    "abortslew": device.abortSlew,
    "findhome": device.findHome,
    "park": device.park,
    "slewtoazimuth": device.slewToAzimuth,
    "getstate": device.getState,
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
    
        if cmd in COMMANDS:
            if device.hasError() and cmd not in ("clearerror", "getstate", "abortslew"):
                return
            handler = COMMANDS[cmd]
            return handler(payload)
    
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
                print("MQTT desconectado:", e)
                client.connected = False

            except Exception as e:
                log_error("mqtt/loop", e)

            try:
                device.update()

            except Exception as e:
                device.setError(1284)
                log_error("main/update", e)

            # Si el domo está idle y MQTT desconectado,
            # se puede entrar en un reconnect() bloqueante
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

def medir_pulsos_por_vuelta(self, vueltas=10):
    encoder = device.encoder
    home_sensor = Pin(14, Pin.IN, Pin.PULL_UP)

    DEBOUNCE_MS = 1000

    cuentas = []

    print("Esperando punto HOME...")

    # Esperar a que el sensor esté activo
    while home_sensor.value():
        pass

    # Esperar a salir del sensor
    while not home_sensor.value():
        pass

    encoder.value(0)
    ultimo_disparo = time.ticks_ms()

    print("Iniciando medición...")

    while len(cuentas) < vueltas:

        if not home_sensor.value():

            ahora = time.ticks_ms()

            if time.ticks_diff(ahora, ultimo_disparo) > DEBOUNCE_MS:

                pulsos = encoder.value()

                cuentas.append(pulsos)

                print(f"Vuelta {len(cuentas)}: {pulsos} pulsos")

                encoder.value(0)

                ultimo_disparo = ahora

                # Esperar a abandonar el sensor para no contar dos veces
                while not home_sensor.value():
                    pass

    promedio = sum(cuentas) / len(cuentas)

    print("\nResultados:")
    for i, c in enumerate(cuentas, 1):
        print(f"Vuelta {i}: {c}")

    print(f"\nPromedio: {promedio:.2f} pulsos/vuelta")

    return promedio, cuentas