import React from 'react'

export default function AircraftArea({ data }) {
  if (!data) return null

  const aircraft = data.aircraft || data || []

  if (!Array.isArray(aircraft) || aircraft.length === 0) {
    return <div>No aircraft found in the requested area.</div>
  }

  return (
    <div className="aircraft-list">
      <div className="summary">
        <strong>Aircraft count:</strong> {data.aircraft_count ?? aircraft.length}
      </div>

      <table>
        <thead>
          <tr>
            <th>ICAO24</th>
            <th>Callsign</th>
            <th>Country</th>
            <th>Lat</th>
            <th>Lon</th>
            <th>Alt (m)</th>
            <th>Vel (m/s)</th>
            <th>Distance (nm)</th>
          </tr>
        </thead>
        <tbody>
          {aircraft.map((ac) => (
            <tr key={ac.icao24 || ac.callsign || Math.random()}>
              <td>{ac.icao24}</td>
              <td>{ac.callsign ?? '-'}</td>
              <td>{ac.origin_country ?? '-'}</td>
              <td>{ac.latitude ?? '-'}</td>
              <td>{ac.longitude ?? '-'}</td>
              <td>{ac.baro_altitude ?? '-'}</td>
              <td>{ac.velocity ?? '-'}</td>
              <td>{ac.distance_nm ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}