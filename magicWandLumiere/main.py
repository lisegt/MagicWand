from mqtt import MQTTClient
from network import WLAN
import machine
import time
import pycom

blanc = 0xFFFFFF
noir = 0x000000

def sub_cb(topic, msg):
    print("found")
    print(msg.decode())
    if msg.decode() == "ON\n":
        print("test")
        pycom.rgbled(blanc)

    elif msg.decode() == "OFF\n":
        pycom.rgbled(noir)

wlan = WLAN(mode=WLAN.STA)
#wlan.connect("yourwifinetwork", auth=(WLAN.WPA2, "wifipassword"), timeout=5000)
wlan.connect(ssid="WiFi-Paul", auth=(WLAN.WPA2, "sqoualala"))

while not wlan.isconnected():
    #machine.idle()
    print(".",end="")
    time.sleep(2)
print("Connected to WiFi\n")

# Déclaration des topics
mqtt_topic_lumiere = "paulort31@laposte.net/gestion_lumiere"

# Initilisation du client MQTT
client = MQTTClient("device_id", "loraserver.tetaneutral.net")
client.connect()
print("connected")
client.set_callback(sub_cb)
client.subscribe(topic="teste")
print("subbed")

# Désactivation du clignotement de 'base' de la LED 
pycom.heartbeat(False)

# # réception d'un message sur le topic lumiere
# def on_gestion_lumiere_message(client, userdata, msg):
#     etatLumiere = msg.payload.decode()
#     print(msg.topic+" "+str(msg.payload))

#     



while True:
    client.check_msg()
    time.sleep(1)

client.disconnect()