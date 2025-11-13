import React, { useState } from 'react'
import { collectAdsbData } from './api'
import AircraftArea from './components/AircraftArea'

export default function App() {
  const [lat, setLat] = useState('37.7749')
  const [lon, setLon] = useState('-122.4194')
  const [radius, setRadius] = useState('50')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await collectAdsbData(lat, lon, radius)
      setResult(res)
    } catch (err) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h1>ADS-B Aircraft Viewer</h1>
        <p>Query aircraft around a location using the backend API.</p>
      </header>

      <main>
        <form onSubmit={handleSubmit} className="query-form">
          <label>
            Latitude:
            <input value={lat} onChange={(e) => setLat(e.target.value)} />
          </label>
          <label>
            Longitude:
            <input value={lon} onChange={(e) => setLon(e.target.value)} />
          </label>
          <label>
            Radius (nm):
            <input value={radius} onChange={(e) => setRadius(e.target.value)} />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Loading…' : 'Search'}
          </button>
        </form>

        {error && <div className="error">Error: {error}</div>}

        {result && (
          <section className="results">
            <h2>Results</h2>
            <AircraftArea data={result} />
          </section>
        )}
      </main>

      <footer>
        <small>Backend API: configured via VITE_BACKEND_URL</small>
      </footer>
    </div>
  )
}