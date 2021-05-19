#!/usr/bin/python3
import RPi.GPIO as GPIO
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import requests, configparser, signal
from datetime import datetime

# read config
config = configparser.ConfigParser()
config.read(['ruuvi_fan.ini','/opt/ruuvi/ruuvi_fan.ini'])

listen = config.get('General', 'listen')
webhook = config.get('General', 'webhook')
tag_timeout = int(config.get('General', 'tag_timeout'))
timeout_check_interval = int(config.get('General', 'timeout_check_interval'))

temp_max = float(config.get('General', 'temp_max'))
temp_min = float(config.get('General', 'temp_min'))

macs = []
names = []
timers = []
move_counts = []
fan_state = 0
pin = 14

for tag in config.items('Tags'):
    print(tag)
    names.append(tag[0])
    macs.append(tag[1])
    move_counts.append(-1)
    timers.append(datetime.now())

listen_macs = []
for l in listen.split(','):
    listen_macs.append(macs[names.index(l)])
    
print('Listen: ' + str(listen_macs))

# Handle timeouts
def timer_handler(signum, frame):
    for idx, mac in enumerate(macs):
        if mac in listen_macs:
#            if timers[idx] == 0:
#                print ('Already at timeout: ' + names[idx])
#            el
            if timers[idx] != 0:
                if (datetime.now() - timers[idx]).total_seconds() > tag_timeout:
                    msg = 'Ei yhteyttä: ' + names[idx]
                    print(msg)
#                    response = requests.post(
#                        webhook,
#                        headers={'Content-type': 'application/json'},
#                        data='{"text":\'' + msg + '\'}'
#                    )
                    timers[idx] = 0
#                else:
#                    print('No timeout: ' + names[idx])
    signal.alarm(timeout_check_interval)

signal.signal(signal.SIGALRM, timer_handler)
signal.alarm(timeout_check_interval)

# Handle data reception
def handle_data(found_data):
    global fan_state
    found_mac = found_data[0]
    idx = macs.index(found_mac)
    found_name = names[idx]
    temperature = found_data[1]['temperature']
    print (
        datetime.now().strftime("%F %H:%M:%S") +
        ' mac: ' + str(found_data[1]['mac']) +
        ' battery: ' + str(found_data[1]['battery']) +
        ' temperature: ' + str(temperature)
    )
    if temperature > temp_max and fan_state == 0:
        print('fan on')
        GPIO.output(pin, GPIO.HIGH)
        fan_state = 1
    if temperature < temp_min and fan_state == 1:
        print('fan off')
        GPIO.output(pin, GPIO.LOW)
        fan_state = 0
#        response = requests.post(
#            webhook, headers={'Content-type': 'application/json'}, data='{"text":\''+msg+'\'}'
#        )
    timers[idx] = datetime.now()

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
