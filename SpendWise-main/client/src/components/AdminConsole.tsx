import { useEffect, useState } from 'react'
import AdminPanelSettingsRounded from '@mui/icons-material/AdminPanelSettingsRounded'
import LogoutRounded from '@mui/icons-material/LogoutRounded'
import PeopleAltRounded from '@mui/icons-material/PeopleAltRounded'
import RefreshRounded from '@mui/icons-material/RefreshRounded'
import { type SessionUser } from './AuthScreen'

type Household = SessionUser

type AdminConsoleProps = {
  user: SessionUser
  onLogout: () => void
}

export default function AdminConsole({ user, onLogout }: AdminConsoleProps) {
  const [households, setHouseholds] = useState<Household[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const loadHouseholds = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch('/auth/households', { credentials: 'include' })
      const result = await response.json()
      if (!response.ok) throw new Error(result.error ?? 'לא ניתן לטעון משקי בית')
      setHouseholds(result as Household[])
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'שגיאת שרת')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void loadHouseholds() }, [])

  const setRole = async (household: Household, role: Household['role']) => {
    setNotice('')
    try {
      const response = await fetch(`/auth/households/${household.user_id}/role`, {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role }),
      })
      const result = await response.json()
      if (!response.ok) throw new Error(result.error ?? 'עדכון ההרשאה נכשל')
      setHouseholds((current) => current.map((item) => item.user_id === household.user_id ? result as Household : item))
      setNotice(`ההרשאה של ${household.first_name} ${household.last_name} עודכנה`)
    } catch (roleError) {
      setNotice(roleError instanceof Error ? roleError.message : 'עדכון ההרשאה נכשל')
    }
  }

  const setFamilySize = async (household: Household, family_size: number) => {
    try {
      const response = await fetch(`/auth/households/${household.user_id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ family_size }),
      })
      const result = await response.json()
      if (!response.ok) throw new Error(result.error ?? 'עדכון גודל משק הבית נכשל')
      setHouseholds((current) => current.map((item) => item.user_id === household.user_id ? result as Household : item))
      setNotice(`גודל משק הבית של ${household.first_name} עודכן`)
    } catch (familyError) {
      setNotice(familyError instanceof Error ? familyError.message : 'עדכון גודל משק הבית נכשל')
    }
  }

  const totalMembers = households.reduce((sum, household) => sum + household.family_size, 0)

  return (
    <div className="admin-shell" dir="rtl">
      <header className="admin-topbar"><a className="admin-brand" href="/"><span className="brand-mark"><i /><i /><i /></span><strong>שקלול<span>.</span></strong></a><span className="admin-session"><AdminPanelSettingsRounded />מנהל מערכת · {user.first_name} {user.last_name}</span><button className="secondary-button" onClick={onLogout}><LogoutRounded />יציאה</button></header>
      <main className="admin-content">
        <div className="admin-title-row"><div><p className="panel-kicker">ניהול מערכת</p><h1>משקי הבית</h1><p>ניהול החשבונות והרשאות הגישה במערכת.</p></div><button className="secondary-button" onClick={() => void loadHouseholds()} disabled={loading}><RefreshRounded />רענון</button></div>
        <section className="admin-metrics"><article><span><PeopleAltRounded /></span><small>משקי בית</small><strong>{households.length}</strong></article><article><span><PeopleAltRounded /></span><small>בני בית רשומים</small><strong>{totalMembers}</strong></article><article><span><AdminPanelSettingsRounded /></span><small>חשבונות מערכת</small><strong>הרשאות לפי תפקיד</strong></article></section>
        <section className="panel admin-table-panel"><div className="panel-heading"><div><p className="panel-kicker">חשבונות רשומים</p><h2>ניהול גישה</h2></div><span className="admin-count">{households.length} חשבונות</span></div>
          {error ? <div className="admin-error" role="alert">{error}</div> : loading ? <p className="empty-note">טוענים חשבונות...</p> : households.length === 0 ? <p className="empty-note">עדיין לא נפתחו חשבונות משק בית.</p> : <div className="admin-table-scroll"><table className="admin-table"><thead><tr><th>שם החשבון</th><th>אימייל</th><th>גודל משק הבית</th><th>נוצר בתאריך</th><th>הרשאה</th></tr></thead><tbody>{households.map((household) => <tr key={household.user_id}><td><strong>{household.first_name} {household.last_name}</strong><small>מזהה {household.user_id}</small></td><td>{household.email}</td><td><select aria-label={`גודל משק הבית עבור ${household.email}`} value={household.family_size} onChange={(event) => void setFamilySize(household, Number(event.target.value))}>{Array.from({ length: 10 }, (_, index) => index + 1).map((size) => <option key={size} value={size}>{size} נפשות</option>)}</select></td><td>{household.join_date ? new Intl.DateTimeFormat('he-IL', { dateStyle: 'medium' }).format(new Date(household.join_date)) : '—'}</td><td><select aria-label={`הרשאה עבור ${household.email}`} value={household.role} onChange={(event) => void setRole(household, event.target.value as Household['role'])}><option value="household">משק בית</option><option value="admin">מנהל מערכת</option></select></td></tr>)}</tbody></table></div>}
          {notice && <p className="admin-notice" role="status">{notice}</p>}
        </section>
        <p className="admin-footnote"><AdminPanelSettingsRounded /> שינוי תפקיד משפיע על ההרשאות של החשבון באופן מיידי.</p>
      </main>
    </div>
  )
}