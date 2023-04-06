from selenium import webdriver
import socket
import time
import paho.mqtt.client as mqtt
import pycom

import usocket
import socket
import machine
import math
import network
import os
import time
import utime
import gc
from machine import RTC
from machine import SD
from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12
from pytrack import Pytrack
from network import WLAN
from mqtt import MQTTClient

time.sleep(2)
gc.enable()

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

py = Pytrack()
l76 = L76GNSS(py, timeout=30)
acc = LIS2HH12()

def sub_cb(topic, msg):
   print("found")
   print(msg)

wlan = WLAN(mode=WLAN.STA)
#wlan.connect("yourwifinetwork", auth=(WLAN.WPA2, "wifipassword"), timeout=5000)
wlan.connect(ssid='WiFi-Paul', auth=(WLAN.WPA2, "sqoualala"))

while not wlan.isconnected():
    #machine.idle()
    print(".",end="")
    time.sleep(2)
print("Connected to WiFi\n")

# Déclaration des topics
mqtt_topic_gestion_lumiere = "paulort31@laposte.net/gestion_lumiere"
mqtt_topic_gestion_televiseur = "paulort31@laposte.net/gestion_televiseur"
mqtt_topic_gestion_chaine = "paulort31@laposte.net/gestion_chaine"

client = MQTTClient("device_id", "maqiatto.com",user="paulort31@laposte.net", password="auzeville31", port=1883)

client.set_callback(sub_cb)
client.connect()
print("connected")



# Variables pour la navigation web
# browser = webdriver.Firefox()
# browser.get("http://www.worldslongestwebsite.com")
# browser.maximize_window()
# last_height = 0

roll = 0.0
pitch = 0.0

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
    client.subscribe("paulort31@laposte.net/lumiere")
    client.subscribe("paulort31@laposte.net/televiseur")
    client.subscribe("paulort31@laposte.net/chaine")
    client.subscribe("paulort31@laposte.net/roll")
    client.subscribe("paulort31@laposte.net/pitch")

###### IMPLEMENTATION DES FONCTIONNALITES PAGES WEB ##########

# réception d'un message sur le topic roll
def on_roll_message(client, userdata, msg):
    global roll
    roll = float(msg.payload)

    # action à effectuer
    update_navigateur()

# réception d'un message sur le topic roll
def on_pitch_message(client, userdata, msg):
    global pitch
    pitch = float(msg.payload)

    # action à effectuer
    update_navigateur()

def update_navigateur() :

    global roll, browser

    if roll > 150:
        roll = roll - 256

    if pitch > 150:
        pitch = pitch - 256

    if browser is not None:

        if pitch <= -60:
            new_height = last_height + 100
            browser.execute_script("window.scrollTo(" + str(last_height) + "," + str(new_height) + ")")
            last_height = new_height

        if pitch >= 45:
            new_height = last_height - 100
            browser.execute_script("window.scrollTo(" + str(last_height) + "," + str(new_height) + ")")
            last_height = new_height

        if roll >= 80:
            browser.close()
            browser = None
    elif roll <= -60:
        browser = webdriver.Firefox()
        browser.get("http://www.worldslongestwebsite.com")
        browser.maximize_window()
        time.sleep(5)
        

###### FIN IMPLEMENTATION DES FONCTIONNALITES PAGES WEB ##########

# réception d'un message sur le topic lumiere
def on_lumiere_message(client, userdata, msg):
    acceleration_x = float(msg.payload)
    print(msg.topic+" "+str(msg.payload))

    # action à effectuer
    global etatLumiere
    if acceleration_x > 0.5 and etatLumiere == False:
        client.publish(topic=mqtt_topic_gestion_lumiere, msg="ON")
        etatLumiere = True
        print("Lumiere Allumee")

    elif acceleration_x > 0.5 and etatLumiere == True:
        client.publish(topic=mqtt_topic_gestion_lumiere, msg="OFF")
        etatLumiere = False
        print("Lumiere Eteinte")

    time.sleep(2)

# réception d'un message sur le topic de televiseur
def on_televiseur_message(client, userdata, msg):
    acceleration_y = float(msg.payload)

    # action à effectuer
    global etatTele
    if acceleration_y > 0.5 and etatTele == False:
        client.publish(topic=mqtt_topic_gestion_televiseur, msg="ON")
        etatTele = True
        print("Tele Allumee")

    elif acceleration_y > 0.5 and etatTele == True:
        client.publish(topic=mqtt_topic_gestion_televiseur, msg="OFF")
        etatTele = False
        print("Tele Eteinte")

    time.sleep(2)
    
# réception d'un message sur le topic de chaine
def on_chaine_message(client, userdata, msg):
    acceleration_z = float(msg.payload)

    global index
    if etatTele == True:

        if acceleration_z > 0.5:
            client.publish(topic=mqtt_topic_gestion_televiseur, msg="Monter")
            print("Chaine +1")  
            
        elif acceleration_z < -0.5:
            client.publish(topic=mqtt_topic_gestion_televiseur, msg="Descendre")
            print("Chaine -1")
        time.sleep(2)
    else:
        print("Veuillez allumer le téléviseur")



# Initilisation du client MQTT
client = mqtt.Client()
client.username_pw_set(username="paulort31@laposte.net",password="auzeville31")
client.on_connect = on_connect
client.message_callback_add("paulort31@laposte.net/lumiere", on_lumiere_message)
client.message_callback_add("paulort31@laposte.net/televiseur", on_televiseur_message)
client.message_callback_add("paulort31@laposte.net/chaine", on_chaine_message)

client.connect("maqiatto.com", 1883, 60)

client.loop_forever()