#!/usr/bin/python3
import RPi.GPIO as GPIO
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import configparser, sys
from datetime import datetime
from influxdb import InfluxDBClient

# read config
config = configparser.ConfigParser()
config.read(['ruuvi_names.ini','/opt/ruuvi/ruuvi_names.ini'])
config.read(['ruuvi_fan.ini','/opt/ruuvi/ruuvi_fan.ini'])

listen = config.get('General', 'listen')

temp_max = float(config.get('General', 'temp_max'))
temp_min = float(config.get('General', 'temp_min'))

pin = int(config.get('General', 'fan_pin'))

db_host = config.get('General', 'db_host')
db_port = config.get('General', 'db_port')
db_name = config.get('General', 'db_name')
dbClient = None

macs = []
names = []
fan_state = 0

for tag in config.items('Tags'):
    print(tag)
    tag_name=tag[0]
    tag_mac=tag[1]
    names.append(tag_name)
    macs.append(tag_mac)
    temp_offsets.append(
        config.get('Opts_'+tag_name, 'offset_temp', 0)
    ):
    
listen_macs = []
for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])

print('Listen: ' + str(listen_macs))

# Handle data reception
def handle_data(found_data):
    global fan_state, dbClient
    found_mac = found_data[0]
    idx = macs.index(found_mac)
    found_name = names[idx]
    temperature = found_data[1]['temperature']
    temp_offset = offsets_temp[idx]
    print ('mac:'+str(found_data[1]['mac']),
        'batt:'+str(found_data[1]['battery']),
        'temp:'+str(temperature)+'+'+str(temp_offset),
        'min:'+str(temp_min),
        'max:'+str(temp_max),
        'fan:'+str(fan_state)
    )
    temperature=temperature+temp_offset;
    if temperature > temp_max and fan_state == 0:
        print('fan started')
        GPIO.output(pin, GPIO.HIGH)
        fan_state = 1
    if temperature < temp_min and fan_state == 1:
        print('fan stopped')
        GPIO.output(pin, GPIO.LOW)
        fan_state = 0
    json_body = [
        {
            "measurement": "fan_info",
            "tags": {
                "fan_id": "01"
            },
            "fields": {
                "fan_state": fan_state
            }
        }
    ]
    try: 
        if dbClient:
            dbClient.write_points(json_body)
        else:
            dbClient = InfluxDBClient(host=db_host, port=db_port)
            dbClient.switch_database(db_name)
    except (InfluxDBClientError) as err:
        print ('InfluxDBClientError: ' + err)
        
    except (InfluxDBServerError) as err:
        print ('InfluxDBServerError: ' + err)
        

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    RuuviTagSensor.get_datas(handle_data, listen_macs)

except KeyboardInterrupt:
    print('Exiting!')

finally:
    print('Cleaning up')
    GPIO.cleanup()
