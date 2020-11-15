import time					              #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import paho.mqtt.client as mqtt
import json

#--------------------------------------------------------------------------------------------#
#mqtt for esp32
ESP32_MQTT_SERVER = '192.168.1.3'
ESP32_MQTT_PORT = 1883
ESP32_MQTT_USER = 'cdavid'
ESP32_MQTT_PASSWORD = 'cdavid'
ESP32_MQTT_TOPIC = 'esp32/topic'
#--------------------------------------------------------------------------------------------#
AWS_MQTT_TOPIC_data = 'AWS_IoT/topic/data'
AWS_MQTT_TOPIC_info = 'AWS_IoT/topic/info'
#--------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------#
# AWS IoT certificate based connection
AWS_MQTTClient = AWSIoTMQTTClient("myClientID")
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 8883)
AWS_MQTTClient.configureCredentials("/home/pi/cert/Amazon_Root_CA_1.pem", "/home/pi/cert/61000fee35-private.pem.key", "/home/pi/cert/61000fee35-certificate.pem.crt")
AWS_MQTTClient.configureEndpoint("a2gztmlqjheqhq-ats.iot.us-east-1.amazonaws.com", 8883)
AWS_MQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
AWS_MQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
AWS_MQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
AWS_MQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
#--------------------------------------------------------------------------------------------#

# The callback for when the client receives a CONNACK response from the server.
def esp32_on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(ESP32_MQTT_TOPIC)
 
# The callback for when a PUBLISH message is received from the server.
def esp32_on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload)[2:-1])
    payload = json.dumps(str(msg.payload)[2:-1])
    AWS_MQTTClient.publish(AWS_MQTT_TOPIC_data, payload, 0)

#connect and publish
AWS_MQTTClient.connect()
AWS_MQTTClient.publish(AWS_MQTT_TOPIC_info, "connected", 0)
#myMQTTClient.publish("xxxx/info", "connected", 0)

# Create an MQTT client and attach our routines to it.
esp32_client = mqtt.Client()
esp32_client.on_connect = esp32_on_connect
esp32_client.on_message = esp32_on_message
 
esp32_client.connect(ESP32_MQTT_SERVER, ESP32_MQTT_PORT, 60)
 
# Process network traffic and dispatch callbacks. This will also handle
# reconnecting. Check the documentation at
# https://github.com/eclipse/paho.mqtt.python
# for information on how to use other loop*() functions
esp32_client.loop_forever()
