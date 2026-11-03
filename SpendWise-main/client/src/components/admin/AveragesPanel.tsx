import { useEffect, useMemo, useState } from 'react'
import SearchRounded from '@mui/icons-material/SearchRounded'
import { fetchAdmin, money, percent, type Averages, type CategoryAverage, type Period } from './api'

type SortKey = 'total_spent' | 'avg_per_household' | 'avg_per_person' | 'variance_percent' | 'households_over_target'

const sortOptions: { key: SortKey; label: string }[] = [
  { key: 'total_spent', label: 'סה״כ הוצאה' },
  { key: 'avg_per_household', label: 'ממוצע למשק בית' },
  { key: 'avg_per_person', label: 'ממוצע לנפש' },
  { key: 'variance_percent', label: 'סטייה מהיעד' },
  { key: 'households_over_target', label: 'חריגות' },
]

export default function AveragesPanel({ period }: { period: Period }) {
  const [data, setData] = useState<Averages | null>(null)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [sortKey, setSortKey] = useState<SortKey>('total_spent')

  useEffect(() => {
    let cancelled = false
    setError('')
    void fetchAdmin<Averages>('/admin/analytics/averages', period)
      .then((result) => { if (!cancelled) setData(result) })
      .catch((loadError: unknown) => {
        if (!cancelled) setError(loadError instanceof Error ? loadError.message : 'שגיאה בטעינה')
      })
    return () => { cancelled = true }
  }, [period])

  const rows = useMemo<CategoryAverage[]>(() => {
    if (!data) return []
    const filtered = data.categories.filter((row) => row.category_name.includes(query.trim()))
    return [...filtered].sort((a, b) => b[sortKey] - a[sortKey])
  }, [data, query, sortKey])

  if (error) return <div className="admin-error" role="alert">{error}</div>
  if (!data) return <p className="empty-note">מחשבים ממוצעים...</p>

  const totalSpent = data.categories.reduce((sum, row) => sum + row.total_spent, 0)
  const totalTarget = data.categories.reduce((sum, row) => sum + row.target_total, 0)
  const maxSpent = Math.max(...data.categories.map((row) => row.total_spent), 1)

  return (
    <>
      <section className="control-heading">
        <div>
          <p className="panel-kicker">ניתוח קטגוריות</p>
          <h1>ממוצעים והשוואות</h1>
          <p>ממוצע, חציון, מקסימום וסטייה מהיעד — לכל קטגוריית הוצאה, על פני כל משקי הבית.</p>
        </div>
        <div className="control-toolbar">
          <label className="search-field">
            <SearchRounded />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="חיפוש קטגוריה" aria-label="חיפוש קטגוריה" />
          </label>
          <select value={sortKey} onChange={(event) => setSortKey(event.target.value as SortKey)} aria-label="מיון">
            {sortOptions.map((option) => <option key={option.key} value={option.key}>מיון לפי {option.label}</option>)}
          </select>
        </div>
      </section>

      <section className="kpi-grid compact">
        <article className="kpi-card tone-blue"><small>סה״כ הוצאות המערכת</small><strong>{money(totalSpent)}</strong><em>{data.categories.length} קטגוריות פעילות</em></article>
        <article className="kpi-card tone-teal"><small>סה״כ יעד מחושב</small><strong>{money(totalTarget)}</strong><em>לפי תקן לנפש × גודל משק בית</em></article>
        <article className="kpi-card tone-amber"><small>סטייה כוללת מהיעד</small><strong>{percent(totalTarget ? (totalSpent - totalTarget) / totalTarget * 100 : 0)}</strong><em>{totalSpent > totalTarget ? 'חריגה מהתקן' : 'מתחת לתקן'}</em></article>
      </section>

      <section className="panel control-panel">
        <div className="panel-heading"><div><p className="panel-kicker">פירוט מלא</p><h2>הוצאות לפי קטגוריה</h2></div><span className="admin-count">{rows.length} קטגוריות</span></div>
        <div className="admin-table-scroll">
          <table className="admin-table analytics-table">
            <thead>
              <tr>
                <th>קטגוריה</th><th>סה״כ</th><th>ממוצע למשק</th><th>חציון</th><th>ממוצע לנפש</th><th>מקסימום</th><th>יעד ממוצע</th><th>סטייה</th><th>חריגות</th><th>התפלגות</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.category_id}>
                  <td>
                    <strong>{row.category_name}</strong>
                    <small>{row.is_essential ? 'חיוני' : 'גמיש'} · {row.households_spending} משקי בית</small>
                  </td>
                  <td>{money(row.total_spent)}</td>
                  <td>{money(row.avg_per_household)}</td>
                  <td>{money(row.median_per_household)}</td>
                  <td>{money(row.avg_per_person)}</td>
                  <td>{money(row.max_per_household)}</td>
                  <td>{money(row.avg_target_per_household)}</td>
                  <td><span className={`variance-pill ${row.variance_percent > 0 ? 'over' : 'under'}`}>{percent(row.variance_percent)}</span></td>
                  <td>{row.households_over_target ? <span className="variance-pill over">{row.households_over_target}</span> : '—'}</td>
                  <td><div className="inline-bar"><span style={{ width: `${Math.round(row.total_spent / maxSpent * 100)}%` }} /></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {rows.length === 0 && <p className="empty-note">לא נמצאו קטגוריות תואמות.</p>}
      </section>
    </>
  )
}
