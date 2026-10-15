import { useState, type FormEvent } from 'react'
import ArrowBackIosNewRounded from '@mui/icons-material/ArrowBackIosNewRounded'
import LockOutlined from '@mui/icons-material/LockOutlined'
import SavingsRounded from '@mui/icons-material/SavingsRounded'

export type SessionUser = {
  user_id: number
  first_name: string
  last_name: string
  email: string
  family_size: number
  role: 'household' | 'admin'
  join_date: string | null
}

type AuthScreenProps = {
  onAuthenticated: (user: SessionUser) => void
  serverMessage?: string
}

export default function AuthScreen({ onAuthenticated, serverMessage }: AuthScreenProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setBusy(true)
    const form = new FormData(event.currentTarget)
    const payload = mode === 'login'
      ? { email: form.get('email'), password: form.get('password') }
      : {
          first_name: form.get('first_name'),
          last_name: form.get('last_name'),
          email: form.get('email'),
          password: form.get('password'),
          family_size: Number(form.get('family_size')),
        }
    try {
      const response = await fetch(`/auth/${mode === 'login' ? 'login' : 'register'}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const result = await response.json()
      if (!response.ok) throw new Error(result.error ?? 'לא הצלחנו להתחבר')
      onAuthenticated(result as SessionUser)
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'לא הצלחנו להתחבר לשרת')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-screen" dir="rtl">
      <header className="auth-brand"><span className="brand-mark"><i /><i /><i /></span><strong>שקלול<span>.</span></strong></header>
      <section className="auth-layout">
        <div className="auth-story">
          <span className="auth-orbit auth-orbit-one" />
          <span className="auth-orbit auth-orbit-two" />
          <div className="auth-story-content">
            <span className="auth-kicker"><SavingsRounded />ניהול כלכלת הבית</span>
            <h1>החלטות קטנות.<br />עתיד רגוע יותר.</h1>
            <p>תמונה ברורה של התקציב, ההוצאות והיעדים של משק הבית, במקום אחד.</p>
            <div className="auth-story-mark"><span>₪</span><i /><i /><i /><i /><i /></div>
          </div>
        </div>
        <div className="auth-panel">
          <div className="auth-panel-heading">
            <span className="auth-lock"><LockOutlined /></span>
            <p className="panel-kicker">המרחב הפיננסי שלכם</p>
            <h2>{mode === 'login' ? 'טוב שחזרתם.' : 'פותחים חשבון ביתי.'}</h2>
            <p>{mode === 'login' ? 'התחברו כדי לראות את תמונת המצב שלכם.' : 'כל משק בית מקבל מרחב נתונים פרטי משלו.'}</p>
          </div>
          <div className="auth-tabs" role="tablist" aria-label="כניסה או הרשמה">
            <button type="button" role="tab" aria-selected={mode === 'login'} className={mode === 'login' ? 'selected' : ''} onClick={() => { setMode('login'); setError('') }}>כניסה</button>
            <button type="button" role="tab" aria-selected={mode === 'register'} className={mode === 'register' ? 'selected' : ''} onClick={() => { setMode('register'); setError('') }}>פתיחת חשבון</button>
          </div>
          <form className="auth-form" onSubmit={(event) => void submit(event)}>
            {mode === 'register' && <div className="auth-name-row"><label>שם פרטי<input name="first_name" autoComplete="given-name" required /></label><label>שם משפחה<input name="last_name" autoComplete="family-name" required /></label></div>}
            <label>כתובת אימייל<input name="email" type="email" autoComplete="email" placeholder="name@example.com" required /></label>
            <label>סיסמה<input name="password" type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} minLength={mode === 'login' ? 1 : 10} required />{mode === 'register' && <small>לפחות 10 תווים</small>}</label>
            {mode === 'register' && <label>מספר בני הבית<input name="family_size" type="number" min="1" max="20" defaultValue="4" required /></label>}
            {(error || serverMessage) && <div className="auth-error" role="alert">{error || serverMessage}</div>}
            <button className="primary-button auth-submit" type="submit" disabled={busy}>{busy ? 'רגע...' : mode === 'login' ? 'כניסה לחשבון' : 'יצירת חשבון'}<ArrowBackIosNewRounded /></button>
          </form>
          <p className="auth-privacy">הנתונים האישיים והפיננסיים נגישים רק לחשבון שלכם.</p>
        </div>
      </section>
      <footer className="auth-footer"><span>שקלול · כלכלת בית חכמה</span><span>חיבור מאובטח</span></footer>
    </main>
  )
}