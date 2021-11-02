#!/usr/bin/env zx

const fs = require('fs');

const name = "filtered2";
const data = fs.readFileSync(name).toString();

const linesAsJson = data.split(/\r?\n/)
    .filter(l => l)
    .map(l => JSON.parse(l));

const sleep = async (n) => new Promise((resolve) => setTimeout(resolve, n));

let i = 0;
while (1) {
    const line = linesAsJson[i];
    console.log(line);
    await $`curl localhost:3000/haloo` // something like this
    i++;
    if (i === linesAsJson.length) i = 0;
    await sleep(2000);
}
