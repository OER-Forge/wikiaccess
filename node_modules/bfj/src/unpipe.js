'use strict'

const stream = require('stream')
const check = require('check-types')
const parse = require('./parse')

module.exports = unpipe

/**
 * Public function `unpipe`.
 *
 * Returns a writeable stream that can be passed to stream.pipe, then parses JSON
 * data read from the stream. If there are no errors, the callback is invoked with
 * the result as the second argument. If errors occur, the first error is passed to
 * the callback as the first argument.
 *
 * @param callback:   Function that will be called after parsing is complete.
 *
 * @option reviver:   Transformation function, invoked depth-first.
 *
 * @option discard:   The number of characters to process before discarding them
 *                    to save memory. The default value is `1048576`.
 *
 * @option yieldRate: The number of data items to process per timeslice,
 *                    default is 1024.
 **/
function unpipe (callback, options) {
  check.assert.function(callback, 'Invalid callback argument')

  const jsonstream = new stream.PassThrough()

  initStream(jsonstream, callback, options)

  return jsonstream
}

async function initStream (jsonstream, callback, options) {
  try {
    const data = await parse(jsonstream, { ...options, ndjson: false })
    await callback(null, data)
  } catch (error) {
    await callback(error)
  }
}
