import { useState, useEffect } from "react"
import axios from "axios"
import './App.css'

const baseUrl = '/token'

const Notification = ({ message }) => {
  if (!message) return null

  return (
    <div className="no-albums">{message}</div>
  )
}

function App() {
  const [accessToken, setAccessToken] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [albums, setAlbums] = useState([])
  const [message, setMessage] = useState(null)

  useEffect(() => {
    axios.get(`${baseUrl}`)
      .then(response => {
        setAccessToken(response.data.access_token)
      })
      .catch(error => console.log(`error: ${error}`))
  }, [])

  const search = async () => {
    if (!accessToken) return

    const artistParams = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + accessToken,
      }
    }  

    const artistID = await axios.get(`https://api.spotify.com/v1/search?q=${searchInput}&type=artist`, artistParams)
      .then(response => {
        const items = response?.data?.artists?.items || []

        if (items.length === 0) {
          setMessage('Artists not found')
          setAlbums([])
          return
        }

        const artistId = items[0].id
        return artistId
      })

    const albumData = await axios.get(`https://api.spotify.com/v1/artists/${artistID}/albums?include_groups=album&market=US&limit=10`, artistParams)
      .then(response => {
        const items = response.data.items

        if (items.length === 0) {
          setMessage(`This artist '${searchInput}' has no albums`)
          return []
        } else {
          setMessage(null)
          return items
        }
      })

    setAlbums(albumData)
  }

  return (
    <>
      <div className={`search-container ${albums.length > 0 ? "top" : "center"}`}>
        <h2 className="title">Spotify Album Search</h2>
        <div className="input-group">
          <input
            className="search-input"
            onChange={e => setSearchInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && search()}
            placeholder="Enter artist name"
          />
          <button className="search-button" onClick={search}>Search</button>
        </div>
      </div>
      <div className="albums-container">
        <Notification message={message} />
        {albums.map(album => (
          <div className="album-card fade-in" key={album.id}>
            <img src={album.images[0].url} alt={album.name} className="album-img"/>
            <p className="album-name">{album.name}</p>
            <p className="album-artists">{album.artists.map(artist => artist.name).join(', ')}</p>
            <p className="album-date">{album.release_date}</p>
            <a href={album.external_urls.spotify} target="_blank" rel="noreferrer" className="album-link">
              Open in Spotify
            </a>
          </div>
        ))}
      </div>
    </>
  )
}

export default App
