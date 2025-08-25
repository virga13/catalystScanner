import React, { useEffect, useState } from 'react'

type Signal = {
  id: number
  event_id?: number
  event_type: string
  headline: string
  tickers: string
  score: number
  playbook_hint?: string
  url?: string
  source: string
  created_at: string
  price_at_publish?: number | null
  rvol?: number | null
  premarket: boolean
}

export default function CatalystTape({ apiUrl, minScore, tickers, limit }: { apiUrl: string, minScore: number, tickers: string, limit: number }) {
  const [signals, setSignals] = useState<Signal[]>([])
  const [loading, setLoading] = useState(false)

  async function fetchSignals() {
    setLoading(true)
    const params = new URLSearchParams({ min_score: String(minScore), limit: String(limit) })
    if (tickers && tickers.trim().length > 0) params.set('tickers', tickers)
    const res = await fetch(`${apiUrl}/api/signals?` + params.toString())
    const data = await res.json()
    setSignals(data)
    setLoading(false)
  }

  useEffect(() => {
    fetchSignals()
    const id = setInterval(fetchSignals, 5000) // poll
    return () => clearInterval(id)
  }, [minScore, tickers, limit])

  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', marginBottom:8}}>
        <div className="muted">{loading ? 'Refreshing...' : `Showing ${signals.length} signals`}</div>
        <button onClick={fetchSignals} className="pill">Refresh</button>
      </div>
      <div>
        {signals.map(sig => (
          <div key={sig.id} className="row">
            <div><span className="badge">{sig.event_type.toUpperCase()}</span></div>
            <div>
              <div style={{fontWeight:600}}>
                {sig.tickers && <span className="muted">[{sig.tickers}] </span>}
                {sig.url ? <a href={sig.url} target="_blank" rel="noreferrer">{sig.headline}</a> : sig.headline}
                <div className="muted" style={{fontSize:12}}>
                {new Date(sig.created_at).toLocaleString()} • {sig.source} • {sig.playbook_hint || ''}
                {typeof sig.price_at_publish === 'number' && <> • ${sig.price_at_publish.toFixed(2)}</>}
                {typeof sig.rvol === 'number' && <> • RVOL {sig.rvol.toFixed(2)}</>}
                {sig.premarket && <> • premarket</>}
              </div>
              </div>
              <div className="muted" style={{fontSize:12}}>{new Date(sig.created_at).toLocaleString()} • {sig.source} • {sig.playbook_hint || ''}</div>
            </div>
            <div style={{textAlign:'right', fontWeight:700}}>{sig.score}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
