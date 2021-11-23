# digitraffic-ais-capture

Capture Digitraffic AIS messages of all ships available from Digitraffic API.

1. `pip3 install paho-mqtt`  
2. `python3 listener.py`  

Data is written to a single file `digitraffic_ais_raw`.
Each row at file represents a single GeoJSON Point Feature. Also known as *GeoJSONSeq*.
