# digitraffic-ais-capture

Capture Digitraffic AIS messages of certain ships and write them to file.

1. `pip3 install paho-mqtt`  
2. Edit `mmsi_map` at listener.py to include ships you wan't  
3. `python3 listener.py`  

Data is written to files of format `vessel_locations_{shortname}_{mmsi}`  
Each row at file represents a single GeoJSON Point Feature.