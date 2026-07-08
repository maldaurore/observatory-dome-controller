import network
import esp
import gc
from config import CONFIG

esp.osdebug(None)
gc.collect()

ssid = CONFIG["ssid"]
password= CONFIG["password"]

print(f"Conectando a red {ssid}...")

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print ("Conexión exitosa")
print(f"Configuración IP: {station.ifconfig()}")