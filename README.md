# digitraffic-ais-capture

Capture Digitraffic AIS messages of all ships available from Digitraffic API.  
Do not insert values where sog = 0. Also max one mmsi per 15s is picked up.

1. `podman build -t ais-listener .`  
2. `podman run -v $PWD/example.db:/app/example.db -e DB_LOCATION=/app/example.db -it ais-listener`

Data is written to a single SQLite defined by `DB_LOCATION`.