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
    changeEtatLumiere(acceleration_x)


def changeEtatLumiere(accel_x):
    global etatLumiere
    if accel_x > 0.5 and etatLumiere == False:
        etatLumiere = True
        print("Lumiere Allumee")
        pycom.rgbled(blanc)

    elif accel_x < -0.5 and etatLumiere == True:
        etatLumiere = False
        print("Lumiere Eteinte")
        pycom.rgbled(ledOFF)
    time.sleep(2)

# réception d'un message sur le topic de televiseur
def on_televiseur_message(client, userdata, msg):
    acceleration_y = float(msg.payload)

    # action à effectuer
    changeEtatTele(acceleration_y)

def changeEtatTele(accel_y):
    global etatTele
    if accel_y > 0.5 and etatTele == False:
        etatTele = True
        print("Tele Allumee")
        pycom.rgbled(rouge)

    elif accel_y < -0.5 and etatTele == True:
        etatTele = False
        print("Tele Eteinte")
        pycom.rgbled(ledOFF)
    time.sleep(2)
    
# réception d'un message sur le topic de chaine
def on_chaine_message(client, userdata, msg):
    acceleration_z = float(msg.payload)

    # action à effectuer
    changerChaine(acceleration_z)

def changerChaine(accel_z):
    global index
    if etatTele == True:
        current_index = index % len(liste)
        if accel_z > 0.5:
            index += 1
            if index == len(liste):
                # Revenir au début de la liste si on atteint la fin
                index = 0
            print("Chaine +1")  
            
        elif accel_z < -0.5:
            index -= 1
            if index < 0:
                # Revenir à la fin de la liste si on atteint le début
                index = len(liste) - 1 
            print("Chaine -1")

        pycom.rgbled(liste[current_index])
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