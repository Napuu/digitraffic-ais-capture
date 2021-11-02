#!/usr/bin/env zx

const fs = require('fs');

const nameIn = "vessel_locations_xprs_276813000";
const nameOut = "filtered2";
const data = fs.readFileSync(nameIn).toString();

const linesAsJson = data.split(/\r?\n/)
    .filter(l => l)
    .map(l => JSON.parse(l))
    .filter(l => l.properties.timestampExternal < 1635874057165 && l.properties.timestampExternal > 1635872825431);

linesAsJson.forEach(line => {
    fs.appendFileSync(nameOut, JSON.stringify(line) + "\n");
});
/*
const sleep = async (n) => new Promise((resolve) => setTimeout(resolve, n));

let i = 0;
while (1) {

    i++;
    if (i === linesAsJson.length) i = 0;
    await sleep(2000);
}
*/