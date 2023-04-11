from mqtt import MQTTClient
from network import WLAN
import machine
import time
import pycom

# Variables pour les couleurs de la LED
rouge = 0xFF0000
vert = 0x00FF00
orange = 0xFF9900
bleu = 0x0000FF
violet = 0x9900FF
noir = 0x000000

liste = [rouge, bleu, vert, orange, violet]
start_value = rouge

ledOFF = noir
etatTele = False
etatLumiere = False

index = liste.index(start_value)

# Désactivation du clignotement de 'base' de la LED 
pycom.heartbeat(False)

def sub_cb(topic, msg):
    print("found")
    print(msg.decode())
    if msg.decode() == "ON":
        print("test")
        pycom.rgbled(rouge)

    elif msg.decode() == "OFF":
        pycom.rgbled(noir)
    
    elif msg.decode() == "Monter":
        index += 1
        if index == len(liste):
            # Revenir au début de la liste si on atteint la fin
            index = 0
        print("Chaine +1")
        pycom.rgbled(liste[index])
        time.sleep(2)

    elif msg.decode() == "Descendre":
        index -= 1
        if index < 0:
            # Revenir à la fin de la liste si on atteint le début
            index = len(liste) - 1 
        print("Chaine -1")
        pycom.rgbled(liste[index])
        time.sleep(2)


wlan = WLAN(mode=WLAN.STA)
#wlan.connect("yourwifinetwork", auth=(WLAN.WPA2, "wifipassword"), timeout=5000)
wlan.connect(ssid="WiFi-Paul", auth=(WLAN.WPA2, "sqoualala"))

while not wlan.isconnected():
    #machine.idle()
    print(".",end="")
    time.sleep(2)
print("Connected to WiFi\n")

# Déclaration des topics
mqtt_topic_tele = "gestion_tele"

# Initilisation du client MQTT
client = MQTTClient("device_id", "loraserver.tetaneutral.net")
client.connect()
print("connected")
client.set_callback(sub_cb)
client.subscribe(topic=mqtt_topic_tele)
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
