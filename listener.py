import uuid
import paho.mqtt.client as mqtt
import time
import json
import os
from signal import signal, SIGINT
import sqlite3
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

dbname = os.environ["DB_LOCATION"]
if (dbname is None):
    dbname = 'testdb.db'

con = sqlite3.connect(dbname)
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS ship
               (mmsi integer,
               lat real,
               lng real,
               sog real,
               cog real,
               rot real,
               heading real,
               ts integer)''')
cur.execute('''CREATE INDEX IF NOT EXISTS ship_mmsi ON ship (mmsi)''')
cur.execute('''CREATE INDEX IF NOT EXISTS ship_pos ON ship (lat, lng)''')
cur.execute('''CREATE INDEX IF NOT EXISTS ship_ts ON ship (ts)''')
con.commit()
con.close()

message_count = 0

mmsi_map = {}
buffer = []

def on_message(client, userdata, message):
    str_message = str(message.payload.decode('utf-8'))
    parsed_message = json.loads(str_message)
    mmsi = parsed_message["properties"]["mmsi"]
    ts = parsed_message["properties"]["timestampExternal"]
    global message_count
    global buffer
    global mmsi_map

    message_count += 1
    if (not mmsi in mmsi_map):
        buffer.append(parsed_message)
        mmsi_map[mmsi] = True

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info('Connected to mqtt')
        client.subscribe(f'vessels/+/locations')
    else:
        logging.error('Failed to connect, return code %d\n', rc)

client_name = '{}; {}'.format("digitraffic-ais-capture", str(uuid.uuid4()))
client = mqtt.Client(client_name, transport="websockets")

client.username_pw_set('digitraffic', 'digitrafficPassword')
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()

def handler(signal_received, frame):
    logging.info('exiting...')
    client.loop_stop()

    client.disconnect()
    exit(0)

if __name__ == '__main__':
    signal(SIGINT, handler)

    client.connect('meri.digitraffic.fi', 61619)

    client.loop_start()
    logging.info('Running. Press CTRL-C to exit.')
    while True:
        interval_seconds = 15
        time.sleep(interval_seconds)

        inserts = [(row["mmsi"], row["geometry"]["coordinates"][1], row["geometry"]["coordinates"][0], row["properties"]["sog"], row["properties"]["cog"], row["properties"]["rot"], row["properties"]["heading"], row["properties"]["timestampExternal"]) for row in buffer if row["properties"]["sog"] > 0]

        logging.info(f'current rate: {message_count}/{interval_seconds}s, inserting {len(inserts)}')

        time_start = time.time()

        con = sqlite3.connect(dbname)
        cur = con.cursor()
        cur.executemany("INSERT INTO ship values(?, ?, ?, ?, ?, ?, ?, ?)", inserts) 
        con.commit()
        con.close()
        buffer = []
        mmsi_map = {}
        message_count = 0

        time_end = time.time()
        logging.debug(f'buffer written, took {round(time_end - time_start, 5)} seconds')
        pass


