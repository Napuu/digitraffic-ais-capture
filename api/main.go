package main

import (
	"log"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/jmoiron/sqlx"
	_ "github.com/mattn/go-sqlite3"
)

type Ship struct {
	MMSI    int     `db:"mmsi"`
	Lat     float64 `db:"lat"`
	Lng     float64 `db:"lng"`
	Sog     float64 `db:"sog"`
	Cog     float64 `db:"cog"`
	Rot     float64 `db:"rot"`
	Heading float64 `db:"heading"`
	TS      int     `db:"ts"`
}

type ShipProperties struct {
	MMSI    int     `json:"mmsi"`
	Sog     float64 `json:"sog"`
	Cog     float64 `json:"cog"`
	Rot     float64 `json:"rot"`
	Heading float64 `json:"heading"`
	TS      int     `json:"ts"`
}

type GeoJSONPointGeometry struct {
	Type        string    `json:"type"`
	Coordinates []float64 `json:"coordinates"`
}
type GeoJSONPoint struct {
	Type       string               `json:"type"`
	Properties ShipProperties       `json:"properties"`
	Geometry   GeoJSONPointGeometry `json:"geometry"`
}
type GeoJSONFeatureCollection struct {
	Type     string         `json:"type"`
	Features []GeoJSONPoint `json:"features"`
}

type TileRequestHandler struct {
	Db *sqlx.DB
}

func (dbObj *TileRequestHandler) Get(c *gin.Context) {
	// <ulx> <uly> <lrx> <lry>
	// lng-min lat-max lng-max lat-min
	// <left-top> <right-bot>
	bbox := c.QueryMap("bbox")

	ts := c.Query("ts")
	tsDiff := c.Query("tsDiff")
	if tsDiff == "" {
		tsDiff = "3600"
	}
	parsedTs, err := time.Parse(time.RFC3339, ts)
	if err != nil {
		log.Println(err)
		c.JSON(500, gin.H{
			"err": "timestamp parsing failed",
		})
		return
	}
	parsedTsDiff, err := strconv.Atoi(tsDiff)
	if err != nil {
		log.Println(err)
		c.JSON(500, gin.H{
			"err": "timestamp diff parsing failed",
		})
	}
	tsMin := parsedTs.Add(-time.Second * time.Duration(parsedTsDiff))
	tsMax := parsedTs
	rows, err := dbObj.Db.Queryx(`
		SELECT *, MAX(ts) as ts FROM ship
		WHERE lat > ? AND lat < ? AND lng > ? AND lng < ? AND
			ts > ? AND ts < ?
		GROUP BY mmsi
		ORDER BY ts DESC`,
		bbox["latmin"], bbox["latmax"], bbox["lngmin"], bbox["lngmax"],
		tsMin.UnixMilli(), tsMax.UnixMilli())

	if err != nil {
		log.Println(err)
		c.JSON(500, gin.H{
			"err": "query failed",
		})
		return
	}
	var feats []GeoJSONPoint
	for rows.Next() {
		var ship Ship

		err := rows.StructScan(&ship)
		if err != nil {
			log.Fatalln(err)
		}

		pointgeom := GeoJSONPointGeometry{
			Type:        "Point",
			Coordinates: []float64{ship.Lng, ship.Lat},
		}

		shipProperties := ShipProperties{
			MMSI:    ship.MMSI,
			Sog:     ship.Sog,
			Cog:     ship.Cog,
			Rot:     ship.Rot,
			Heading: ship.Heading,
			TS:      ship.TS,
		}
		shipfeat := GeoJSONPoint{
			Type:       "Feature",
			Properties: shipProperties,
			Geometry:   pointgeom,
		}

		feats = append(feats, shipfeat)
	}
	c.JSON(200, gin.H{
		"type":     "FeatureCollection",
		"features": feats,
	})
}

func main() {

	dbPath := os.Getenv("DB_LOCATION")
	if dbPath == "" {
		log.Fatalln("DB_LOCATION is not set")
	}
	db, err := sqlx.Open("sqlite3", dbPath+"?mode=ro&cache=shared")
	if err != nil {
		log.Fatalln(err)
	}
	defer db.Close()

	Obj := new(TileRequestHandler)
	Obj.Db = db

	r := gin.Default()

	r.GET("/ship", Obj.Get)
	r.Run()
}
