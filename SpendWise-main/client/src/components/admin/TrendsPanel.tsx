import { useEffect, useState } from 'react'
import { fetchAdmin, money, type Period, type TrendPoint, type Trends } from './api'

const monthName = (year: number, month: number) =>
  new Intl.DateTimeFormat('he-IL', { month: 'short' }).format(new Date(year, month - 1, 1))

const WIDTH = 720
const HEIGHT = 260
const PAD = { top: 18, right: 16, bottom: 30, left: 52 }

function TrendChart({ points }: { points: TrendPoint[] }) {
  const [hover, setHover] = useState<number | null>(null)
  const plotWidth = WIDTH - PAD.left - PAD.right
  const plotHeight = HEIGHT - PAD.top - PAD.bottom
  const maxValue = Math.max(...points.flatMap((point) => [point.income, point.expense]), 1)
  const ceiling = Math.ceil(maxValue / 5000) * 5000 || 5000

  const x = (index: number) => PAD.left + (points.length <= 1 ? plotWidth / 2 : (index / (points.length - 1)) * plotWidth)
  const y = (value: number) => PAD.top + plotHeight - (value / ceiling) * plotHeight

  const line = (key: 'income' | 'expense') =>
    points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${x(index).toFixed(1)} ${y(point[key]).toFixed(1)}`).join(' ')

  const area = `${line('income')} L ${x(points.length - 1).toFixed(1)} ${y(0)} L ${x(0).toFixed(1)} ${y(0)} Z`
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => ceiling * ratio)

  return (
    <div className="trend-chart">
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="גרף הכנסות מול הוצאות">
        {ticks.map((tick) => (
          <g key={tick}>
            <line x1={PAD.left} x2={WIDTH - PAD.right} y1={y(tick)} y2={y(tick)} className="chart-grid" />
            <text x={PAD.left - 10} y={y(tick) + 4} className="chart-tick" textAnchor="end">{Math.round(tick / 1000)}k</text>
          </g>
        ))}
        <path d={area} className="chart-area" />
        <path d={line('income')} className="chart-line income-line" />
        <path d={line('expense')} className="chart-line expense-line" />
        {points.map((point, index) => (
          <g key={`${point.year}-${point.month}`}>
            <circle cx={x(index)} cy={y(point.income)} r={hover === index ? 5 : 3.5} className="chart-dot income-dot" />
            <circle cx={x(index)} cy={y(point.expense)} r={hover === index ? 5 : 3.5} className="chart-dot expense-dot" />
            <text x={x(index)} y={HEIGHT - 10} className="chart-tick" textAnchor="middle">{monthName(point.year, point.month)}</text>
            <rect x={x(index) - plotWidth / Math.max(points.length, 1) / 2} y={PAD.top} width={plotWidth / Math.max(points.length, 1)} height={plotHeight} className="chart-hit" onMouseEnter={() => setHover(index)} onMouseLeave={() => setHover(null)} />
          </g>
        ))}
      </svg>
      {hover !== null && points[hover] && (
        <div className="chart-tooltip" style={{ right: `${Math.min(92, Math.max(8, (x(hover) / WIDTH) * 100))}%` }}>
          <strong>{monthName(points[hover].year, points[hover].month)} {points[hover].year}</strong>
          <span><i className="dot-income" />הכנסות {money(points[hover].income)}</span>
          <span><i className="dot-expense" />הוצאות {money(points[hover].expense)}</span>
          <span><i className="dot-balance" />מאזן {money(points[hover].balance)}</span>
        </div>
      )}
    </div>
  )
}

export default function TrendsPanel({ period }: { period: Period }) {
  const [data, setData] = useState<Trends | null>(null)
  const [error, setError] = useState('')
  const [months, setMonths] = useState(6)

  useEffect(() => {
    let cancelled = false
    setError('')
    void fetchAdmin<Trends>('/admin/analytics/trends', period, `&months=${months}`)
      .then((result) => { if (!cancelled) setData(result) })
      .catch((loadError: unknown) => {
        if (!cancelled) setError(loadError instanceof Error ? loadError.message : 'שגיאה בטעינה')
      })
    return () => { cancelled = true }
  }, [period, months])

  if (error) return <div className="admin-error" role="alert">{error}</div>
  if (!data) return <p className="empty-note">טוענים מגמות...</p>

  const points = data.months
  const last = points[points.length - 1]
  const previous = points[points.length - 2]
  const change = previous && previous.expense > 0 ? (last.expense - previous.expense) / previous.expense * 100 : 0
  const best = points.reduce((top, point) => point.balance > top.balance ? point : top, points[0])
  const worse = points.reduce((low, point) => point.balance < low.balance ? point : low, points[0])
  const maxRate = Math.max(...points.map((point) => Math.abs(point.savings_rate)), 1)

  return (
    <>
      <section className="control-heading">
        <div>
          <p className="panel-kicker">התפתחות לאורך זמן</p>
          <h1>מעקב מגמות</h1>
          <p>השוואת הכנסות והוצאות חודש-מול-חודש, וזיהוי מגמת יחס החיסכון.</p>
        </div>
        <div className="segmented" role="group" aria-label="טווח חודשים">
          {[6, 12, 18].map((option) => (
            <button key={option} className={months === option ? 'active' : ''} onClick={() => setMonths(option)}>{option} חודשים</button>
          ))}
        </div>
      </section>

      <section className="kpi-grid compact">
        <article className="kpi-card tone-green"><small>הוצאות החודש</small><strong>{money(last.expense)}</strong><em>{change > 0 ? `עלייה של ${change.toFixed(1)}%` : change < 0 ? `ירידה של ${Math.abs(change).toFixed(1)}%` : 'ללא שינוי'}</em></article>
        <article className="kpi-card tone-teal"><small>יחס חיסכון</small><strong>{last.savings_rate}%</strong><em>{last.savings_rate >= 20 ? 'בתוך מסלול בריא' : 'מתחת ליעד המומלץ'}</em></article>
        <article className="kpi-card tone-blue"><small>החודש הטוב ביותר</small><strong>{monthName(best.year, best.month)}</strong><em>{money(best.balance)} מאזן</em></article>
        <article className="kpi-card tone-amber"><small>החודש החלש</small><strong>{monthName(worse.year, worse.month)}</strong><em>{money(worse.balance)} מאזן</em></article>
      </section>

      <section className="panel control-panel">
        <div className="panel-heading">
          <div><p className="panel-kicker">גרף מצטבר</p><h2>הכנסות מול הוצאות</h2></div>
          <div className="chart-legend"><span><i className="dot-income" />הכנסות</span><span><i className="dot-expense" />הוצאות</span></div>
        </div>
        <TrendChart points={points} />
      </section>

      <section className="panel control-panel">
        <div className="panel-heading"><div><p className="panel-kicker">פירוט חודשי</p><h2>יחס חיסכון לפי חודש</h2></div></div>
        <div className="rate-list">
          {[...points].reverse().map((point) => (
            <div className="rate-row" key={`${point.year}-${point.month}`}>
              <span className="rate-label">{monthName(point.year, point.month)} {point.year}</span>
              <div className="rate-track">
                <div className="rate-center" />
                <span
                  className={point.savings_rate >= 0 ? 'rate-positive' : 'rate-negative'}
                  style={{
                    width: `${Math.min(50, Math.abs(point.savings_rate) / maxRate * 50)}%`,
                    [point.savings_rate >= 0 ? 'right' : 'left']: '50%',
                  } as React.CSSProperties}
                />
              </div>
              <strong className={point.savings_rate >= 0 ? 'positive' : 'danger'}>{point.savings_rate}%</strong>
              <small>{point.active_households} משקי בית</small>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}
