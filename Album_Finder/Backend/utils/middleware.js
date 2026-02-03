const logger = require('./logger')

const errorHandler = (error, request, response, next) => {
  logger.error(error.message)

  response.status(500).send({ error: 'Failed to fetch token' })
  next(error)
}

const unknownEndpoint = (request, response) => {
  response.status(404).send({ error: 'unknown endpoint' })
}

module.exports = {
  errorHandler,
  unknownEndpoint,
}