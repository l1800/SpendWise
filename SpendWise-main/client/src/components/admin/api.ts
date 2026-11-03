export type Period = { year: number; month: number }

export type Overview = {
  period: Period
  households_total: number
  households_active: number
  households_over_budget: number
  open_alerts: number
  active_savings_goals: number
  total_income: number
  total_expense: number
  savings_rate: number
  avg_income: number
  avg_expense: number
  median_expense: number
  total_overage: number
  avg_health_score: number
  risk_households: number
}

export type CategoryAverage = {
  category_id: number
  category_name: string
  is_essential: boolean
  total_spent: number
  avg_per_household: number
  median_per_household: number
  avg_per_person: number
  max_per_household: number
  target_total: number
  avg_target_per_household: number
  variance_percent: number
  households_spending: number
  households_over_target: number
}

export type Averages = { period: Period; categories: CategoryAverage[] }

export type TrendPoint = {
  year: number
  month: number
  income: number
  expense: number
  balance: number
  savings_rate: number
  active_households: number
}

export type Trends = { months: TrendPoint[] }

export type HealthBand = 'excellent' | 'good' | 'watch' | 'risk'

export type HealthRow = {
  user_id: number
  name: string
  email: string
  family_size: number
  income: number
  expense: number
  balance: number
  expense_ratio: number
  health_score: number
  band: HealthBand
  overage_total: number
  overage_categories: number
  open_alerts: number
}

export type Health = { period: Period; bands: Record<HealthBand, number>; households: HealthRow[] }

export async function fetchAdmin<T>(path: string, period: Period, extra = ''): Promise<T> {
  const query = new URLSearchParams({ year: String(period.year), month: String(period.month) })
  const response = await fetch(`${path}?${query}${extra}`, { credentials: 'include' })
  const result = await response.json()
  if (!response.ok) throw new Error(result.error ?? 'טעינת הנתונים נכשלה')
  return result as T
}

export const money = (amount: number) =>
  new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS', maximumFractionDigits: 0 }).format(amount || 0)

export const percent = (value: number) => `${value > 0 ? '+' : ''}${value.toFixed(1)}%`

export const bandLabel: Record<HealthBand, string> = {
  excellent: 'מצוין',
  good: 'טוב',
  watch: 'למעקב',
  risk: 'בסיכון',
}
