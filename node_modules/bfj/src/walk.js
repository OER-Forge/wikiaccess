'use strict'

const check = require('check-types')
const error = require('./error')
const EventEmitter = require('events').EventEmitter
const events = require('./events')

const terminators = {
  obj: '}',
  arr: ']'
}

const escapes = {
  /* eslint-disable quote-props */
  '"': '"',
  '\\': '\\',
  '/': '/',
  'b': '\b',
  'f': '\f',
  'n': '\n',
  'r': '\r',
  't': '\t'
  /* eslint-enable quote-props */
}

const DEFAULT_BUFFER_LENGTH = 256

module.exports = initialise

/**
 * Public function `walk`.
 *
 * Returns an event emitter and asynchronously walks a stream of JSON data,
 * emitting events as it encounters tokens. The event emitter is decorated
 * with a `pause` method that can be called to pause processing.
 *
 * @param stream:        Readable instance representing the incoming JSON.
 *
 * @option bufferLength:    The length of the walk buffer, default is 256.
 *
 * @option ndjson:          Set this to true to parse newline-delimited JSON.
 *
 * @option stringChunkSize: The size at which to chunk long strings, emitting
 *                          `string-chunk` events for each chunk followed by a
 *                          regular `string` event when the complete string has
 *                          been walked. Default is disabled.
 *
 * @option yieldRate:       The number of data items to process per timeslice,
 *                          default is 1024.
 **/
function initialise (stream, options = {}) {
  check.assert.instanceStrict(stream, require('stream').Readable, 'Invalid stream argument')
  check.assert.maybe.greater(options.stringChunkSize, 0, 'Invalid stringChunkSize option')

  const currentPosition = {
    line: 1,
    column: 1
  }
  const emitter = new EventEmitter()
  const handlers = {
    arr: value,
    obj: property
  }
  const json = []
  const lengths = []
  const previousPosition = {}
  const scopes = []
  const shouldHandleNdjson = !! options.ndjson
  const yieldRate = options.yieldRate || 1024
  const bufferLength = options.bufferLength || DEFAULT_BUFFER_LENGTH
  const stringChunkSize = options.stringChunkSize || Number.POSITIVE_INFINITY

  let index = 0
  let isStreamEnded = false
  let isStreamPaused = false
  let isWalkBegun = false
  let isWalkEnded = false
  let isWalkingString = false
  let hasEndedLine = true
  let count = 0
  let stringChunkCount = 0
  let stringChunkStart = 0
  let resumeFn
  let pause
  let cachedCharacter

  stream.setEncoding('utf8')
  stream.on('data', readStream)
  stream.on('end', endStream)
  stream.on('error', err => {
    emitter.emit(events.error, err)
    endStream()
  })

  emitter.pause = () => {
    let resolve
    pause = new Promise(res => resolve = res)
    return () => {
      pause = null
      count = 0

      if (shouldHandleNdjson && isStreamEnded && isWalkEnded) {
        emit(events.end)
      } else {
        resolve()
      }
    }
  }

  return emitter

  function readStream (chunk) {
    addChunk(chunk)

    if (isWalkBegun) {
      resume()
    } else {
      isWalkBegun = true
      value()
    }
  }

  function addChunk (chunk) {
    json.push(chunk)

    if (json.length >= bufferLength) {
      stream.pause()
      isStreamPaused = true
    }

    const chunkLength = chunk.length
    lengths.push({
      item: chunkLength,
      aggregate: length() + chunkLength
    })
  }

  function length () {
    const chunkCount = lengths.length

    if (chunkCount === 0) {
      return 0
    }

    return lengths[chunkCount - 1].aggregate
  }

  function value () {
    if (++count % yieldRate !== 0) {
      return consumeValue()
    }

    return new Promise(resolve => {
      setImmediate(() => consumeValue(resolve))
    })
  }

  async function consumeValue (resolve, reject) {
    try {
      await awaitNonWhitespace()
      await handleValue(await next())
      if (resolve) {
        resolve()
      }
    } catch (err) {
      if (reject) {
        reject(err)
      }
    }
  }

  async function awaitNonWhitespace () {
    await awaitCharacter()

    if (isWhitespace(character())) {
      await next()
      await awaitNonWhitespace()
    }
  }

  function awaitCharacter () {
    if (index < length()) {
      return Promise.resolve()
    }

    if (isStreamEnded) {
      setImmediate(endWalk)
      return Promise.reject()
    }

    return new Promise((resolve, reject) => {
      resumeFn = afterCharacter.bind(null, resolve, reject)
    })
  }

  function afterCharacter (resolve, reject) {
    if (index < length()) {
      return resolve()
    }

    reject()

    if (isStreamEnded) {
      setImmediate(endWalk)
    }
  }

  function character () {
    if (cachedCharacter) {
      return cachedCharacter
    }

    if (lengths[0].item > index) {
      return cachedCharacter = json[0].charAt(index)
    }

    const len = lengths.length
    for (let i = 1; i < len; ++i) {
      const { aggregate, item } = lengths[i]
      if (aggregate > index) {
        return cachedCharacter = json[i].charAt(index + item - aggregate)
      }
    }
  }

  function isWhitespace (char) {
    switch (char) {
      case '\n':
        if (shouldHandleNdjson && scopes.length === 0) {
          return false
        }
      case ' ':
      case '\t':
      case '\r':
        return true
    }

    return false
  }

  async function next () {
    await awaitCharacter()

    const result = character()

    cachedCharacter = null
    index += 1
    previousPosition.line = currentPosition.line
    previousPosition.column = currentPosition.column

    if (result === '\n') {
      currentPosition.line += 1
      currentPosition.column = 1
    } else {
      currentPosition.column += 1
    }

    while (index > lengths[0].aggregate) {
      json.shift()

      const difference = lengths.shift().item
      index -= difference

      lengths.forEach(len => len.aggregate -= difference)
    }

    if (isStreamPaused && json.length <= Math.floor(bufferLength / 2)) {
      isStreamPaused = false
      setImmediate(() => stream.resume())
    }

    return result
  }

  async function handleValue (char) {
    if (shouldHandleNdjson && scopes.length === 0) {
      if (char === '\n') {
        hasEndedLine = true
        await emit(events.endLine)
        return value()
      }

      if (! hasEndedLine) {
        await fail(char, '\n', previousPosition)
        return value()
      }

      hasEndedLine = false
    }

    switch (char) {
      case '[':
        return array()
      case '{':
        return object()
      case '"':
        return string()
      case '0':
      case '1':
      case '2':
      case '3':
      case '4':
      case '5':
      case '6':
      case '7':
      case '8':
      case '9':
      case '-':
      case '.':
        return number(char)
      case 'f':
        return literalFalse()
      case 'n':
        return literalNull()
      case 't':
        return literalTrue()
      default:
        await fail(char, 'value', previousPosition)
        return value()
    }
  }

  function array () {
    return scope(events.array, value)
  }

  async function scope (event, contentHandler) {
    await emit(event)

    scopes.push(event)
    await endScope(event)

    return await contentHandler()
  }

  async function emit (...args) {
    if (pause) {
      await pause
    }

    try {
      emitter.emit(...args)
    } catch (err) {
      try {
        emitter.emit(events.error, err)
      } catch (_) {
        // When calling user code, anything is possible
      }
    }
  }

  async function endScope (scp) {
    try {
      await awaitNonWhitespace()

      if (character() === terminators[scp]) {
        await emit(events.endPrefix + scp)

        scopes.pop()
        await next()

        await endValue()
      }
    } catch (_) {
      setImmediate(endWalk)
    }
  }

  async function endValue () {
    try {
      await awaitNonWhitespace()

      if (scopes.length === 0) {
        if (shouldHandleNdjson) {
          await value()
        } else {
          await fail(character(), 'EOF', currentPosition)
          await value()
        }
      }

      const scp = scopes[scopes.length - 1]
      const handler = handlers[scp]

      await endScope(scp)

      if (scopes.length > 0) {
        const isComma = await checkCharacter(character(), ',', currentPosition)
        if (isComma) {
          await next()
        }
      }

      await handler()
    } catch (_) {
      setImmediate(endWalk)
    }
  }

  function fail (actual, expected, position) {
    return emit(
      events.dataError,
      error.create(
        actual,
        expected,
        position.line,
        position.column
      )
    )
  }

  async function checkCharacter (char, expected, position) {
    if (char === expected) {
      return true
    }

    await fail(char, expected, position)

    return false
  }

  function object () {
    return scope(events.object, property)
  }

  async function property () {
    await awaitNonWhitespace()
    await checkCharacter(await next(), '"', previousPosition)
    await walkString(events.property)
    await awaitNonWhitespace()
    await checkCharacter(await next(), ':', previousPosition)
    await value()
  }

  async function walkString (event) {
    isWalkingString = true
    await walkStringContinue(event, [], false)
  }

  async function walkStringContinue (event, str, isEscaping) {
    const char = await next()

    if (isEscaping) {
      str.push(await escape(char))
      if (++stringChunkCount >= stringChunkSize) {
        await walkStringChunk(event, str)
      }
      return walkStringContinue(event, str, false)
    }

    if (char === '\\') {
      return walkStringContinue(event, str, true)
    }

    if (char !== '"') {
      str.push(char)
      if (++stringChunkCount >= stringChunkSize) {
        await walkStringChunk(event, str)
      }
      return walkStringContinue(event, str, isEscaping)
    }

    isWalkingString = false

    await walkStringChunk(event, str)
    stringChunkStart = 0

    return emit(event, str.join(''))
  }

  function walkStringChunk (event, str) {
    if (event === events.string) {
      const chunk = str.slice(stringChunkStart).join('')
      stringChunkStart = str.length
      stringChunkCount = 0
      return emit(events.stringChunk, chunk)
    }
  }

  async function escape (char) {
    if (escapes[char]) {
      return escapes[char]
    }

    if (char === 'u') {
      return escapeHex([], 0)
    }

    await fail(char, 'escape character', previousPosition)

    return `\\${char}`
  }

  async function escapeHex (hexits, idx) {
    const char = await next()

    if (isHexit(char)) {
      hexits.push(char)
    }

    if (idx < 3) {
      return escapeHex(hexits, idx + 1)
    }

    hexits = hexits.join('')

    if (hexits.length === 4) {
      return String.fromCharCode(parseInt(hexits, 16))
    }

    await fail(char, 'hex digit', previousPosition)
    return `\\u${hexits}${char}`
  }

  async function string () {
    await walkString(events.string)
    await endValue()
  }

  async function number (firstCharacter) {
    const digits = [ firstCharacter ]

    let atEnd = await walkDigits(digits)
    if (atEnd) {
      return endNumber(digits)
    }

    if (character() === '.') {
      digits.push(await next())
      atEnd = await walkDigits(digits)
      if (atEnd) {
        return endNumber(digits)
      }
    }

    if (character() === 'e' || character() === 'E') {
      try {
        digits.push(await next())

        await awaitCharacter()
        if (character() === '+' || character() === '-') {
          digits.push(await next())
        }

        await walkDigits(digits)
      } catch (_) {
        return fail('EOF', 'exponent', currentPosition)
      }
    }

    return endNumber(digits)
  }

  async function walkDigits (digits) {
    try {
      await awaitCharacter()

      if (isDigit(character())) {
        digits.push(await next())
        return walkDigits(digits)
      }

      return false
    } catch (_) {
      return true
    }
  }

  async function endNumber (digits) {
    await emit(events.number, parseFloat(digits.join('')))
    await endValue()
  }

  function literalFalse () {
    return literal([ 'a', 'l', 's', 'e' ], false)
  }

  async function literal (expectedCharacters, val) {
    try {
      await awaitCharacter()

      const actual = await next()
      const expected = expectedCharacters.shift()

      if (actual !== expected) {
        // eslint-disable-next-line no-throw-literal
        throw [ actual, expected ]
      }

      if (expectedCharacters.length === 0) {
        await emit(events.literal, val)
        return endValue()
      }

      await literal(expectedCharacters, val)
    } catch (err) {
      if (expectedCharacters.length > 0) {
        await fail('EOF', expectedCharacters[0], currentPosition)
      } else if (Array.isArray(err)) {
        const [ actual, expected ] = err
        await fail(actual, expected, previousPosition)
      }

      return endValue()
    }
  }

  function literalNull () {
    return literal([ 'u', 'l', 'l' ], null)
  }

  function literalTrue () {
    return literal([ 'r', 'u', 'e' ], true)
  }

  function endStream () {
    isStreamEnded = true

    if (isWalkBegun) {
      return resume()
    }

    endWalk()
  }

  function resume () {
    if (resumeFn) {
      resumeFn()
      resumeFn = null
    }
  }

  async function endWalk () {
    if (isWalkEnded) {
      return
    }

    isWalkEnded = true

    if (isWalkingString) {
      await fail('EOF', '"', currentPosition)
    }

    await popScopes()
    await emit(events.end)
  }

  async function popScopes () {
    if (scopes.length === 0) {
      return
    }

    await fail('EOF', terminators[scopes.pop()], currentPosition)
    await popScopes()
  }
}

function isHexit (character) {
  return isDigit(character) ||
    isInRange(character, 'A', 'F') ||
    isInRange(character, 'a', 'f')
}

function isDigit (character) {
  return isInRange(character, '0', '9')
}

function isInRange (character, lower, upper) {
  const code = character.charCodeAt(0)

  return code >= lower.charCodeAt(0) && code <= upper.charCodeAt(0)
}
