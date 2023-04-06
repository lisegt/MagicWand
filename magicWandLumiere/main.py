from selenium import webdriver
import socket
import time
import paho.mqtt.client as mqtt
import pycom

blanc = 0xFFFFFF
noir = 0x000000

# callback quand le client reçoit une réponse du broker MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("paulort31@laposte.net/gestion_lumiere")

# réception d'un message sur le topic lumiere
def on_gestion_lumiere_message(client, userdata, msg):
    etatLumiere = msg.payload.decode()
    print(msg.topic+" "+str(msg.payload))

    if etatLumiere == "ON":
        pycom.rgbled(blanc)

    elif etatLumiere == "OFF":
        pycom.rgbled(noir)

# Initilisation du client MQTT
client = mqtt.Client()
client.username_pw_set(username="paulort31@laposte.net",password="auzeville31")
client.on_connect = on_connect
client.message_callback_add("paulort31@laposte.net/gestion_lumiere", on_gestion_lumiere_message)

client.connect("maqiatto.com", 1883, 60)

client.loop_forever()