#!/usr/bin/python

import ttn
import time
from influxdb import InfluxDBClient

app_id = "re_lora_x"
access_key = "ttn-account-v2.nUtMM21Pkfpc6Lubw2Ot7iI_zibZkt_-9sMSE1Q6ljk"

db_name = "ttn_db"
db_user = "admin"
db_pass = "admin"
db_address = "localhost"
db_port = 8086

influx_client = InfluxDBClient(host=db_address, port=db_port, database=db_name, username=db_user, password=db_pass)

def uplink_callback(msg, client):
	print "Received uplink from: " + str(msg.dev_id)
	print msg.payload_fields._fields

	json_body = [{
        	"measurement": str(msg.dev_id),
        	"tags": {
            		"host": "ttn_listener",
        	},
        	"fields": {
        	}
    	}]	

	for field in msg.payload_fields._fields:
		print "\t" + field + ": " + str(msg.payload_fields.__getattribute__(field))
		json_body[0]["fields"][field] = msg.payload_fields.__getattribute__(field) 
	print

	influx_client.write_points(json_body) 

handler = ttn.HandlerClient(app_id, access_key)

# using mqtt client
mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()

while True:
	time.sleep(30)

mqtt_client.close()

# using application manager client
#app_client =  handler.application()
#my_app = app_client.get()
#print(my_app)
#my_devices = app_client.devices()
#print(my_devices)
