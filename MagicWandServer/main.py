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
# sd = SD()
# os.mount(sd, '/sd')
# f = open('/sd/gps-record.txt', 'w')

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
mqtt_topic_roll = "paulort31@laposte.net/roll"
mqtt_topic_pitch = "paulort31@laposte.net/pitch"
mqtt_topic_lumiere = "paulort31@laposte.net/lumiere"
mqtt_topic_televiseur = "paulort31@laposte.net/televiseur"
mqtt_topic_chaine = "paulort31@laposte.net/chaine"


client = MQTTClient("device_id", "maqiatto.com",user="paulort31@laposte.net", password="auzeville31", port=1883)

client.set_callback(sub_cb)
client.connect()
print("connected")
client.subscribe(topic=mqtt_topic_roll)
print("subbed")

while (True):

    pitch = int(acc.pitch())
    roll = int(acc.roll())
    acceleration = int(acc.acceleration())
    acceleration_x = acceleration[0]
    acceleration_y = acceleration[1]
    acceleration_z = acceleration[2]
    client.publish(topic=mqtt_topic_roll, msg=str(roll))
    client.publish(topic=mqtt_topic_lumiere, msg="ON")

    # mqtt_client.publish(mqtt_topic_roll, payload=str(roll),qos=0, retain=True)
    # mqtt_client.publish(mqtt_topic_pitch, payload=str(pitch),qos=0, retain=True)
    # mqtt_client.publish(mqtt_topic_lumiere, payload=str(acceleration_x),qos=0, retain=True)
    # mqtt_client.publish(mqtt_topic_televiseur, payload=str(acceleration_y),qos=0, retain=True)
    # mqtt_client.publish(mqtt_topic_chaine, payload=str(acceleration_z),qos=0, retain=True)


    liste = [pitch,roll,acceleration_x,acceleration_y,acceleration_z]
    print(liste)
    
# Arrêt du client MQTT
mqtt_client.loop_stop()
mqtt_client.disconnect()
