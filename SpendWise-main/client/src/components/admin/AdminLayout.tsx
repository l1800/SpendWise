import type { ReactNode } from 'react'
import AdminPanelSettingsRounded from '@mui/icons-material/AdminPanelSettingsRounded'
import DashboardRounded from '@mui/icons-material/DashboardRounded'
import InsightsRounded from '@mui/icons-material/InsightsRounded'
import ShowChartRounded from '@mui/icons-material/ShowChartRounded'
import HealthAndSafetyRounded from '@mui/icons-material/HealthAndSafetyRounded'
import PeopleAltRounded from '@mui/icons-material/PeopleAltRounded'
import LogoutRounded from '@mui/icons-material/LogoutRounded'
import ChevronLeftRounded from '@mui/icons-material/ChevronLeftRounded'
import ChevronRightRounded from '@mui/icons-material/ChevronRightRounded'
import type { SessionUser } from '../AuthScreen'

export type AdminPage = 'overview' | 'averages' | 'trends' | 'health' | 'households'

type NavItem = { id: AdminPage; label: string; caption: string; icon: typeof DashboardRounded }

const navItems: NavItem[] = [
  { id: 'overview', label: 'סקירה כללית', caption: 'מדדי מערכת', icon: DashboardRounded },
  { id: 'averages', label: 'ממוצעים והשוואות', caption: 'לפי קטגוריה', icon: InsightsRounded },
  { id: 'trends', label: 'מעקב מגמות', caption: 'התפתחות חודשית', icon: ShowChartRounded },
  { id: 'health', label: 'בריאות פיננסית', caption: 'דירוג משקי בית', icon: HealthAndSafetyRounded },
  { id: 'households', label: 'משקי בית', caption: 'ניהול הרשאות', icon: PeopleAltRounded },
]

const monthLabel = (year: number, month: number) =>
  new Intl.DateTimeFormat('he-IL', { month: 'long', year: 'numeric' }).format(new Date(year, month - 1, 1))

type AdminLayoutProps = {
  user: SessionUser
  page: AdminPage
  onNavigate: (page: AdminPage) => void
  onLogout: () => void
  period: { year: number; month: number }
  onPeriodChange: (monthOffset: number) => void
  children: ReactNode
}

export default function AdminLayout({ user, page, onNavigate, onLogout, period, onPeriodChange, children }: AdminLayoutProps) {
  const current = navItems.find((item) => item.id === page) ?? navItems[0]

  return (
    <div className="admin-shell" dir="rtl">
      <aside className="control-nav">
        <a className="admin-brand" href="/"><span className="brand-mark"><i /><i /><i /></span><strong>שקלול<span>.</span></strong></a>
        <div className="control-nav-label"><AdminPanelSettingsRounded /> מרכז שליטה</div>
        <nav className="control-links" aria-label="ניווט ניהול">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                className={`control-link ${page === item.id ? 'active' : ''}`}
                onClick={() => onNavigate(item.id)}
                aria-current={page === item.id ? 'page' : undefined}
              >
                <span className="control-link-icon"><Icon /></span>
                <span><strong>{item.label}</strong><small>{item.caption}</small></span>
              </button>
            )
          })}
        </nav>
        <div className="control-profile">
          <span className="profile-avatar">{user.first_name.slice(0, 1)}</span>
          <span><strong>{user.first_name} {user.last_name}</strong><small>מנהל מערכת</small></span>
          <button className="icon-button" aria-label="יציאה" onClick={onLogout}><LogoutRounded /></button>
        </div>
      </aside>

      <div className="control-main">
        <header className="control-topbar">
          <div className="breadcrumbs"><span>מרכז שליטה</span><span className="crumb-divider">/</span><strong>{current.label}</strong></div>
          <div className="control-period">
            <button aria-label="חודש הבא" onClick={() => onPeriodChange(1)}><ChevronRightRounded /></button>
            <span>{monthLabel(period.year, period.month)}</span>
            <button aria-label="חודש קודם" onClick={() => onPeriodChange(-1)}><ChevronLeftRounded /></button>
          </div>
        </header>
        <main className="control-content">{children}</main>
      </div>
    </div>
  )
}
