#!/usr/bin/python3

import sys
import os
import datetime
from time import sleep
import random
import base64

import Adafruit_DHT

from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

import LoRaWAN
from LoRaWAN.MHDR import MHDR

# Add path to pyRadioHeadiRF95 module
sys.path.append(os.path.dirname(__file__) + "/../")
import pyRadioHeadRF95 as radio

rf95 = radio.RF95()

rf95.init()

#rf95.setTxPower(14, False)
rf95.setTxPower(20, False)
rf95.setFrequency(434)

rf95.setSignalBandwidth(rf95.Bandwidth125KHZ)
rf95.setSpreadingFactor(rf95.SpreadingFactor7)
rf95.setCodingRate4(rf95.CodingRate4_5)

devaddr = [0x26, 0x01, 0x1D, 0xAC]
nwskey = [0x11, 0x24, 0x22, 0x44, 0x0E, 0x67, 0x72, 0x57, 0x32, 0x02, 0x90, 0x02, 0x9E, 0x2D, 0xEC, 0x2D]
appskey = [0x62, 0x8A, 0x0D, 0xAC, 0x94, 0xAB, 0xDF, 0x17, 0xEE, 0xBB, 0x2F, 0xC0, 0x0E, 0x09, 0xE2, 0x72]

DHTpin = 26
postingDelay = 3
errorSleepTime = 10

t_mean = 1
h_mean = 1
iteration = 0

t_offset = 10
h_offset = 25


def log(msg):
    timestamp = str(datetime.datetime.now())
    with open("log.txt", 'a') as log:
        log.write(timestamp + "\t" + str(msg) + '\n')
    print(timestamp + "\t" + str(msg))


def error(errMsg=None, sleepTime=errorSleepTime):
    if errMsg:
        log("Error: " + str(errMsg))
        log("Sleeping for " + str(sleepTime) + " seconds...")
        sleep(sleepTime)


def loop():
    print("Startup done!")
    while True:
        try:
            # Retrieve data
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHTpin)
            humidity = round(humidity, 2)
            temperature = round(temperature, 2)
            log("Values:\tTemp.: %s\t|\tHumidity: %s" % (str(temperature), str(humidity)))

            global t_mean, h_mean, iteration

            if humidity > 0 or humidity < 100 or temperature > 0 or temperature < 45:
                if (temperature < t_mean - t_offset or temperature > t_mean + t_offset) and iteration > 0:
                    error("Temperature too broad from mean. Discarding value")
                elif (humidity < h_mean - h_offset or humidity > h_mean + h_offset) and iteration > 0:
                    error("Humidity too broad from mean. Discarding value")
                else:
                    iteration += 1
                    t_mean = round((t_mean * (iteration - 1) + temperature) / iteration, 2)
                    h_mean = round((h_mean * (iteration - 1) + humidity) / iteration, 2)

                    log("Mean:\tTemp.: %s\t|\tHumidity: %s" % (str(t_mean), str(h_mean)))

                    msg = str(temperature) + ';' + str(humidity)
                    lorawan = LoRaWAN.new(nwskey, appskey)
                    lorawan.create(MHDR.UNCONF_DATA_UP, {'devaddr': devaddr, 'fcnt': 1, 'data': list(map(ord, msg))})

                    msg = lorawan.to_raw()

                    log("Raw packet: " + str(msg))
                    # raw = bytearray(raw)
                    # msg = base64.b64encode(raw)

                    rf95.send(msg, len(msg))
                    rf95.waitPacketSent()
                    log("Sent message. Sleeping for %s" % postingDelay)

                    # Sleep
                    sleep(int(postingDelay))

            else:
                error("Invalid measuring.")

        except KeyboardInterrupt:
            log('Closing...')
            break
        except BaseException:
            error()

        print()


if __name__ == '__main__':
    loop()

