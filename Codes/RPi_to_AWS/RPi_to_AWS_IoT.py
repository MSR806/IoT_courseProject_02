import paho.mqtt.client as mqtt
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

#mqtt for esp
MQTT_ADDRESS = '192.168.0.8'
MQTT_USER = 'cdavid'
MQTT_PASSWORD = 'cdavid'
MQTT_TOPIC = 'home/+/+'

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
ENDPOINT = "customEndpointUrl"
CLIENT_ID = "testDevice"
PATH_TO_CERT = "certificates/a1b23cd45e-certificate.pem.crt"
PATH_TO_KEY = "certificates/a1b23cd45e-private.pem.key"
PATH_TO_ROOT = "certificates/root.pem"
MESSAGE = "Hello World"
TOPIC = "test/testing"
RANGE = 20

#mqtt client for rpi to aws
# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERT,
            pri_key_filepath=PATH_TO_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_ROOT,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")


def on_connect_esp(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message_esp(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    global publish
    global mqtt_connection
    print('Begin Publish')
    message = msg
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
    t.sleep(0.1)
    print(msg.topic + ' ' + str(msg.payload))
 

#mqtt client for nodemcu to rpi
client_esp = mqtt.Client()
client_esp.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client_esp.on_connect = on_connect_esp
client_esp.on_message = on_message_esp
client_esp.connect(MQTT_ADDRESS, 1883)
client_esp.loop_forever()
    

