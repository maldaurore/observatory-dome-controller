from umqtt.simple import MQTTClient
import ujson as json
import time
import network
from config import CONFIG

CLIENT_ID = "dome-base-client"
TOPIC_EVENTS = b"dome/events"
WILL_PAYLOAD = {
    "base_online": False,
}
BROKER_HOST = CONFIG["mqtt_broker_host"] 
BROKER_PORT = CONFIG["mqtt_broker_port"]
TOPIC_COMMANDS = b"dome/base/commands"

class Msg:
    pass

class SimpleMQTTWrapper:

    def __init__(self):
        self.on_message = None
        self.connected = False

        self._client = MQTTClient(
            client_id=CLIENT_ID,
            server=BROKER_HOST,
            port=BROKER_PORT,
            keepalive=30
        )

        self._client.set_last_will(
            TOPIC_EVENTS,
            json.dumps(WILL_PAYLOAD),
            retain=True,
            qos=1
        )

        self._client.set_callback(self._internal_callback)

        print(f"Conectando al broker MQTT en {BROKER_HOST}...")
        self._client.connect()
        print("Conectado al broker MQTT")
        self.connected = True
        self._client.subscribe(TOPIC_COMMANDS)
        print("Suscrito a", TOPIC_COMMANDS)

        self.publish_message(json.dumps({"base_online": True}))

    def _internal_callback(self, topic, msg):
        if self.on_message:

            m = Msg()
            m.topic = topic
            m.payload = msg

            self.on_message(self, m)

    def _create_client(self):
        c = MQTTClient(
            client_id=CLIENT_ID,
            server=BROKER_HOST,
            port=BROKER_PORT,
            keepalive=30
        )
        c.set_last_will(
            TOPIC_EVENTS,
            json.dumps(WILL_PAYLOAD),
            retain=True,
            qos=0
        )
        c.set_callback(self._internal_callback)
        return c

    def publish_message(self, payload):
        if not isinstance(payload, (str, bytes, bytearray)):
            payload = json.dumps(payload)

        self._client.publish(
            TOPIC_EVENTS,
            payload,
            qos=0
        )

    def loop_once(self):
        self._client.check_msg()

    def reconnect(self):
        self.connected = False

        wlan = network.WLAN(network.STA_IF)
        print("Reconectando MQTT...")

        while not wlan.isconnected():
            print("Esperando WiFi...")
            time.sleep(1)

        try:
            self._client.disconnect()
        except:
            pass

        while True:
            try:
                self._client = self._create_client()
                self._client.connect()
                self._client.set_callback(self._internal_callback)
                self._client.subscribe(TOPIC_COMMANDS)
                self.connected = True
                self.publish_message({"base_online": True})
                print("Reconectado")
                break
            except Exception:
                # No es error del controlador.
                # No llamar a log_error()
                print("Broker no disponible, reintentando...")
                time.sleep(1)

client = SimpleMQTTWrapper()
