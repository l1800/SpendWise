import { useEffect, useMemo, useState } from 'react'
import SearchRounded from '@mui/icons-material/SearchRounded'
import { bandLabel, fetchAdmin, money, type Health, type HealthBand, type Period } from './api'

const bands: HealthBand[] = ['excellent', 'good', 'watch', 'risk']
type Filter = 'all' | HealthBand

export default function HealthPanel({ period }: { period: Period }) {
  const [data, setData] = useState<Health | null>(null)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<Filter>('all')
  const [query, setQuery] = useState('')

  useEffect(() => {
    let cancelled = false
    setError('')
    void fetchAdmin<Health>('/admin/analytics/health', period)
      .then((result) => { if (!cancelled) setData(result) })
      .catch((loadError: unknown) => {
        if (!cancelled) setError(loadError instanceof Error ? loadError.message : 'שגיאה בטעינה')
      })
    return () => { cancelled = true }
  }, [period])

  const rows = useMemo(() => {
    if (!data) return []
    return data.households.filter((row) =>
      (filter === 'all' || row.band === filter) && row.name.includes(query.trim()),
    )
  }, [data, filter, query])

  if (error) return <div className="admin-error" role="alert">{error}</div>
  if (!data) return <p className="empty-note">מחשבים דירוג משקי בית...</p>

  const total = data.households.length

  return (
    <>
      <section className="control-heading">
        <div>
          <p className="panel-kicker">ניטור פיננסי</p>
          <h1>בריאות פיננסית</h1>
          <p>ציון לכל משק בית המשלב יחס הוצאה/הכנסה וחריגות מתקציב. מסודר מהנמוך לגבוה.</p>
        </div>
        <label className="search-field">
          <SearchRounded />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="חיפוש משק בית" aria-label="חיפוש משק בית" />
        </label>
      </section>

      <section className="band-cards">
        <button className={`band-card ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
          <small>הכל</small><strong>{total}</strong><em>משקי בית</em>
        </button>
        {bands.map((band) => (
          <button key={band} className={`band-card band-${band} ${filter === band ? 'active' : ''}`} onClick={() => setFilter(band)}>
            <small>{bandLabel[band]}</small>
            <strong>{data.bands[band] ?? 0}</strong>
            <em>{total ? Math.round((data.bands[band] ?? 0) / total * 100) : 0}% מהמערכת</em>
          </button>
        ))}
      </section>

      <section className="panel control-panel">
        <div className="panel-heading"><div><p className="panel-kicker">טבלת דירוג</p><h2>משקי בית</h2></div><span className="admin-count">{rows.length} מוצגים</span></div>
        <div className="admin-table-scroll">
          <table className="admin-table analytics-table">
            <thead>
              <tr><th>משק בית</th><th>נפשות</th><th>הכנסות</th><th>הוצאות</th><th>מאזן</th><th>ניצול</th><th>חריגה</th><th>התראות</th><th>ציון</th><th>מצב</th></tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.user_id}>
                  <td><strong>{row.name}</strong><small>{row.email}</small></td>
                  <td>{row.family_size}</td>
                  <td>{money(row.income)}</td>
                  <td>{money(row.expense)}</td>
                  <td className={row.balance >= 0 ? 'positive' : 'danger'}>{money(row.balance)}</td>
                  <td>
                    <div className="ratio-cell">
                      <div className="inline-bar"><span className={row.expense_ratio > 100 ? 'over' : ''} style={{ width: `${Math.min(100, row.expense_ratio)}%` }} /></div>
                      <small>{row.expense_ratio}%</small>
                    </div>
                  </td>
                  <td>{row.overage_total ? <span className="variance-pill over">{money(row.overage_total)}</span> : '—'}</td>
                  <td>{row.open_alerts || '—'}</td>
                  <td><strong>{Math.round(row.health_score)}</strong></td>
                  <td><span className={`status-pill band-${row.band}`}>{bandLabel[row.band]}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {rows.length === 0 && <p className="empty-note">לא נמצאו משקי בית תואמים.</p>}
      </section>
    </>
  )
}
