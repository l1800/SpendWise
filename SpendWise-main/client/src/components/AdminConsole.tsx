import { useEffect, useState } from 'react'
import AdminLayout, { type AdminPage } from './admin/AdminLayout'
import OverviewPanel from './admin/OverviewPanel'
import AveragesPanel from './admin/AveragesPanel'
import TrendsPanel from './admin/TrendsPanel'
import HealthPanel from './admin/HealthPanel'
import HouseholdsPanel from './admin/HouseholdsPanel'
import type { Period } from './admin/api'
import { type SessionUser } from './AuthScreen'

type AdminConsoleProps = {
  user: SessionUser
  onLogout: () => void
}

const currentPeriod = (): Period => {
  const now = new Date()
  return { year: now.getFullYear(), month: now.getMonth() + 1 }
}

export default function AdminConsole({ user, onLogout }: AdminConsoleProps) {
  const [page, setPage] = useState<AdminPage>('overview')
  const [period, setPeriod] = useState<Period>(currentPeriod)
  const [periodResolved, setPeriodResolved] = useState(false)

  // פותחים את הלוח בחודש שבו יש נתונים בפועל, ולאו דווקא בחודש הנוכחי
  useEffect(() => {
    let cancelled = false
    void fetch('/admin/analytics/latest-period', { credentials: 'include' })
      .then((response) => (response.ok ? response.json() : null))
      .then((result: Period | null) => {
        if (!cancelled && result && Number.isFinite(result.year) && Number.isFinite(result.month)) {
          setPeriod({ year: result.year, month: result.month })
        }
      })
      .catch(() => { /* נופלים חזרה לחודש הנוכחי */ })
      .finally(() => { if (!cancelled) setPeriodResolved(true) })
    return () => { cancelled = true }
  }, [])

  const shiftMonth = (offset: number) => {
    setPeriod((current) => {
      const next = new Date(current.year, current.month - 1 + offset, 1)
      return { year: next.getFullYear(), month: next.getMonth() + 1 }
    })
  }

  return (
    <AdminLayout user={user} page={page} onNavigate={setPage} onLogout={onLogout} period={period} onPeriodChange={shiftMonth}>
      {!periodResolved ? (
        <p className="empty-note">טוענים את לוח הבקרה...</p>
      ) : (
        <>
          {page === 'overview' && <OverviewPanel period={period} />}
          {page === 'averages' && <AveragesPanel period={period} />}
          {page === 'trends' && <TrendsPanel period={period} />}
          {page === 'health' && <HealthPanel period={period} />}
          {page === 'households' && <HouseholdsPanel user={user} />}
        </>
      )}
    </AdminLayout>
  )
}
