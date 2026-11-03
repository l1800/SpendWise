import { useEffect, useState } from 'react'
import PeopleAltRounded from '@mui/icons-material/PeopleAltRounded'
import AccountBalanceWalletRounded from '@mui/icons-material/AccountBalanceWalletRounded'
import TrendingUpRounded from '@mui/icons-material/TrendingUpRounded'
import TrendingDownRounded from '@mui/icons-material/TrendingDownRounded'
import SavingsRounded from '@mui/icons-material/SavingsRounded'
import WarningAmberRounded from '@mui/icons-material/WarningAmberRounded'
import NotificationsActiveRounded from '@mui/icons-material/NotificationsActiveRounded'
import TrackChangesRounded from '@mui/icons-material/TrackChangesRounded'
import { fetchAdmin, money, percent, type Health, type Overview, type Period } from './api'

function Gauge({ score }: { score: number }) {
  const radius = 52
  const circumference = Math.PI * radius
  const filled = (score / 100) * circumference
  const tone = score >= 75 ? '#5b9c78' : score >= 55 ? '#c9a227' : '#c0725f'
  return (
    <div className="gauge" aria-label={`ציון ממוצע ${score}`}>
      <svg viewBox="0 0 120 66" role="img">
        <path d={`M 8 60 A ${radius} ${radius} 0 0 1 112 60`} className="gauge-track" />
        <path
          d={`M 8 60 A ${radius} ${radius} 0 0 1 112 60`}
          className="gauge-fill"
          stroke={tone}
          strokeDasharray={`${filled} ${circumference}`}
        />
      </svg>
      <strong>{Math.round(score)}</strong>
      <small>ציון ממוצע</small>
    </div>
  )
}

export default function OverviewPanel({ period }: { period: Period }) {
  const [data, setData] = useState<Overview | null>(null)
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setError('')
    void Promise.all([
      fetchAdmin<Overview>('/admin/analytics/overview', period),
      fetchAdmin<Health>('/admin/analytics/health', period),
    ])
      .then(([overviewResult, healthResult]) => {
        if (cancelled) return
        setData(overviewResult)
        setHealth(healthResult)
      })
      .catch((loadError: unknown) => {
        if (!cancelled) setError(loadError instanceof Error ? loadError.message : 'שגיאה בטעינה')
      })
    return () => { cancelled = true }
  }, [period])

  if (error) return <div className="admin-error" role="alert">{error}</div>
  if (!data) return <p className="empty-note">טוענים את מדדי המערכת...</p>

  const topRisk = health?.households.filter((row) => row.band === 'risk').slice(0, 4) ?? []
  const totalBands = health ? Object.values(health.bands).reduce((sum, value) => sum + value, 0) : 0

  const cards = [
    { label: 'משקי בית פעילים', value: String(data.households_active), hint: `מתוך ${data.households_total} רשומים`, icon: PeopleAltRounded, tone: 'blue' },
    { label: 'הכנסה כוללת', value: money(data.total_income), hint: `ממוצע ${money(data.avg_income)} למשק בית`, icon: TrendingUpRounded, tone: 'green' },
    { label: 'הוצאה כוללת', value: money(data.total_expense), hint: `חציון ${money(data.median_expense)}`, icon: TrendingDownRounded, tone: 'peach' },
    { label: 'יחס חיסכון', value: `${data.savings_rate}%`, hint: 'מההכנסה הכוללת', icon: SavingsRounded, tone: 'teal' },
    { label: 'חריגה מתקציב', value: `${data.households_over_budget}`, hint: `סה״כ חריגה ${money(data.total_overage)}`, icon: WarningAmberRounded, tone: 'amber' },
    { label: 'התראות פתוחות', value: String(data.open_alerts), hint: 'ממתינות לטיפול', icon: NotificationsActiveRounded, tone: 'red' },
  ]

  return (
    <>
      <section className="control-heading">
        <div>
          <p className="panel-kicker">לוח בקרה</p>
          <h1>תמונת המצב של המערכת</h1>
          <p>מדדים מצטברים על כל משקי הבית הרשומים, מחושבים ישירות ממסד הנתונים.</p>
        </div>
      </section>

      <section className="kpi-grid">
        {cards.map(({ label, value, hint, icon: Icon, tone }) => (
          <article className={`kpi-card tone-${tone}`} key={label}>
            <span className="kpi-icon"><Icon /></span>
            <small>{label}</small>
            <strong>{value}</strong>
            <em>{hint}</em>
          </article>
        ))}
      </section>

      <section className="control-split">
        <div className="panel control-panel">
          <div className="panel-heading">
            <div><p className="panel-kicker">בריאות המערכת</p><h2>התפלגות משקי הבית</h2></div>
            <span className="admin-count">{totalBands} משקי בית</span>
          </div>
          <div className="band-layout">
            <Gauge score={data.avg_health_score} />
            <div className="band-legend">
              {(['excellent', 'good', 'watch', 'risk'] as const).map((band) => {
                const count = health?.bands[band] ?? 0
                const width = totalBands ? Math.round((count / totalBands) * 100) : 0
                return (
                  <div className={`band-row band-${band}`} key={band}>
                    <span className="band-dot" />
                    <span className="band-name">{ { excellent: 'מצוין', good: 'טוב', watch: 'למעקב', risk: 'בסיכון' }[band] }</span>
                    <div className="band-track"><span style={{ width: `${width}%` }} /></div>
                    <strong>{count}</strong>
                  </div>
                )
              })}
            </div>
          </div>
          <div className="control-figures">
            <div><small>יעדי חיסכון פעילים</small><strong><TrackChangesRounded />{data.active_savings_goals}</strong></div>
            <div><small>משקי בית בסיכון</small><strong className={data.risk_households ? 'danger' : ''}><WarningAmberRounded />{data.risk_households}</strong></div>
            <div><small>מאזן מצטבר</small><strong className={data.total_income - data.total_expense >= 0 ? 'positive' : 'danger'}><AccountBalanceWalletRounded />{money(data.total_income - data.total_expense)}</strong></div>
          </div>
        </div>

        <div className="panel control-panel">
          <div className="panel-heading">
            <div><p className="panel-kicker">דורש טיפול</p><h2>משקי בית בסיכון</h2></div>
          </div>
          {topRisk.length ? topRisk.map((row) => (
            <div className="risk-row" key={row.user_id}>
              <span className="profile-avatar">{row.name.slice(0, 1)}</span>
              <span className="risk-copy"><strong>{row.name}</strong><small>{row.family_size} נפשות · ניצול {row.expense_ratio}%</small></span>
              <span className="risk-meter"><span style={{ width: `${Math.min(100, row.expense_ratio)}%` }} /></span>
              <b>{Math.round(row.health_score)}</b>
            </div>
          )) : <p className="empty-note">אין כרגע משקי בית בסיכון גבוה.</p>}
          <div className="overage-summary">
            <small>סך חריגות מתקציב החודש</small>
            <strong>{money(data.total_overage)}</strong>
            <span className="variance-chip">{percent(data.avg_expense ? (data.total_expense / Math.max(data.total_income, 1) - 1) * 100 : 0)} ניצול תקציב</span>
          </div>
        </div>
      </section>
    </>
  )
}
