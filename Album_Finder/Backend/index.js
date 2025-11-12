require('dotenv').config()
const express = require('express')
const cors = require('cors')

const app = express()

app.use(cors())
app.use(express.static('dist'))

app.get('/token', async (req, res) => {
  try {
    const authString = Buffer.from(
      process.env.CLIENT_ID + ':' + process.env.CLIENT_SECRET
    ).toString('base64')

    const response = await fetch('https://accounts.spotify.com/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': `Basic ${authString}`,
      },
      body: 'grant_type=client_credentials'
    })

    const data = await response.json()
    res.json(data)
  } catch (error) {
    console.error('Token fetch failed:', error)
    res.status(500).json({ error: 'Failed to fetch token' })
  }
})

const port = process.env.PORT
app.listen(port, () => console.log(`server is running on port ${port}`))