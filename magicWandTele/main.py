from selenium import webdriver
import socket
import time
import paho.mqtt.client as mqtt
import pycom

# Variables pour les couleurs de la LED
rouge = 0xFF0000
vert = 0x00FF00
orange = 0xFF9900
bleu = 0x0000FF
violet = 0x9900FF
noir = 0x000000
blanc = 0xFFFFFF

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
    client.subscribe("paulort31@laposte.net/gestion_televiseur")
    #client.subscribe("paulort31@laposte.net/gestion_chaine")

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
client = mqtt.Client()
client.username_pw_set(username="paulort31@laposte.net",password="auzeville31")
client.on_connect = on_connect
client.message_callback_add("paulort31@laposte.net/gestion_televiseur", on_gestion_televiseur_message)
#client.message_callback_add("paulort31@laposte.net/gestion_chaine", on_gestion_chaine_message)

client.connect("maqiatto.com", 1883, 60)

client.loop_forever()