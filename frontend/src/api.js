const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001'

export async function collectAdsbData(latitude, longitude, radius) {
  const url = new URL(`${BACKEND}/api/collect_adsb_data`)
  url.searchParams.set('latitude', latitude)
  url.searchParams.set('longitude', longitude)
  url.searchParams.set('radius', radius)

  const resp = await fetch(url.toString())
  if (!resp.ok) {
    const text = await resp.text()
    throw new Error(text || `HTTP ${resp.status}`)
  }
  return resp.json()
}