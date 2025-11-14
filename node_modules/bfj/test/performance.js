#!/usr/bin/env node

'use strict'

const fs = require('fs')
const path = require('path')
const check = require('check-types')
const bfj = require('../src')

const inPath = getDataPath('.json');

let time = process.hrtime()

if (process.argv.length === 4) {
  const inStream = fs.createReadStream(inPath)

  if (process.argv[3] === 'walk') {
    console.log('walking json')
    const emitter = bfj.walk(inStream)
    emitter.on(bfj.events.end, () => {
      console.log('hooray!')
      process.exit(0)
    })
    emitter.on(bfj.events.error, error => {
      console.error(error)
      process.exit(1)
    })
    emitter.on(bfj.events.dataError, error => {
      console.error(error)
      process.exit(2)
    })
  } else {
    console.log('matching json')
    const stuff = []
    const outStream = bfj.match(inStream, process.argv[3])
    outStream.on('data', thing => stuff.push(thing))
    outStream.on('end', () => {
      reportTime()
      console.log('hooray!', stuff.length)
      fs.writeFileSync(getDataPath('-result.ndjson'), stuff.map(s => JSON.stringify(s)).join('\n'), {
        encoding: 'utf8',
      })
      process.exit(0)
    })
    outStream.on('error', error => {
      console.error('error!', error.stack)
      process.exit(1)
    })
    outStream.on('dataError', error => {
      console.error('dataError!', error.stack)
      process.exit(2)
    })
  }
} else {
  console.log('reading json')
  bfj.read(inPath)
    .then(data => {
      reportTime()
      console.log('writing json')
      return bfj.write(getDataPath('-result.json'), data)
    })
    .then(() => done('succeeded'))
    .catch(error => done(error.stack, 1))
}

function getDataPath (suffix) {
  return path.resolve(__dirname, process.argv[2] + suffix)
}

function reportTime () {
  let interimTime = process.hrtime(time)
  console.log('%d seconds and %d nanoseconds', interimTime[0], interimTime[1])
  time = process.hrtime()
}

function done (message, code) {
  reportTime()
  console.log(message)
  process.exit(code)
}

