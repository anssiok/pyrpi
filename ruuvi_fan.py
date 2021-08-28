#!/usr/bin/python3
import RPi.GPIO as GPIO
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import configparser
from datetime import datetime
from influxdb import InfluxDBClient

# read config
config = configparser.ConfigParser()
config.read(['ruuvi_names.ini','/opt/ruuvi/ruuvi_names.ini'])
config.read(['ruuvi_fan.ini','/opt/ruuvi/ruuvi_fan.ini'])

listen = config.get('General', 'listen')
tag_timeout = int(config.get('General', 'tag_timeout'))
timeout_check_interval = int(config.get('General', 'timeout_check_interval'))

temp_max = float(config.get('General', 'temp_max'))
temp_min = float(config.get('General', 'temp_min'))

db_host = config.get('General', 'db_host')
db_port = config.get('General', 'db_port')
db_name = config.get('General', 'db_name')

macs = []
names = []
fan_state = 0
pin = 14

dbClient = InfluxDBClient(host=db_host, port=db_port)
dbClient.switch_database(db_name)

for tag in config.items('Tags'):
    print(tag)
    names.append(tag[0])
    macs.append(tag[1])

listen_macs = []
for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])

print('Listen: ' + str(listen_macs))

# Handle data reception
def handle_data(found_data):
    global fan_state
    found_mac = found_data[0]
    idx = macs.index(found_mac)
    found_name = names[idx]
    temperature = found_data[1]['temperature']
    print ('mac:' + str(found_data[1]['mac']) +
        ' batt:' + str(found_data[1]['battery']) +
        ' temp:' + str(temperature) +
        ' fan:' + str(fan_state)
    )
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
    dbClient.write_points(json_body)

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    RuuviTagSensor.get_datas(handle_data, listen_macs)
except KeyboardInterrupt:
    print('Interrupted!')
except:
    print('Some error!')
finally:
    print('Cleaning up')
    GPIO.cleanup()
