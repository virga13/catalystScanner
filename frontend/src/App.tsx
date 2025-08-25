import React, { useEffect, useMemo, useState } from 'react'
import CatalystTape from './components/CatalystTape'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [minScore, setMinScore] = useState(60)
  const [tickers, setTickers] = useState('')
  const [limit, setLimit] = useState(200)

  return (
    <div style={{maxWidth: 1100, margin: '20px auto', padding: 16}}>
      <div className="header">
        <h1 style={{fontSize: 24, fontWeight: 700}}>⚡ Catalyst Tape</h1>
        <div style={{display:'flex', gap:8}}>
          <input placeholder="Tickers (comma sep)" value={tickers} onChange={e=>setTickers(e.target.value)} />
          <input type="number" min={0} max={100} value={minScore} onChange={e=>setMinScore(parseInt(e.target.value||'0'))} />
          <select value={limit} onChange={e=>setLimit(parseInt(e.target.value))}>
            <option value={100}>100</option>
            <option value={200}>200</option>
            <option value={500}>500</option>
          </select>
        </div>
      </div>
      <CatalystTape apiUrl={API_URL} minScore={minScore} tickers={tickers} limit={limit} />
    </div>
  )
}
