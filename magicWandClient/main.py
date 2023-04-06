from selenium import webdriver
import socket
import time

HOST = '192.168.0.117'  # The server's hostname or IP address
PORT = 1024  # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected !")

browser = webdriver.Firefox()
browser.get("http://www.worldslongestwebsite.com")
browser.maximize_window()
last_height = 0

while True:

    data = s.recv(1024)

    pitch = data[0]
    roll = data[1]
    # acceleration_x = data[2]
    # acceleration_y = data[3]
    # acceleration_z = data[4]

    # print("Acceleration" acceleration_x)
    # print(acceleration_y)
    # print(acceleration_z)




# ancien code
    if pitch > 150:
        pitch = pitch - 256
    if roll > 150:
        roll = roll - 256

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
