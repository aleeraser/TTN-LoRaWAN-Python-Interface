#!/usr/bin/env python3

import base64
import datetime
import json
import os
import random
import socket
import sys
import time

import LoRaWAN
from LoRaWAN.MHDR import MHDR

UDP_IP = "router.eu.thethings.network"
UDP_PORT = 1700

start = '01'
rand_token = '3443'
sender_mac = 'a0481cffff0c9f1b'  # Device on which you run this code == Gateway EUI
zero = '00'

devaddr = [0x26, 0x01, 0x17, 0x8C]
nwskey = [0x86, 0x76, 0x5D, 0xD1, 0xD2, 0x26, 0x04, 0x65, 0xB7, 0x31, 0x6E, 0x13, 0xC3, 0xB3, 0x79, 0xE0]
appskey = [0xF5, 0x38, 0xDA, 0x40, 0x24, 0x7A, 0x85, 0x6F, 0x63, 0x65, 0xA2, 0x23, 0xAD, 0x68, 0x3B, 0x1A]

while True:
    msg = str(100 + int(random.random() * 100))
    lorawan = LoRaWAN.new(nwskey, appskey)
    lorawan.create(MHDR.UNCONF_DATA_UP, {'devaddr': devaddr, 'fcnt': 1, 'data': list(map(ord, msg))})

    raw = lorawan.to_raw()

    print(msg)
    raw = bytearray(raw)
    msg = base64.b64encode(raw)

    # TTN Json Msg
    data = {"rxpk": [
        {
            "tmst": int(time.time()),
            "chan": 0,
            "rfch": 0,
            "freq": 868.1,
            "stat": 1,
            "modu": "LORA",
            "datr": "SF7BW125",
            "codr": "4/5",
            "lsnr": 9,
            'data': msg.decode('utf-8')
        }]
    }

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP

    content = bytes.fromhex(start + rand_token + zero + sender_mac) + json.dumps(data).encode()
    print(content)

    sock.sendto(content, (UDP_IP, UDP_PORT))

    time.sleep(5)
