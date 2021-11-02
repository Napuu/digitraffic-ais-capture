#!/usr/bin/env zx

const fs = require('fs');
// TODO - this should be renamed to construct_geojson or something
const name = "filtered2";
const data = fs.readFileSync(name).toString();

const linesAsJson = data.split(/\r?\n/)
    .filter(l => l)
    .map(l => JSON.parse(l));


const featureCollection = {
    type: "FeatureCollection",
    features: []
};

featureCollection.features = linesAsJson;

fs.writeFileSync("test2.geojson", JSON.stringify(featureCollection));

/*
const sleep = async (n) => new Promise((resolve) => setTimeout(resolve, n));

let i = 0;
while (1) {

    i++;
    if (i === linesAsJson.length) i = 0;
    await sleep(2000);
}
*/