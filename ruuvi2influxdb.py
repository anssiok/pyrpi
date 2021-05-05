#!/usr/bin/python3
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from datetime import datetime
from influxdb import InfluxDBClient
import configparser

config = configparser.ConfigParser()
config.read(['./ruuvi2influxdb.ini', '/opt/ruuvi/ruuvi2influxdb.ini'])

listen=config.get('General', 'listen')
influxdb=config.get('General', 'influxdb')

macs = []
listen_macs = []
names = []

ixClient = InfluxDBClient(host='localhost', port=8086)
ixClient.switch_database('ruuvi')

for tag in config.items('Tags'):
    print(tag)
    names.append(tag[0])
    macs.append(tag[1])

#('FB:D8:55:BE:DC:9A', {'data_format': 5, 'humidity': 22.97, 'temperature': 21.59, 'pressure': 1000.67, 'acceleration': 1036.5018089709251, 'acceleration_x': 28, 'acceleration_y': -16, 'acceleration_z': 1036, 'tx_power': 4, 'battery': 2701, 'movement_counter': 156, 'measurement_sequence_number': 49793, 'mac': 'fbd855bedc9a'})

for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])
    
print('Listen: ' + str(listen_macs))

def handle_data(in_data):
    in_mac = in_data[0]
    in_name = names[macs.index(in_mac)]
    in_temperature = in_data[1]["temperature"]
    in_dataformat = in_data[1]["dataformat"]
    print (datetime.now().strftime("%F %H:%M:%S"))
    print(in_data)

    json_body = [
        {
            "measurement": "ruuvi_measurements",
            "tags": {
                "dataFormat": in_dataformat
                "name": in_name,
                "mac": upper(in_mac)
            },
            "time": "2018-03-28T8:01:00Z",
            "fields": {
                "temperature": 127
            }
        }
    ]

    
RuuviTagSensor.get_datas(handle_data, listen_macs)
print('done')
