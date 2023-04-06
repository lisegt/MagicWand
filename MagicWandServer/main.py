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

wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid='Skidblacknir', auth=(WLAN.WPA2, 'maissurtoutpourmoi'))

print("connecting", end='')
while not wlan.isconnected():
    time.sleep(0.25)
    print(".", end='')

print(wlan.ifconfig())

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 1024        # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()

while (True):

    pitch = int(acc.pitch())
    roll = int(acc.roll())
    liste = [pitch,roll]
    
    conn.send(bytearray(liste))
