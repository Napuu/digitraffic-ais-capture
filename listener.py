import uuid
import paho.mqtt.client as mqtt
import time
import json
from signal import signal, SIGINT

message_count = 0

buffer = ""

def on_message(client, userdata, message):
    str_message = str(message.payload.decode('utf-8'))
    parsed_message = json.loads(str_message)
    mmsi = parsed_message["properties"]["mmsi"]
    ts = parsed_message["properties"]["timestampExternal"]
    global message_count
    global buffer
    message_count += 1
    buffer += json.dumps(parsed_message) + "\n"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to mqtt')
        client.subscribe(f'vessels/+/locations')
    else:
        print('Failed to connect, return code %d\n', rc)

client_name = '{}; {}'.format("digitraffic-ais-capture", str(uuid.uuid4()))
client = mqtt.Client(client_name, transport="websockets")

client.username_pw_set('digitraffic', 'digitrafficPassword')
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()
def handler(signal_received, frame):
    print('exiting...')
    client.loop_stop()

    client.disconnect()
    exit(0)

if __name__ == '__main__':
    signal(SIGINT, handler)

    client.connect('meri.digitraffic.fi', 61619)

    client.loop_start()
    print('Running. Press CTRL-C to exit.')
    while True:
        time.sleep(60)
        print(f'current rate: {message_count}/60s')
        with open(f'digitraffic_ais_raw', "a") as f:
            f.write(buffer)
            buffer = ""
        message_count = 0
        pass
