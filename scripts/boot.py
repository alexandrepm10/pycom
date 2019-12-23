import pycom
from network import WLAN
import time
import machine
from machine import Pin
import pycom
import sys
from network import LoRa
import socket

try:
    from pymesh_config import PymeshConfig
except:
    from _pymesh_config import PymeshConfig

try:
    from pymesh import Pymesh
except:
    from _pymesh import Pymesh


HOST = '192.168.1.86'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


def new_message_cb(rcv_ip, rcv_port, rcv_data):
    ''' callback triggered when a new packet arrived '''
    print('Incoming %d bytes from %s (port %d):' %
            (len(rcv_data), rcv_ip, rcv_port))
    print(rcv_data)

    # user code to be inserted, to send packet to the designated Mesh-external interface
    for _ in range(3):
        pycom.rgbled(0x888888)
        time.sleep(.2)
        pycom.rgbled(0)
        time.sleep(.1)
    return

wlan = WLAN(mode=WLAN.STA)
Pin('P12', mode=Pin.OUT)(True)
wlan.antenna(WLAN.EXT_ANT)
nets = wlan.scan()
for net in nets:
    if net.ssid == 'Home-Marques':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'MARQUES65'), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        print('IP - MASK - ROUTER - DNS')
        print(wlan.ifconfig())
        break
    else:
        print('Network not found!')
        break

pycom.heartbeat(False)

# read config file, or set default values
pymesh_config = PymeshConfig.read_config()

#initialize Pymesh
pymesh = Pymesh(pymesh_config, new_message_cb)

mac = pymesh.mac()
# based on LoRa MAC address, some nodes could be forced to be
# sleep-end-devices (always Child) or to have increased Leader priority
# if mac > 10:
#     pymesh.end_device(True)
# elif mac == 5:
#     pymesh.leader_priority(255)

# while not pymesh.is_connected():
#     print(pymesh.status_str())
#     time.sleep(3)

# send message to the Node having MAC address 5
pymesh.send_mess(5, "Hello World")

# def new_br_message_cb(rcv_ip, rcv_port, rcv_data, dest_ip, dest_port):
#     ''' callback triggered when a new packet arrived for the current Border Router,
#     having destination an IP which is external from Mesh '''
#     print('Incoming %d bytes from %s (port %d), to external IPv6 %s (port %d)' %
#             (len(rcv_data), rcv_ip, rcv_port, dest_ip, dest_port))
#     print(rcv_data)

#     # user code to be inserted, to send packet to the designated Mesh-external interface
#     # ...
#     return

# add current node as Border Router, with a priority and a message handler callback
# pymesh.br_set(PymeshConfig.BR_PRIORITY_NORM, new_br_message_cb)

# remove Border Router function from current node
#pymesh.br_remove()

# send data for Mesh-external, basically to the BR
# ip = "1:2:3::4"
# port = 5555
# pymesh.send_mess_external(ip, port, "Hello World")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)

print("done Pymesh init, forever loop, exit/stop with Ctrl+C multiple times")
# set BR with callback

while True:
    time.sleep(3)