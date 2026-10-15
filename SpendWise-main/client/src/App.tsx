import { useEffect, useState, type CSSProperties, type FormEvent } from 'react'
import './App.css'
import AddRounded from '@mui/icons-material/AddRounded'
import ArrowBackIosNewRounded from '@mui/icons-material/ArrowBackIosNewRounded'
import AutoGraphRounded from '@mui/icons-material/AutoGraphRounded'
import CalendarMonthRounded from '@mui/icons-material/CalendarMonthRounded'
import CheckCircleRounded from '@mui/icons-material/CheckCircleRounded'
import CloseRounded from '@mui/icons-material/CloseRounded'
import DashboardRounded from '@mui/icons-material/DashboardRounded'
import ExpandMoreRounded from '@mui/icons-material/ExpandMoreRounded'
import FlagRounded from '@mui/icons-material/FlagRounded'
import LightbulbRounded from '@mui/icons-material/LightbulbRounded'
import MenuRounded from '@mui/icons-material/MenuRounded'
import NotificationsNoneRounded from '@mui/icons-material/NotificationsNoneRounded'
import ReceiptLongRounded from '@mui/icons-material/ReceiptLongRounded'
import SavingsRounded from '@mui/icons-material/SavingsRounded'
import TrendingDownRounded from '@mui/icons-material/TrendingDownRounded'
import TrendingUpRounded from '@mui/icons-material/TrendingUpRounded'
import WarningAmberRounded from '@mui/icons-material/WarningAmberRounded'
import AuthScreen, { type SessionUser } from './components/AuthScreen'
import AdminConsole from './components/AdminConsole'

type Category = { category_id: number; category_name: string; total_amount: number; is_essential: boolean; recommended_budget: number }
type Transaction = { id: number; category_id: number; title: string; amount: number; date: string; type: 'expense' | 'income' }
type Alert = { alert_id?: number; category_name?: string; message?: string; severity?: string }
type SavingsGoal = { id: number; name: string; current_balance: number; target_amount: number | null }
type Page = 'overview' | 'expenses' | 'plan' | 'insights' | 'goals'
type EntryKind = 'expense' | 'income'
type DashboardData = { totalIncome: number; fixedCosts: number; netBudget: number; stressScore: number; explanation: string; categories: Category[]; transactions: Transaction[]; alerts: Alert[] }

const demoCategories: Category[] = [
  { category_id: 1, category_name: 'דיור', total_amount: 5300, is_essential: true, recommended_budget: 5200 },
  { category_id: 2, category_name: 'חשבונות וארנונה', total_amount: 1160, is_essential: true, recommended_budget: 1100 },
  { category_id: 3, category_name: 'מזון וסופר', total_amount: 2820, is_essential: true, recommended_budget: 2600 },
  { category_id: 4, category_name: 'חינוך וילדים', total_amount: 1960, is_essential: true, recommended_budget: 1850 },
  { category_id: 5, category_name: 'תחבורה', total_amount: 850, is_essential: false, recommended_budget: 900 },
  { category_id: 6, category_name: 'בריאות', total_amount: 490, is_essential: true, recommended_budget: 600 },
  { category_id: 7, category_name: 'ביגוד', total_amount: 430, is_essential: false, recommended_budget: 500 },
  { category_id: 8, category_name: 'בילויים ואוכל בחוץ', total_amount: 620, is_essential: false, recommended_budget: 520 },
  { category_id: 9, category_name: 'צדקה ומתנות', total_amount: 1020, is_essential: false, recommended_budget: 900 },
  { category_id: 10, category_name: 'חיסכון', total_amount: 1000, is_essential: false, recommended_budget: 1000 },
  { category_id: 11, category_name: 'תקשורת', total_amount: 360, is_essential: true, recommended_budget: 400 },
  { category_id: 12, category_name: 'הלוואות', total_amount: 1250, is_essential: true, recommended_budget: 1250 },
  { category_id: 13, category_name: 'הוצאות שונות', total_amount: 390, is_essential: false, recommended_budget: 450 },
]

const todayString = () => {
  const today = new Date()
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
}

const demoData = (): DashboardData => ({
  totalIncome: 20000, fixedCosts: 7090, netBudget: 12910, stressScore: 28,
  explanation: 'ההוצאות יציבות יחסית. אפשר לפנות עוד מקום בתקציב הבילויים והקניות.',
  categories: demoCategories,
  transactions: [
    { id: 1, category_id: 3, title: 'קנייה שבועית בסופר', amount: 684, date: todayString(), type: 'expense' },
    { id: 2, category_id: 4, title: 'צהרון וחוגים', amount: 920, date: todayString(), type: 'expense' },
    { id: 3, category_id: 1, title: 'שכר דירה', amount: 5300, date: todayString(), type: 'expense' },
    { id: 4, category_id: 0, title: 'משכורת חודשית', amount: 18000, date: todayString(), type: 'income' },
  ],
  alerts: [{ category_name: 'בילויים ואוכל בחוץ', message: 'ההוצאה החודשית מתקרבת לתקרה שהוגדרה.', severity: 'info' }],
})

const money = (amount: number) => new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS', maximumFractionDigits: 0 }).format(amount || 0)
const numberFrom = (value: unknown, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback

async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, { credentials: 'include', ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } })
  if (!response.ok) throw new Error(`Request failed (${response.status})`)
  return response.json() as Promise<T>
}

const pages: { id: Page; label: string; icon: typeof DashboardRounded }[] = [
  { id: 'overview', label: 'תמונת מצב', icon: DashboardRounded },
  { id: 'expenses', label: 'הוצאות ותנועות', icon: ReceiptLongRounded },
  { id: 'plan', label: 'תוכנית תקציב', icon: FlagRounded },
  { id: 'insights', label: 'תובנות פיננסיות', icon: AutoGraphRounded },
  { id: 'goals', label: 'יעדים וחיסכון', icon: SavingsRounded },
]

function BrandMark() {
  return <div className="brand-lockup" aria-label="שקלול"><span className="brand-mark"><i /><i /><i /></span><span className="brand-name">שקלול<span>.</span></span></div>
}

function DashboardApp({ user, onLogout }: { user: SessionUser; onLogout: () => void }) {
  const [page, setPage] = useState<Page>('overview')
  const [data, setData] = useState<DashboardData>(demoData)
  const [connection, setConnection] = useState<'loading' | 'demo' | 'live' | 'partial'>('loading')
  const userId = user.user_id
  const [monthOffset, setMonthOffset] = useState(0)
  const [entryKind, setEntryKind] = useState<EntryKind | null>(null)
  const [toast, setToast] = useState('')
  const [isPlanLoading, setIsPlanLoading] = useState(false)
  const [plan, setPlan] = useState<Record<string, unknown> | null>(null)
  const [dismissedAlerts, setDismissedAlerts] = useState<number[]>([])
  const [expenseTypes, setExpenseTypes] = useState<{ id: number; name: string }[]>([])
  const [incomeCategories, setIncomeCategories] = useState<{ id: number; name: string }[]>([])
  const [incomeFrequencyId, setIncomeFrequencyId] = useState(1)
  const [savingsGoals, setSavingsGoals] = useState<SavingsGoal[]>([])
  const [goalDialog, setGoalDialog] = useState<'create' | 'deposit' | null>(null)
  const [selectedGoalId, setSelectedGoalId] = useState<number | null>(null)

  const period = new Date()
  period.setDate(1)
  period.setMonth(period.getMonth() + monthOffset)
  const year = period.getFullYear()
  const month = period.getMonth() + 1
  const monthLabel = new Intl.DateTimeFormat('he-IL', { month: 'long', year: 'numeric' }).format(period)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      setConnection('loading')
      const sample = demoData()
      try {
        const results = await Promise.allSettled([
          requestJson<Record<string, unknown>>(`/budget/net/${userId}/${year}/${month}`),
          requestJson<Record<string, unknown>>(`/budget/expenses-by-category/${userId}/${year}/${month}`),
          requestJson<Record<string, unknown>>(`/budget/stress/${userId}/${year}/${month}`),
          requestJson<Record<string, unknown>>(`/budget/standard/${user.family_size}`),
          requestJson<{ ExpenseTypeId: number; ExpenseTypeName: string }[]>('/expense_types'),
          requestJson<{ category_id: number; category_name: string }[]>('/income_categories'),
          requestJson<{ frequency_id: number; frequency_name: string }[]>('/income_frequency'),
          requestJson<Alert[]>(`/api/early-warning/alerts?user_id=${userId}&year=${year}&month=${month}`),
          requestJson<SavingsGoal[]>(`/savings/goals/user/${userId}`),
          requestJson<{ categories: Record<string, unknown>[] } & Record<string, unknown>>('/auth/catalog'),
        ])
        if (cancelled) return
        const value = (index: number) => results[index].status === 'fulfilled' ? results[index].value : null
        const net = value(0) as Record<string, unknown> | null
        const expenseSummary = value(1) as Record<string, unknown> | null
        const stress = value(2) as Record<string, unknown> | null
        const standards = value(3) as Record<string, unknown> | null
        const categoryRows = Array.isArray(expenseSummary?.categories) ? expenseSummary.categories as Record<string, unknown>[] : []
        const standardRows = Array.isArray(standards?.standards) ? standards.standards as Record<string, unknown>[] : []
        const liveExpenses = categoryRows.map((category) => {
          const standard = standardRows.find((row) => row.category_id === category.category_id)
          return {
            category_id: numberFrom(category.category_id), category_name: String(category.category_name ?? 'קטגוריה'),
            total_amount: numberFrom(category.total_amount), is_essential: Boolean(category.is_essential),
            recommended_budget: numberFrom(standard?.recommended_budget, numberFrom(category.total_amount) * 1.05),
          }
        })
        const catalog = value(9) as { categories?: Record<string, unknown>[] } | null
        const categoryCatalog = Array.isArray(catalog?.categories) ? catalog.categories : []
        const householdCategories = categoryCatalog.map((category) => {
          const spent = liveExpenses.find((item) => item.category_id === numberFrom(category.category_id))
          return {
            category_id: numberFrom(category.category_id),
            category_name: String(category.category_name ?? 'קטגוריה'),
            is_essential: Boolean(category.is_essential),
            total_amount: spent?.total_amount ?? 0,
            recommended_budget: numberFrom(category.recommended_budget),
          }
        })
        setData({
          ...sample,
          totalIncome: numberFrom(net?.total_income, sample.totalIncome),
          fixedCosts: numberFrom(net?.fixed_costs, sample.fixedCosts),
          netBudget: numberFrom(net?.net_budget, sample.netBudget),
          stressScore: numberFrom(stress?.['ציון'] ?? stress?.score, sample.stressScore),
          explanation: String(stress?.explanation ?? sample.explanation),
          categories: householdCategories.length ? householdCategories : liveExpenses.length ? liveExpenses : net && expenseSummary ? [] : sample.categories,
          transactions: [],
          alerts: (value(7) as Alert[] | null) ?? sample.alerts,
        })
        setConnection(net && expenseSummary && householdCategories.length ? 'live' : 'partial')
        const goals = value(8) as SavingsGoal[] | null
        setSavingsGoals(goals ?? [])
        const types = value(4) as { ExpenseTypeId: number; ExpenseTypeName: string }[] | null
        const incomes = value(5) as { category_id: number; category_name: string }[] | null
        const frequencies = value(6) as { frequency_id: number; frequency_name: string }[] | null
        setExpenseTypes(types?.map((type) => ({ id: type.ExpenseTypeId, name: type.ExpenseTypeName })) ?? [])
        setIncomeCategories(incomes?.map((item) => ({ id: item.category_id, name: item.category_name })) ?? [])
        if (frequencies?.[0]) setIncomeFrequencyId(frequencies[0].frequency_id)
      } catch {
        if (!cancelled) { setData(sample); setConnection('demo') }
      }
    }
    void load()
    return () => { cancelled = true }
  }, [month, user.family_size, userId, year])

  useEffect(() => {
    if (!toast) return
    const timeout = window.setTimeout(() => setToast(''), 3200)
    return () => window.clearTimeout(timeout)
  }, [toast])

  const totalSpent = data.categories.reduce((sum, item) => sum + item.total_amount, 0)
  const remaining = data.totalIncome - totalSpent
  const healthScore = Math.max(0, Math.min(100, 100 - data.stressScore))
  const alertList = data.alerts.filter((item) => !item.alert_id || !dismissedAlerts.includes(item.alert_id))
  const overBudgetCount = data.categories.filter((item) => item.total_amount > item.recommended_budget).length
  const title = pages.find((item) => item.id === page)?.label ?? 'תמונת מצב'
  const status = connection === 'live' ? 'מחובר לנתונים' : connection === 'partial' ? 'חיבור חלקי' : connection === 'loading' ? 'מתחבר...' : 'נתוני הדגמה'

  const submitEntry = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!entryKind) return
    const form = new FormData(event.currentTarget)
    const amount = numberFrom(form.get('amount'))
    const date = String(form.get('date') || todayString())
    const categoryId = numberFrom(form.get('category'))
    if (amount <= 0 || !categoryId) { setToast('נא לבחור קטגוריה ולהזין סכום תקין'); return }
    if (entryKind === 'income' && connection === 'live' && !incomeCategories.length) { setToast('לא נמצאו קטגוריות הכנסה בשרת'); return }
    const name = entryKind === 'expense'
      ? data.categories.find((item) => item.category_id === categoryId)?.category_name ?? 'הוצאה חדשה'
      : incomeCategories.find((item) => item.id === categoryId)?.name ?? 'הכנסה חדשה'
    const transaction: Transaction = { id: Date.now(), category_id: categoryId, title: name, amount, date, type: entryKind }
    try {
      if (userId && connection !== 'demo') {
        const payload = entryKind === 'expense'
          ? { user_id: userId, amount, date, expense_type_id: numberFrom(form.get('expenseType'), expenseTypes[0]?.id ?? 1), category_id: categoryId }
          : { user_id: userId, amount, date, frequency_id: incomeFrequencyId, category_id: categoryId }
        await requestJson(entryKind === 'expense' ? '/expenses/' : '/income', { method: 'POST', body: JSON.stringify(payload) })
      } else {
        const old = JSON.parse(localStorage.getItem('spendwise-demo-transactions') ?? '[]') as Transaction[]
        localStorage.setItem('spendwise-demo-transactions', JSON.stringify([transaction, ...old].slice(0, 20)))
      }
      setData((current) => ({
        ...current,
        totalIncome: current.totalIncome + (entryKind === 'income' ? amount : 0),
        categories: entryKind === 'expense' ? current.categories.map((item) => item.category_id === categoryId ? { ...item, total_amount: item.total_amount + amount } : item) : current.categories,
        transactions: [transaction, ...current.transactions].slice(0, 8),
      }))
      setEntryKind(null)
      setToast(userId && connection !== 'demo' ? 'התנועה נשמרה בהצלחה' : 'נשמר במצב הדגמה בדפדפן')
    } catch { setToast('השמירה מול השרת נכשלה. בדקו שה־API פעיל ונסו שוב.') }
  }

  const buildPlan = async () => {
    if (!userId) {
      setPlan({ budget: data.categories.map((item) => ({ category_name: item.category_name, current_spending: item.total_amount, planned: Math.min(item.total_amount, item.recommended_budget), target: item.recommended_budget })), monthly_limit: data.netBudget })
      setPage('plan'); setToast('תוכנית דוגמה נבנתה לפי נתוני המשפחה'); return
    }
    setIsPlanLoading(true)
    try {
      setPlan(await requestJson<Record<string, unknown>>(`/budget/plan/${userId}/${year}/${month}`))
      setPage('plan'); setToast('תוכנית התקציב חושבה ונשמרה')
    } catch { setToast('לא ניתן לבנות תוכנית כרגע. בדקו שהשרת והטבלאות זמינים.') }
    finally { setIsPlanLoading(false) }
  }

  const dismissAlert = async (alert: Alert) => {
    if (alert.alert_id && connection !== 'demo' && userId) {
      try { await requestJson(`/api/early-warning/alerts/${alert.alert_id}/dismiss`, { method: 'PUT' }) }
      catch { setToast('לא ניתן לעדכן את ההתראה בשרת'); return }
    }
    if (alert.alert_id) setDismissedAlerts((items) => [...items, alert.alert_id as number])
    else setData((current) => ({ ...current, alerts: current.alerts.filter((item) => item !== alert) }))
    setToast('ההתראה סומנה כטופלה')
  }

  const submitGoalAction = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!userId || connection === 'demo') {
      setToast('כדי לשמור יעדים, יש להפעיל את שרת ה־API ולזרוע את נתוני הדמו')
      return
    }
    const form = new FormData(event.currentTarget)
    try {
      if (goalDialog === 'create') {
        const created = await requestJson<{ id: number; name: string }>('/savings/goals', {
          method: 'POST',
          body: JSON.stringify({ user_id: userId, name: String(form.get('name') || '').trim(), target_amount: numberFrom(form.get('target')) }),
        })
        setSavingsGoals((goals) => [...goals, { ...created, current_balance: 0, target_amount: numberFrom(form.get('target')) }])
        setToast('יעד החיסכון נוסף')
      } else if (selectedGoalId) {
        const amount = numberFrom(form.get('deposit'))
        await requestJson(`/savings/goals/${selectedGoalId}/deposit`, {
          method: 'POST', body: JSON.stringify({ amount, description: 'הפקדה ליעד חיסכון' }),
        })
        setSavingsGoals((goals) => goals.map((goal) => goal.id === selectedGoalId ? { ...goal, current_balance: goal.current_balance + amount } : goal))
        setToast('ההפקדה נוספה ליעד')
      }
      setGoalDialog(null)
    } catch { setToast('שמירת היעד נכשלה. בדקו שה־API זמין ונסו שוב.') }
  }

  const displayTransactions = (() => {
    try {
      const saved = JSON.parse(localStorage.getItem('spendwise-demo-transactions') ?? '[]') as Transaction[]
      return [...saved, ...data.transactions.filter((item) => !saved.some((entry) => entry.id === item.id))].slice(0, 8)
    }
    catch { return data.transactions }
  })()
  const visibleSavingsGoals = savingsGoals.length
    ? savingsGoals
    : connection === 'demo' || connection === 'loading'
      ? [{ id: -1, name: 'קרן חירום', current_balance: 8500, target_amount: 30000 }, { id: -2, name: 'חופשה משפחתית', current_balance: 5000, target_amount: 12000 }, { id: -3, name: 'חיסכון לילדים', current_balance: 3200, target_amount: 20000 }]
      : []

  return (
    <div className="app-shell" dir="rtl">
      <aside className="sidebar">
        <div className="sidebar-top"><BrandMark /><button className="icon-button mobile-menu" aria-label="פתיחת תפריט"><MenuRounded /></button></div>
        <div className="workspace-label">המרחב המשפחתי</div>
        <button className="family-switcher"><span className="family-avatar">{user.first_name.slice(0, 1)}</span><span className="family-name"><strong>משפחת {user.last_name}</strong><small>{user.family_size} בני בית</small></span><ExpandMoreRounded className="switcher-chevron" /></button>
        <div className="nav-caption">ניהול פיננסי</div>
        <nav className="main-nav" aria-label="ניווט ראשי">{pages.map((item) => { const Icon = item.icon; return <button key={item.id} className={`nav-item ${page === item.id ? 'active' : ''}`} onClick={() => setPage(item.id)}><Icon /><span>{item.label}</span>{item.id === 'expenses' && alertList.length > 0 && <i className="nav-dot" />}</button> })}</nav>
        <div className="sidebar-bottom"><div className="sidebar-tip"><span className="tip-icon"><LightbulbRounded /></span><p><strong>טיפ קטן לחודש</strong>בדקו את ההוצאות המשתנות לפני סוף השבוע.</p></div><div className="profile-row"><span className="profile-avatar">{user.first_name.slice(0, 1)}</span><span><strong>{user.first_name} {user.last_name}</strong><small>{user.email}</small></span><button className="profile-more" aria-label="יציאה מהחשבון" onClick={onLogout}>↪</button></div></div>
      </aside>

      <main className="main-content">
        <header className="topbar"><div className="breadcrumbs"><span>המרחב שלי</span><span className="crumb-divider">/</span><strong>{title}</strong></div><div className="topbar-actions"><span className={`connection-pill ${connection}`}><i />{status}</span><button className="icon-button notification-button" aria-label="התראות" onClick={() => setPage('overview')}><NotificationsNoneRounded />{alertList.length > 0 && <i />}</button><span className="topbar-divider" /><div className="date-switcher"><CalendarMonthRounded /><span>{monthLabel}</span><button aria-label="חודש הבא" onClick={() => setMonthOffset((offset) => offset + 1)}>›</button><button aria-label="חודש קודם" onClick={() => setMonthOffset((offset) => offset - 1)}>‹</button></div></div></header>
        <div className="page-wrap">
          <section className="page-heading"><div><p className="eyebrow">{monthLabel}<span>·</span> כלכלת הבית</p><h1>{page === 'overview' ? 'הכסף שלכם, בתמונה אחת.' : title}</h1><p className="heading-subtitle">{page === 'overview' ? 'הנה מה שקורה בתקציב המשפחתי החודש.' : 'נתונים ברורים שיעזרו לכם לקבל החלטות טובות.'}</p></div><button className="primary-button" onClick={() => setEntryKind('expense')}><AddRounded />הוספת תנועה</button></section>

          {connection !== 'live' && <div className={`demo-notice ${connection}`}><span className="notice-symbol"><WarningAmberRounded /></span><span><strong>{connection === 'loading' ? 'מתחברים לשרת...' : connection === 'partial' ? 'החיבור לשרת חלקי' : 'אתם צופים בנתוני הדגמה'}</strong><small>{connection === 'demo' ? 'הנתונים ממחישים את המערכת ואינם נשלפים ממסד הנתונים.' : connection === 'partial' ? 'חלק מהנתונים נטענו מהשרת, ופריטים חסרים מוצגים כהדגמה.' : 'טוענים את נתוני המשפחה.'}</small></span></div>}

          {page === 'overview' && <>
            <section className="metric-grid" aria-label="סיכום חודשי">
              <article className="metric-card balance-card"><div className="metric-top"><span className="metric-label">נשאר לכם החודש</span><span className="metric-icon balance-icon"><SavingsRounded /></span></div><strong className="metric-value">{money(remaining)}</strong><span className={`metric-note ${remaining >= 0 ? 'positive' : 'negative'}`}><CheckCircleRounded />{remaining >= 0 ? 'התקציב עדיין מאוזן' : 'ההוצאות עברו את ההכנסות'}</span><div className="balance-track"><span style={{ width: `${Math.max(3, Math.min(100, totalSpent / Math.max(data.totalIncome, 1) * 100))}%` }} /></div><div className="track-labels"><span>הוצאות {money(totalSpent)}</span><span>הכנסות {money(data.totalIncome)}</span></div></article>
              <article className="metric-card"><div className="metric-top"><span className="metric-label">הכנסות החודש</span><span className="metric-icon income-icon"><TrendingUpRounded /></span></div><strong className="metric-value">{money(data.totalIncome)}</strong><span className="metric-note muted">הכנסה משפחתית כוללת</span><div className="mini-bars income-bars" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /></div></article>
              <article className="metric-card"><div className="metric-top"><span className="metric-label">הוצאות החודש</span><span className="metric-icon expense-icon"><TrendingDownRounded /></span></div><strong className="metric-value">{money(totalSpent)}</strong><span className="metric-note muted">{overBudgetCount ? `${overBudgetCount} קטגוריות מעל היעד` : 'בתוך המסגרת שהוגדרה'}</span><div className="mini-bars expense-bars" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /></div></article>
              <article className="metric-card health-card"><div className="metric-top"><span className="metric-label">בריאות פיננסית</span><span className="metric-icon health-icon"><AutoGraphRounded /></span></div><div className="health-score"><strong>{healthScore}</strong><span>/ 100</span></div><span className="metric-note positive"><CheckCircleRounded />מצב יציב</span><div className="health-meter"><span style={{ width: `${healthScore}%` }} /></div></article>
            </section>

            <section className="content-grid"><div className="panel category-panel"><div className="panel-heading"><div><p className="panel-kicker">חלוקת הוצאות</p><h2>לאן הכסף הולך</h2></div><button className="text-button" onClick={() => setPage('expenses')}>כל הקטגוריות <ArrowBackIosNewRounded /></button></div><div className="category-list">{[...data.categories].sort((a, b) => b.total_amount - a.total_amount).slice(0, 6).map((category, index) => { const ratio = Math.min(100, Math.round(category.total_amount / Math.max(category.recommended_budget, 1) * 100)); return <div className="category-row" key={category.category_id}><span className={`category-mark color-${index % 5}`} /><div className="category-info"><div><strong>{category.category_name}</strong><small>{category.is_essential ? 'הוצאה חיונית' : 'הוצאה גמישה'}</small></div><div className="category-track"><span className={`category-progress ${ratio > 100 ? 'over' : ''}`} style={{ width: `${ratio}%` }} /></div></div><div className="category-numbers"><strong>{money(category.total_amount)}</strong><small>מתוך {money(category.recommended_budget)}</small></div></div> })}</div></div>
              <div className="side-stack"><div className="panel insight-card"><div className="insight-head"><span className="insight-icon"><LightbulbRounded /></span><span className="insight-tag">תובנה חכמה</span></div><h2>{overBudgetCount ? 'אפשר לשפר בלי לוותר על מה שחשוב.' : 'אתם שומרים על איזון יפה.'}</h2><p>{data.explanation}</p><button className="insight-link" onClick={() => setPage('insights')}>לכל התובנות <ArrowBackIosNewRounded /></button><span className="insight-decoration" /></div>
                <div className="panel alert-panel"><div className="panel-heading compact"><div><p className="panel-kicker">מעקב חכם</p><h2>מה דורש תשומת לב</h2></div><span className="alert-count">{alertList.length}</span></div>{alertList.length ? alertList.slice(0, 2).map((alert, index) => <div className="alert-item" key={alert.alert_id ?? index}><span className="alert-symbol"><WarningAmberRounded /></span><span className="alert-copy"><strong>{alert.category_name ?? 'עדכון תקציבי'}</strong><small>{alert.message ?? 'נמצאה חריגה שכדאי לבדוק.'}</small></span><button className="alert-dismiss" aria-label="סימון כטופל" onClick={() => void dismissAlert(alert)}><CloseRounded /></button></div>) : <p className="empty-note">אין כרגע התראות פתוחות.</p>}</div></div></section>
            <section className="panel transactions-panel"><div className="panel-heading"><div><p className="panel-kicker">התנועות האחרונות</p><h2>מה קרה בחשבון</h2></div><button className="text-button" onClick={() => setPage('expenses')}>לכל התנועות <ArrowBackIosNewRounded /></button></div><TransactionTable transactions={displayTransactions.slice(0, 4)} /></section>
          </>}

          {page === 'expenses' && <section className="detail-grid"><div className="panel detail-main"><div className="panel-heading"><div><p className="panel-kicker">מעקב חודשי</p><h2>הוצאות לפי קטגוריה</h2></div><button className="secondary-button" onClick={() => setEntryKind('expense')}><AddRounded />הוצאה חדשה</button></div><div className="full-category-list">{[...data.categories].sort((a, b) => b.total_amount - a.total_amount).map((category) => { const ratio = Math.min(100, Math.round(category.total_amount / Math.max(category.recommended_budget, 1) * 100)); return <div className="full-category-row" key={category.category_id}><div className="full-category-title"><span className={`category-mark color-${category.category_id % 5}`} /><div><strong>{category.category_name}</strong><small>{category.is_essential ? 'חיוני' : 'גמיש'}</small></div></div><div className="wide-progress"><span className={ratio > 100 ? 'over' : ''} style={{ width: `${ratio}%` }} /></div><div className="full-category-total"><strong>{money(category.total_amount)}</strong><small>יעד {money(category.recommended_budget)}</small></div></div> })}</div></div><div className="panel transactions-panel detail-transactions"><div className="panel-heading"><div><p className="panel-kicker">תנועות</p><h2>העדכניות ביותר</h2></div></div><TransactionTable transactions={displayTransactions} /></div></section>}

          {page === 'plan' && <section className="panel plan-panel"><div className="plan-hero"><span className="plan-hero-icon"><FlagRounded /></span><div><p className="panel-kicker">תכנון חכם לחודש</p><h2>{plan ? 'תוכנית התקציב שלכם' : 'בואו נתכנן חודש רגוע יותר.'}</h2><p>{plan ? 'התקציב חושב לפי ההכנסות, דפוסי ההוצאה והעדיפויות שלכם.' : 'המערכת תדרג קטגוריות, תחשב קיצוץ ותבנה מסגרת חדשה.'}</p></div>{!plan && <button className="primary-button" disabled={isPlanLoading} onClick={() => void buildPlan()}>{isPlanLoading ? 'מחשב תוכנית...' : 'בנו לי תוכנית'}<ArrowBackIosNewRounded /></button>}</div><div className="plan-summary"><div><small>הכנסה חודשית</small><strong>{money(data.totalIncome)}</strong></div><div><small>הוצאות קבועות</small><strong>{money(data.fixedCosts)}</strong></div><div><small>כסף לתכנון</small><strong>{money(data.netBudget)}</strong></div><div><small>קטגוריות מעל היעד</small><strong>{overBudgetCount}</strong></div></div>{(plan && Array.isArray(plan.budget) ? plan.budget as Record<string, unknown>[] : [...data.categories].sort((a, b) => b.total_amount / b.recommended_budget - a.total_amount / a.recommended_budget) as unknown as Record<string, unknown>[]).map((item, index) => { const category = data.categories.find((row) => row.category_name === item.category_name); const current = numberFrom(item.current_spending ?? item.total_amount); const planned = numberFrom(item.planned ?? item.planned_amount ?? Math.min(current, category?.recommended_budget ?? 0)); return <div className="plan-row" key={String(item.category_id ?? index)}><span className={`category-mark color-${index % 5}`} /><strong>{String(item.category_name ?? 'קטגוריה')}</strong><span className="plan-current">כיום {money(current)}</span><span className="plan-target">יעד {money(numberFrom(item.target, category?.recommended_budget ?? 0))}</span><b>{money(planned)}</b></div> })}{plan && <button className="text-button rebuild-button" onClick={() => void buildPlan()}>חישוב מחדש <AutoGraphRounded /></button>}</section>}

          {page === 'insights' && <section className="insights-layout"><div className="panel health-detail"><div className="panel-heading"><div><p className="panel-kicker">מדד משולב</p><h2>הבריאות הפיננסית שלכם</h2></div><span className="health-badge"><CheckCircleRounded />ציון {healthScore}</span></div><div className="health-detail-content"><div className="score-ring" style={{ '--score': `${healthScore * 3.6}deg` } as CSSProperties}><div><strong>{healthScore}</strong><small>מתוך 100</small></div></div><div className="health-explanation"><span className="panel-kicker">הסבר המערכת</span><h3>{healthScore >= 70 ? 'התנהלות טובה עם מקום לצמיחה' : 'כמה שינויים קטנים יכולים לעזור'}</h3><p>{data.explanation}</p><p className="engine-note">הציון משלב חריגות, מגמות ולחץ תקציבי לפי מנוע הבריאות הפיננסית.</p></div></div></div><div className="panel suggestion-panel"><div className="panel-heading"><div><p className="panel-kicker">הצעד הבא</p><h2>המלצות למשפחה</h2></div></div><div className="suggestion"><span className="suggestion-number">01</span><div><strong>בדקו את הקטגוריות מעל היעד</strong><p>התחילו בסעיפים הגמישים, והשאירו הוצאות חיוניות וקבועות מוגנות.</p></div></div><div className="suggestion"><span className="suggestion-number">02</span><div><strong>השתמשו בתוכנית החודשית</strong><p>הקצאה ברורה מראש מאפשרת לעקוב בלי להפתיע את התקציב.</p></div></div><button className="secondary-button" onClick={() => void buildPlan()}><AutoGraphRounded />קבלת תוכנית מותאמת</button></div><div className="panel category-panel insight-categories"><div className="panel-heading"><div><p className="panel-kicker">חריגות לפי קטגוריה</p><h2>איפה כדאי להתמקד</h2></div></div>{data.categories.filter((item) => item.total_amount > item.recommended_budget).map((item, index) => <div className="attention-row" key={item.category_id}><span className={`category-mark color-${index % 5}`} /><strong>{item.category_name}</strong><span>חריגה של {money(item.total_amount - item.recommended_budget)}</span><span className="attention-ratio">{Math.round((item.total_amount / item.recommended_budget - 1) * 100)}%+</span></div>)}</div></section>}

          {page === 'goals' && <section className="goals-layout"><div className="goal-feature"><div className="goal-feature-top"><span className="goal-feature-icon"><SavingsRounded /></span><span className="goal-chip">{connection === 'live' ? savingsGoals.length ? 'יעד פעיל' : 'יעדים ריקים' : 'תצוגת הדגמה'}</span></div><p className="panel-kicker">חיסכון משפחתי</p><h2>{visibleSavingsGoals[0]?.name ?? 'עוד לא הוגדר יעד'}</h2>{visibleSavingsGoals.length ? <><p className="goal-description">בונים מרווח נשימה להוצאות בלתי צפויות, צעד אחר צעד.</p><div className="goal-progress-label"><strong>{money(visibleSavingsGoals[0].current_balance)}</strong><span>מתוך {money(visibleSavingsGoals[0].target_amount ?? 0)}</span></div><div className="goal-track"><span style={{ width: `${Math.min(100, visibleSavingsGoals[0].current_balance / Math.max(visibleSavingsGoals[0].target_amount ?? 0, 1) * 100)}%` }} /></div><div className="goal-footer"><span>{Math.round(Math.min(100, visibleSavingsGoals[0].current_balance / Math.max(visibleSavingsGoals[0].target_amount ?? 0, 1) * 100))}% מהיעד</span>{visibleSavingsGoals[0].id > 0 && <button onClick={() => { setSelectedGoalId(visibleSavingsGoals[0].id); setGoalDialog('deposit') }}>הפקדה ליעד</button>}</div></> : <p className="goal-description">צרו יעד ראשון כדי לעקוב אחר ההתקדמות.</p>}</div><div className="panel goals-side"><div className="panel-heading"><div><p className="panel-kicker">{connection === 'live' ? 'היעדים שלכם' : 'יעדים לדוגמה'}</p><h2>מתקדמים בקצב שלכם</h2></div><button className="icon-button" aria-label="הוספת יעד" onClick={() => setGoalDialog('create')}><AddRounded /></button></div>{visibleSavingsGoals.length ? visibleSavingsGoals.map((goal, index) => <div className="goal-list-item" key={goal.id}><span className={`goal-list-icon ${index % 2 ? 'travel-goal' : 'home-goal'}`}><SavingsRounded /></span><span><strong>{goal.name}</strong><small>יעד: {money(goal.target_amount ?? 0)}</small></span><b>{goal.target_amount ? `${Math.round(goal.current_balance / goal.target_amount * 100)}%` : money(goal.current_balance)}</b>{goal.id > 0 && <button className="goal-deposit" onClick={() => { setSelectedGoalId(goal.id); setGoalDialog('deposit') }}>הפקדה</button>}</div>) : <p className="empty-note">עדיין לא נוצרו יעדי חיסכון.</p>}</div><div className="panel saving-advice"><span className="insight-icon"><LightbulbRounded /></span><div><p className="panel-kicker">הצעה לשיפור</p><h2>העברה קבועה, שקט גדול.</h2><p>העברה אוטומטית בתחילת החודש עוזרת לחיסכון לקרות לפני שהכסף מתפזר.</p></div></div></section>}
          <footer className="page-footer"><BrandMark /><span>מתקדמים עם החלטות טובות יותר.</span><span className="footer-status"><i />הנתונים שלך נשארים שלך</span></footer>
        </div>
      </main>

      {entryKind && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setEntryKind(null) }}><section className="entry-modal" role="dialog" aria-modal="true" aria-labelledby="entry-title"><div className="modal-head"><div><p className="panel-kicker">רישום תנועה</p><h2 id="entry-title">{entryKind === 'expense' ? 'הוספת הוצאה' : 'הוספת הכנסה'}</h2></div><button className="icon-button" aria-label="סגירה" onClick={() => setEntryKind(null)}><CloseRounded /></button></div><div className="entry-tabs"><button className={entryKind === 'expense' ? 'selected' : ''} onClick={() => setEntryKind('expense')}>הוצאה</button><button className={entryKind === 'income' ? 'selected' : ''} onClick={() => setEntryKind('income')}>הכנסה</button></div><form className="entry-form" onSubmit={(event) => void submitEntry(event)}><label>סכום בשקלים<div className="amount-input"><span>₪</span><input name="amount" type="number" min="1" step="0.01" placeholder="0" required autoFocus /></div></label><label>קטגוריה<select name="category" required defaultValue=""><option value="" disabled>בחירת קטגוריה</option>{entryKind === 'expense' ? data.categories.map((item) => <option key={item.category_id} value={item.category_id}>{item.category_name}</option>) : (incomeCategories.length ? incomeCategories : [{ id: 1, name: 'משכורת' }, { id: 2, name: 'עסק' }, { id: 3, name: 'קצבה' }]).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>{entryKind === 'expense' && <label>סוג הוצאה<select name="expenseType">{expenseTypes.length ? expenseTypes.map((item) => <option key={item.id} value={item.id}>{item.name}</option>) : <option value="1">רגילה</option>}</select></label>}<label>תאריך<input name="date" type="date" defaultValue={todayString()} required /></label><button className="primary-button submit-entry" type="submit">שמירת {entryKind === 'expense' ? 'הוצאה' : 'הכנסה'}<ArrowBackIosNewRounded /></button></form></section></div>}
      {goalDialog && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setGoalDialog(null) }}><section className="entry-modal" role="dialog" aria-modal="true" aria-labelledby="goal-title"><div className="modal-head"><div><p className="panel-kicker">יעדי חיסכון</p><h2 id="goal-title">{goalDialog === 'create' ? 'יעד חדש' : 'הפקדה ליעד'}</h2></div><button className="icon-button" aria-label="סגירה" onClick={() => setGoalDialog(null)}><CloseRounded /></button></div><form className="entry-form goal-form" onSubmit={(event) => void submitGoalAction(event)}>{goalDialog === 'create' ? <><label>שם היעד<input name="name" placeholder="למשל: קרן חירום" required /></label><label>סכום היעד<input name="target" type="number" min="1" step="1" placeholder="30000" required /></label></> : <label>סכום ההפקדה<input name="deposit" type="number" min="1" step="1" placeholder="500" required autoFocus /></label>}<button className="primary-button submit-entry" type="submit">{goalDialog === 'create' ? 'שמירת יעד' : 'ביצוע הפקדה'}<ArrowBackIosNewRounded /></button></form></section></div>}
      {toast && <div className="toast-message" role="status"><CheckCircleRounded />{toast}</div>}
    </div>
  )
}

function TransactionTable({ transactions }: { transactions: Transaction[] }) {
  if (!transactions.length) return <p className="empty-note">עדיין לא נרשמו תנועות.</p>
  return <div className="table-scroll"><table className="transaction-table"><thead><tr><th>תנועה</th><th>תאריך</th><th>קטגוריה</th><th>סכום</th><th>סטטוס</th></tr></thead><tbody>{transactions.map((item) => <tr key={item.id}><td><span className={`transaction-icon ${item.type}`}><ReceiptLongRounded /></span><strong>{item.title}</strong></td><td>{new Intl.DateTimeFormat('he-IL', { day: 'numeric', month: 'short' }).format(new Date(`${item.date}T12:00:00`))}</td><td>{item.type === 'income' ? 'הכנסה' : 'הוצאה שוטפת'}</td><td className={item.type === 'income' ? 'income-amount' : ''}>{item.type === 'income' ? '+' : '−'}{money(item.amount)}</td><td><span className="transaction-status"><i />נרשם</span></td></tr>)}</tbody></table></div>
}

function App() {
  const [user, setUser] = useState<SessionUser | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const [serverMessage, setServerMessage] = useState('')

  useEffect(() => {
    let cancelled = false
    void fetch('/auth/me', { credentials: 'include' })
      .then(async (response) => {
        if (response.status === 401) return null
        if (!response.ok) throw new Error('שרת ההתחברות אינו זמין')
        return response.json() as Promise<SessionUser>
      })
      .then((currentUser) => { if (!cancelled) setUser(currentUser) })
      .catch(() => { if (!cancelled) setServerMessage('לא ניתן להתחבר לשרת כרגע. הפעילו את שרת Flask ונסו שוב.') })
      .finally(() => { if (!cancelled) setCheckingSession(false) })
    return () => { cancelled = true }
  }, [])

  const logout = () => {
    void fetch('/auth/logout', { method: 'POST', credentials: 'include' }).finally(() => setUser(null))
  }

  if (checkingSession) return <div className="auth-loading" dir="rtl"><span className="brand-mark"><i /><i /><i /></span><p>בודקים את החיבור המאובטח...</p></div>
  if (!user) return <AuthScreen onAuthenticated={(authenticatedUser) => { setServerMessage(''); setUser(authenticatedUser) }} serverMessage={serverMessage} />
  if (user.role === 'admin') return <AdminConsole user={user} onLogout={logout} />
  return <DashboardApp key={user.user_id} user={user} onLogout={logout} />
}

export default App
