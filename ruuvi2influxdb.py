#!/usr/bin/python3
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import configparser, os
from datetime import datetime
from influxdb import InfluxDBClient

# read config
configfile=os.path.splitext(os.path.basename(__file__))[0] + '.ini'
config = configparser.ConfigParser()
config.read(['ruuvi_names.ini', '/opt/ruuvi/ruuvi_names.ini'])
config.read([configfile,'/opt/ruuvi/' + configfile])

db_host = config.get('General', 'db_host')
db_port = config.get('General', 'db_port')
db_name = config.get('General', 'db_name')
db_measurement = config.get('General', 'db_measurement')

listen = config.get('General', 'listen')

macs = []
names = []
listen_macs = []
temp_offsets = []

dbClient = InfluxDBClient(host=db_host, port=db_port)
dbClient.switch_database(db_name)

for tag in config.items('Tags'):
    print(tag)
    tag_name=tag[0]
    tag_mac=tag[1]
    names.append(tag_name)
    macs.append(tag_mac)
    temp_offsets.append(
        float(config.get('Opts_'+tag_name, 'offset_temp', fallback=0))
    )

for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])

print('Listen: ' + listen + '(' + str(listen_macs) + ')')

# Handle data reception
def handle_data(received_data):
    """
    Convert data into RuuviCollector naming schme and scale
    returns:
        Object to be written to InfluxDB
    """
    mac = received_data[0]
    payload = received_data[1]
    idx = macs.index(mac)
    name = names[idx]
    
    temp = payload['temperature'] if ('temperature' in payload) else None
    temp_offset = temp_offsets[idx]
    
    dataFormat = payload['data_format'] if ('data_format' in payload) else None
    fields = {}
    fields['temperature']                = (temp + temp_offset) if (temp is not None) else None
    fields['humidity']                   = payload['humidity'] if ('humidity' in payload) else None
#    fields['pressure']                  = payload['pressure'] if ('pressure' in payload) else None
#    fields['accelerationX']             = payload['acceleration_x'] if ('acceleration_x' in payload) else None
#    fields['accelerationY']             = payload['acceleration_y'] if ('acceleration_y' in payload) else None
#    fields['accelerationZ']             = payload['acceleration_z'] if ('acceleration_z' in payload) else None
    fields['batteryVoltage']             = payload['battery']/1000.0 if ('battery' in payload) else None
#    fields['txPower']                   = payload['tx_power'] if ('tx_power' in payload) else None
#    fields['movementCounter']           = payload['movement_counter'] if ('movement_counter' in payload) else None
#    fields['measurementSequenceNumber'] = payload['measurement_sequence_number'] if ('measurement_sequence_number' in payload) else None
#    fields['tagID']                     = payload['tagID'] if ('tagID' in payload) else None
#    fields['rssi']                      = payload['rssi'] if ('rssi' in payload) else None
    json_body = [
        {
            'measurement': db_measurement,
            'tags': {
                'mac': mac,
                'dataFormat': dataFormat,
                'name': name
            },
            'fields': fields
        }
    ]
    print(json_body)
    print('Temp read:',temp,' offset:',temp_offset)
    dbClient.write_points(json_body)

if __name__ == "__main__":
    RuuviTagSensor.get_datas(handle_data, listen_macs)
