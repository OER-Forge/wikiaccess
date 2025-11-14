'use strict'

const check = require('check-types')
const EventEmitter = require('events').EventEmitter
const events = require('./events')

const invalidTypes = {
  undefined: true, // eslint-disable-line no-undefined
  function: true,
  symbol: true
}

module.exports = eventify

/**
 * Public function `eventify`.
 *
 * Returns an event emitter and asynchronously traverses a data structure
 * (depth-first), emitting events as it encounters items. Sanely handles
 * promises, buffers, maps and other iterables. The event emitter is
 * decorated with a `pause` method that can be called to pause processing.
 *
 * @param data:       The data structure to traverse.
 *
 * @option promises:  'resolve' or 'ignore', default is 'resolve'.
 *
 * @option buffers:   'toString' or 'ignore', default is 'toString'.
 *
 * @option maps:      'object' or 'ignore', default is 'object'.
 *
 * @option iterables:  'array' or 'ignore', default is 'array'.
 *
 * @option circular:   'error' or 'ignore', default is 'error'.
 *
 * @option yieldRate:  The number of data items to process per timeslice,
 *                     default is 1024.
 **/
function eventify (data, options = {}) {
  const coercions = {}
  const emitter = new EventEmitter()
  const references = new Map()

  let count = 0
  let disableCoercions = false
  let ignoreCircularReferences
  let ignoreItems
  let pause
  let yieldRate

  emitter.pause = () => {
    let resolve
    pause = new Promise((res) => resolve = res)
    return () => {
      pause = null
      count = 0
      resolve()
    }
  }
  parseOptions()
  setImmediate(begin)

  return emitter

  function parseOptions () {
    parseCoercionOption('promises')
    parseCoercionOption('buffers')
    parseCoercionOption('maps')
    parseCoercionOption('iterables')

    if (Object.keys(coercions).length === 0) {
      disableCoercions = true
    }

    if (options.circular === 'ignore') {
      ignoreCircularReferences = true
    }

    check.assert.maybe.positive(options.yieldRate)
    yieldRate = options.yieldRate || 1024
  }

  function parseCoercionOption (key) {
    if (options[key] !== 'ignore') {
      coercions[key] = true
    }
  }

  async function begin () {
    try {
      await proceed(data)
    } catch (error) {
      await emit(events.error, error)
    } finally {
      await emit(events.end)
    }
  }

  async function proceed (datum) {
    if (++count % yieldRate !== 0) {
      return afterCoercion(await coerce(datum))
    }

    return new Promise(yieldThenProceed.bind(null, datum))
  }

  async function coerce (datum) {
    if (disableCoercions || check.primitive(datum)) {
      return datum
    }

    if (check.thenable(datum)) {
      return coerce(await coerceThing(datum, 'promises', coercePromise))
    }

    if (check.instanceStrict(datum, Buffer)) {
      return coerceThing(datum, 'buffers', coerceBuffer)
    }

    if (check.instanceStrict(datum, Map)) {
      return coerceThing(datum, 'maps', coerceMap)
    }

    if (
      check.iterable(datum) &&
      check.not.string(datum) &&
      check.not.array(datum)
    ) {
      return coerceThing(datum, 'iterables', coerceIterable)
    }

    if (check.function(datum.toJSON)) {
      return datum.toJSON()
    }

    return datum
  }

  function coerceThing (datum, thing, fn) {
    if (coercions[thing]) {
      return fn(datum)
    }

    return Promise.resolve()
  }

  function coercePromise (p) {
    return p
  }

  function coerceBuffer (buffer) {
    return Promise.resolve(buffer.toString())
  }

  function coerceMap (map) {
    const result = {}

    return coerceCollection(map, result, (val, key) => {
      result[key] = val
    })
  }

  function coerceCollection (coll, target, push) {
    coll.forEach(push)

    return Promise.resolve(target)
  }

  function coerceIterable (iterable) {
    const result = []

    return coerceCollection(iterable, result, (val) => {
      result.push(val)
    })
  }

  function afterCoercion (coerced) {
    if (isInvalid(coerced)) {
      return
    }

    if (coerced === false || coerced === true || coerced === null) {
      return literal(coerced)
    }

    if (Array.isArray(coerced)) {
      return array(coerced)
    }

    const type = typeof coerced

    switch (type) {
      case 'number':
        return value(coerced, type)
      case 'string':
        return value(escapeString(coerced), type)
      default:
        return object(coerced)
    }
  }

  function isInvalid (datum) {
    const type = typeof datum
    return !! invalidTypes[type] || (
      type === 'number' && ! isValidNumber(datum)
    )
  }

  function isValidNumber (datum) {
    return datum > Number.NEGATIVE_INFINITY && datum < Number.POSITIVE_INFINITY
  }

  function yieldThenProceed (datum, resolve, reject) {
    setImmediate(async () => {
      try {
        resolve(await afterCoercion(await coerce(datum)))
      } catch (error) {
        reject(error)
      }
    })
  }

  function literal (datum) {
    return value(datum, 'literal')
  }

  function array (datum) {
    // For an array, collection:object and collection:array are the same.
    return collection(datum, datum, 'array', async (val) => {
      if (isInvalid(val)) {
        await proceed(null)
      } else {
        await proceed(val)
      }
    })
  }

  async function collection (obj, arr, type, action) {
    let ignoreThisItem

    if (references.has(obj)) {
      ignoreThisItem = ignoreItems = true

      if (! ignoreCircularReferences) {
        return emit(events.dataError, new Error('Circular reference.'))
      }
    } else {
      references.set(obj, true)
    }

    await emit(events[type])

    await item(obj, arr, type, action, ignoreThisItem, 0)
  }

  async function emit (event, eventData) {
    try {
      await pause
      emitter.emit(event, eventData)
    } catch (error) {
      try {
        emitter.emit(events.error, error)
      } catch (_) {
        // When calling user code, anything is possible
      }
    }
  }

  async function item (obj, arr, type, action, ignoreThisItem, index) {
    if (index >= arr.length) {
      if (ignoreThisItem) {
        ignoreItems = false
      }

      if (ignoreItems) {
        return
      }

      await emit(events.endPrefix + events[type])

      references.delete(obj)

      return
    }

    if (ignoreItems) {
      return item(obj, arr, type, action, ignoreThisItem, index + 1)
    }

    await action(arr[index])

    await item(obj, arr, type, action, ignoreThisItem, index + 1)
  }

  function value (datum, type) {
    return emit(events[type], datum)
  }

  function object (datum) {
    // For an object, collection:object and collection:array are different.
    return collection(datum, Object.keys(datum), 'object', async (key) => {
      const val = datum[key]

      if (isInvalid(val)) {
        return
      }

      await emit(events.property, escapeString(key))

      await proceed(val)
    })
  }

  function escapeString (string) {
    string = JSON.stringify(string)
    return string.substring(1, string.length - 1)
  }
}
