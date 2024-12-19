import network
import time
import machine

from umqtt.simple import MQTTClient
from machine import Pin
  
ssid = 'SSID_NAME'
password = 'WIFI_PASSWORD'
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
 
# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
 
led = Pin(15, Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

hostname = 'YOUR_IOT_HUB_NAME.azure-devices.net'
clientid = 'picow'
user_name = 'YOUR_IOT_HUB_NAME.azure-devices.net/picow/?api-version=2021-04-12'
passw = 'YOUR_SAS_TOKEN'
topic_pub = b'devices/picow/messages/events/'
topic_msg = b'{"buttonpressed":"1"}'
port_no = 0
subscribe_topic = "devices/picow/messages/devicebound/#"

def mqtt_connect():

    certificate_path = "digicert.der"
    print('Loading Digicert Certificate')
    with open(certificate_path, 'rb') as f:
        cert = f.read()
    print('Obtained Digicert Certificate')
    sslparams = {'cadata':cert}
    
    client = MQTTClient(client_id=clientid, server=hostname, port=port_no, user=user_name, password=passw, keepalive=3600, ssl=True, ssl_params=sslparams)
    client.connect()
    print('Connected to IoT Hub MQTT Broker')
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

def callback_handler(topic, message_receive):
    print("Received message")
    print(message_receive)
    if message_receive.strip() == b'led_on':
        led.value(1)
    else:
        led.value(0)

try:
    client = mqtt_connect()
    client.set_callback(callback_handler)
    client.subscribe(topic=subscribe_topic)
except OSError as e:
    print(e)
    reconnect()

while True:
    
    client.check_msg()
    
    if button.value():
        client.publish(topic_pub, topic_msg)
        time.sleep(0.5)
    else:
        pass