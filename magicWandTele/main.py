import socket
import time
from mqtt import MQTTClient
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

# callback quand le client reçoit une réponse du broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("gestion_televiseur")

# réception d'un message sur le topic lumiere
def on_gestion_televiseur_message(client, userdata, msg):

    global index
    index = index % len(liste)

    etatTele = msg.payload.decode()
    print(msg.topic+" "+str(msg.payload))

    # allumage/extinction de la TV
    if etatTele == "ON":
        pycom.rgbled(rouge)

    elif etatTele == "OFF":
        pycom.rgbled(noir)

    # gestion des chaînes
    if etatTele == "Monter":

        index += 1
        if index == len(liste):
            # Revenir au début de la liste si on atteint la fin
            index = 0
        print("Chaine +1") 

    elif etatTele == "Descendre":

        index -= 1
        if index < 0:
            # Revenir à la fin de la liste si on atteint le début
            index = len(liste) - 1 
        print("Chaine -1")

    pycom.rgbled(liste[index])
    time.sleep(2)
    

# Initilisation du client MQTT
client = MQTTClient("device_id", "loraserver.tetaneutral.net")
client.connect()
print("connected")
client.set_callback(on_gestion_televiseur_message)
client.subscribe(topic="gestion_televiseur")
print("subbed")

client.loop_forever()