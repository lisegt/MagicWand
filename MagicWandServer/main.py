#!/usr/bin/env python
#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

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

etatTele = False
etatLumiere = False

gc.enable()

#setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

py = Pytrack()
l76 = L76GNSS(py, timeout=30)
time.sleep(1)
# sd = SD()
# os.mount(sd, '/sd')
# f = open('/sd/gps-record.txt', 'w')

py = Pytrack()
accelerometer = LIS2HH12()

def sub_cb(topic, msg):
   print("found")
   print(msg)

wlan = WLAN(mode=WLAN.STA)
#wlan.connect("yourwifinetwork", auth=(WLAN.WPA2, "wifipassword"), timeout=5000)
wlan.connect(ssid="WiFi-Paul", auth=(WLAN.WPA2, "sqoualala"))

while not wlan.isconnected():
    #machine.idle()
    print(".",end="")
    time.sleep(2)
print("Connected to WiFi\n")

# Déclaration des topics
mqtt_topic_roll = "paulort31@laposte.net/roll"
mqtt_topic_pitch = "paulort31@laposte.net/pitch"
mqtt_topic_lumiere = "paulort31@laposte.net/lumiere"
mqtt_topic_televiseur = "paulort31@laposte.net/televiseur"
mqtt_topic_chaine = "paulort31@laposte.net/chaine"

mqtt_topic_gestion_lumiere = "paulort31@laposte.net/gestion_lumiere"
mqtt_topic_gestion_televiseur = "paulort31@laposte.net/gestion_televiseur"

#Connexion au brocker MQTT sui MaQiaTTo
print("connexion mqtt")
client = MQTTClient("device_id", "maqiatto.com",user="paulort31@laposte.net", password="auzeville31", port=1883)

print("subscribe mqtt")
client.set_callback(sub_cb)
client.connect()
print("connected")

#Boucle infini
while (True):
    #Récupération des données capteur
    roll = accelerometer.roll()
    pitch = accelerometer.pitch()
    x, y, z = accelerometer.acceleration()

    if (roll > -30 and roll < 30) and (pitch > -30 and pitch < 30):
        if x > 0.35 and etatLumiere == False:
            client.publish(topic=mqtt_topic_gestion_lumiere, msg="ON")
            etatLumiere = True
            print("Lumiere Allumee")
            time.sleep(2)

        elif x > 0.35 and etatLumiere == True:
            client.publish(topic=mqtt_topic_gestion_lumiere, msg="OFF")
            etatLumiere = False
            print("Lumiere Eteinte")
            time.sleep(2)

        if y > 0.35 and etatTele == False:
            client.publish(topic=mqtt_topic_gestion_televiseur, msg="ON")
            etatTele = True
            print("Tele Allumee")
            time.sleep(2)

        elif y > 0.35 and etatTele == True:
            client.publish(topic=mqtt_topic_gestion_televiseur, msg="OFF")
            etatTele = False
            print("Tele Eteinte")
            time.sleep(2)
        
        if etatTele == True:
            if z > 1.35:
                client.publish(topic=mqtt_topic_gestion_televiseur, msg="Monter")
                print("Chaine +1")  
                time.sleep(2)
            elif z < 0.65:
                client.publish(topic=mqtt_topic_gestion_televiseur, msg="Descendre")
                print("Chaine -1")
                time.sleep(2)

    #Envoi des données sur les topics
    client.publish(topic=mqtt_topic_lumiere, msg=str(x))
    client.publish(topic=mqtt_topic_televiseur, msg=str(y))
    client.publish(topic=mqtt_topic_chaine, msg=str(z))
    client.publish(topic=mqtt_topic_roll, msg=str(roll))
    client.publish(topic=mqtt_topic_pitch, msg=str(pitch))

    #Print pour vérifier les données
    print("Acceleration X: {:.2f}, Y: {:.2f}, Z: {:.2f}".format(x, y, z))
    print("Roll: {:.2f} deg, Pitch: {:.2f} deg".format(roll, pitch))

# Arrêt du client MQTT
mqtt_client.loop_stop()
mqtt_client.disconnect()
