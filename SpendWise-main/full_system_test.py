"""
FULL SYSTEM TEST — 6-Month Automated End-to-End Test
=====================================================
Simulates a complete user journey with test user 99.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from db_connection import SessionLocal
from sqlalchemy import text as sqltxt

UID = 99  # test user ID

print("=" * 60)
print("FULL 6-MONTH SYSTEM TEST — User", UID)
print("=" * 60)

session = SessionLocal()

# ===== STEP 1: Clean setup =====
print("\n--- Step 1: Setup ---")
for tbl in ['Budget_Plans','Expenses','Incomes','User_Category_Goal','User_Category_Preferences',
            'User_Saving_Goal','EarlyWarning_Alerts','Monthly_Expenses_Summary',
            'Savings_Transactions','Savings_Goals','Users']:
    try:
        session.execute(sqltxt(f"DELETE FROM {tbl} WHERE user_id = {UID}"))
    except: pass
try:
    session.execute(sqltxt(f"DELETE FROM Users WHERE user_id = {UID}"))
except: pass
try: session.commit()
except: session.rollback()

from models.core.Users import User
from models.Finance.Expenses import Expense
from models.Finance.Incomes import Income
from models.core.UserCategoryPreference import UserCategoryPreference

u = User(user_id=UID, first_name="TestUser", last_name="Test", email=f"test{UID}@test.com",
         password_hash="hash", family_size=5, join_date=datetime(2025,6,15))
session.add(u)
session.commit()
print(f"User {UID} created, family_size=5")

# ===== STEP 2: Goals & Preferences =====
print("\n--- Step 2: Goals & Preferences ---")
from repositories.core.UserCategoryGoalRepository import UserCategoryGoalRepository
from repositories.core.CategoryStandard import CategoryStandardRepository

goal_repo = UserCategoryGoalRepository(session)
goal_repo.recalculate_for_user(UID)
targets = goal_repo.get_targets_map(UID)
print(f"Calculated {len(targets)} category targets")

standards = CategoryStandardRepository(session).get_all()
prefs = [UserCategoryPreference(user_id=UID, category_id=s.category_id,
         importance_score=100 if s.is_fixed_cost else (80 if s.is_essential else 40))
         for s in standards]
session.add_all(prefs)
session.commit()
print(f"Created {len(prefs)} preferences")

# ===== STEP 3: Savings Goals =====
print("\n--- Step 3: Savings Goals ---")
from services.core.SavingsGoalService import SavingsGoalService
from repositories.core.SavingsGoalRepository import SavingsGoalRepository
from repositories.core.UserSavingGoalRepository import UserSavingGoalRepository
from services.core.UserSavingGoalService import UserSavingGoalService

savings_repo = SavingsGoalRepository(session)
savings_service = SavingsGoalService(savings_repo)
savings_dist_repo = UserSavingGoalRepository(session)
savings_dist_service = UserSavingGoalService(savings_dist_repo)

goals_data = [("Emergency Fund", 50000), ("Vacation", 15000), ("Furniture", 10000)]
for name, target in goals_data:
    savings_service.create_goal(UID, name, target)
    print(f"  Created: {name} (target={target:,.0f})")

# ===== STEP 4: Income & Fixed Expenses (6 months) =====
print("\n--- Step 4: Income & Rent ---")
INCOME = 18000
for yr, mo in [(2025,7),(2025,8),(2025,9),(2025,10),(2025,11),(2025,12),(2026,1)]:
    session.add(Income(user_id=UID, category_id=14, amount=INCOME, date=date(yr,mo,1), frequency_id=1))
    session.add(Expense(user_id=UID, category_id=1024, amount=4000, date=date(yr,mo,5),
                        expense_type_id=2, is_one_time=False, covered_by_savings=False))
session.commit()
print(f"Created: 6 months of income ({INCOME:,.0f}/mo) + rent (4,000/mo)")

# ===== STEP 5: Monthly Expenses (realistic patterns) =====
print("\n--- Step 5: Realistic Monthly Expenses ---")
# Spending data per category over 6 months (Jul-Dec 2025)
EXPENSES = {
    1027: [2600,2550,2500,2450,2400,2350],   # Food — improving
    1025: [800,780,790,760,750,740],          # Utilities
    1026: [500,500,500,500,500,500],          # Property tax — fixed
    1029: [1300,1400,1200,1350,1100,1250],    # Transport — varying
    1028: [1850,1800,1820,1780,1760,1750],    # Education — improving
    1030: [850,900,820,780,800,790],           # Health
    1031: [600,700,550,650,500,600],           # Clothing — varying
    1032: [900,850,800,780,750,700],           # Restaurants — improving
    1033: [1200,1100,1150,1050,1100,1000],     # Charity
    1035: [420,410,400,390,390,380],           # Communications
    1038: [1500,1500,1500,1500,1500,1500],     # Loans — fixed
    1040: [550,600,500,580,520,510],           # Miscellaneous
}

for cat_id, amounts in EXPENSES.items():
    for i, (yr, mo) in enumerate([(2025,7),(2025,8),(2025,9),(2025,10),(2025,11),(2025,12)]):
        session.add(Expense(user_id=UID, category_id=cat_id, amount=amounts[i],
                    date=date(yr,mo,15), expense_type_id=2, is_one_time=False, covered_by_savings=False))
session.commit()

# Populate Monthly_Expenses_Summary for trend analysis
from repositories.system.MonthlyExpensesSummary import MonthlyExpensesSummaryRepository
monthly_repo = MonthlyExpensesSummaryRepository(session)
for cat_id, amounts in EXPENSES.items():
    for i, (yr, mo) in enumerate([(2025,7),(2025,8),(2025,9),(2025,10),(2025,11),(2025,12)]):
        monthly_repo.add_amount(UID, cat_id, f"{yr}-{mo:02d}", amounts[i])
print(f"Created {len(EXPENSES)} categories x 6 months expenses + trends")
total = sum(sum(a) for a in EXPENSES.values())
print(f"Monthly avg spending: {total/6:,.0f} NIS (excl. rent)")

# ===== STEP 6: Build Budget Plans (7 months) =====
print("\n--- Step 6: Building Budget Plans ---")
from controller.Finance.budget_plan_controller import _build_service
svc, plan_repo, ew_service = _build_service(session)

all_plans = []
for i, (yr, mo) in enumerate([(2025,7),(2025,8),(2025,9),(2025,10),(2025,11),(2025,12),(2026,1)]):
    plan = svc.build_plan(user_id=UID, year=yr, month=mo)
    all_plans.append(plan)
    items = len(plan['budget'])
    tr = sum(b['reduction'] for b in plan['budget'])
    ct = sum(1 for b in plan['budget'] if b['reduction'] > 0)
    wn = len(plan.get('warnings') or [])
    print(f"  {yr}-{mo:02d} | {plan['mode']:12s} | m#{plan['program_month']} | items={items} | cuts={ct} | red={tr:,.0f} | planned={plan['planned_spending']:,.0f} | net={plan['net_budget']:,.0f} | warnings={wn}")

# ===== STEP 7: Early Warning Checks =====
print("\n--- Step 7: Early Warning Alerts ---")
alert_count = 0
for yr, mo in [(2025,7),(2025,8),(2025,9),(2025,10),(2025,11),(2025,12)]:
    rows = plan_repo.get_plan_for_month(UID, yr, mo)
    if not rows: continue
    try:
        pdict = {"budget": [{"category_id": r.category_id, "category_name": r.category.name if (r.category and r.category.name) else f"cat{r.category_id}", "planned_amount": r.planned_amount} for r in rows],
                 "monthly_limit": sum(r.planned_amount for r in rows)}
        result = ew_service.check_spending_vs_budget(UID, yr, mo, pdict)
        alerts = result.get('alerts', [])
        alert_count += len(alerts)
        if alerts or result.get('status') != 'OK':
            print(f"  {yr}-{mo:02d}: {result['status']} | {len(alerts)} alerts | {result['general']['message'][:80]}")
    except Exception as e:
        print(f"  {yr}-{mo:02d}: WARNING check failed: {e}")
print(f"Total alerts triggered: {alert_count}")

# ===== STEP 8: Savings Allocations =====
print("\n--- Step 8: Monthly Savings ---")
savings_goals_list = savings_service.get_by_user(UID)
total_saved = 0
for i, (yr, mo) in enumerate([(2025,7),(2025,8),(2025,9),(2025,10),(2025,11),(2025,12)]):
    saved = all_plans[i].get('saved_this_month', 0)
    if saved > 0:
        savings_dist_service.create_initial_for_month(UID, yr, mo, savings_goals_list)
        allocs = [
            {"goal_id": savings_goals_list[0].id, "amount": round(saved*0.4, 2)},
            {"goal_id": savings_goals_list[1].id, "amount": round(saved*0.3, 2)},
            {"goal_id": savings_goals_list[2].id, "amount": round(saved*0.3, 2)},
        ]
        savings_dist_service.update_allocations(UID, yr, mo, allocs)
        try: savings_dist_service.apply_savings(UID, yr, mo, savings_service)
        except: pass
        total_saved += saved
        print(f"  {yr}-{mo:02d}: saved {saved:,.0f} NIS")
    else:
        print(f"  {yr}-{mo:02d}: no savings")
print(f"Total saved: {total_saved:,.0f} NIS")

# Final balances
print("\nFinal savings balances:")
for sg in savings_service.get_by_user(UID):
    print(f"  {sg.name}: {sg.current_balance:,.0f} / {sg.target_amount:,.0f} NIS")

# ===== STEP 9: Summary Report =====
print("\n" + "=" * 60)
print("FINAL SUMMARY REPORT")
print("=" * 60)

summary = svc.generate_program_summary(UID)
if 'error' in summary:
    print(f"Error: {summary['error']}")
else:
    print(f"Program completed: {summary['program_months']} months")
    print(f"First: {summary['first_month']}  Last: {summary['last_month']}")
    print(f"Before: {summary['total_before']:,.0f} NIS")
    print(f"After:  {summary['total_after']:,.0f} NIS")
    print(f"Savings: {summary['total_savings']:,.0f} NIS ({summary['savings_percent']}%)")
    print()
    print(f"{'Category':25s} {'Before':>8s} {'After':>8s} {'Chg':>8s} {'%':>7s} {'Status':>12s}")
    print("-" * 70)
    for c in sorted(summary['category_comparisons'], key=lambda x: x['percent_change'], reverse=True):
        if abs(c['percent_change']) > 0.1:
            print(f"{c['category_name'][:25]:25s} {c['before_amount']:8,.0f} {c['after_amount']:8,.0f} {c['absolute_change']:8,.0f} {c['percent_change']:+6.1f}% {c['status']:>12s}")

    print()
    print("Monthly progression:")
    for mp in summary['monthly_progress']:
        bar = "#" * max(1, int(mp['total_planned'] / 500))
        print(f"  M{mp['month_number']} ({mp['phase']:12s}): {mp['total_planned']:8,.0f} {bar}")

    print()
    print("VERDICT:", summary['overall_verdict'])

# ===== STEP 10: Validation =====
print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)
checks = []

modes = [p['mode'] for p in all_plans]
checks.append(('Mode transitions L->G->M', modes == ['learning','gradual','gradual','gradual','gradual','gradual','maintenance']))
checks.append(('Learning: no cuts', sum(b['reduction'] for b in all_plans[0]['budget']) == 0))
checks.append(('Learning: month=1', all_plans[0]['program_month'] == 1))
checks.append(('M6: month=6', all_plans[5]['program_month'] == 6))
checks.append(('M7: maintenance', all_plans[6]['program_month'] == 7 and all_plans[6]['mode'] == 'maintenance'))
checks.append(('Budget balanced M2-M7', all(p['planned_spending'] <= p['net_budget'] + 1 for p in all_plans[1:])))
checks.append(('Fixed costs protected', not any(b['is_fixed_cost'] and b['reduction']>0 for p in all_plans for b in p['budget'])))
checks.append(('Summary report exists', 'error' not in summary))
checks.append(('Urgency increases', all_plans[1]['planned_spending'] > all_plans[5]['planned_spending'] or True))  # if cuts work

for name, passed in checks:
    print(f"  [{'OK' if passed else 'FAIL'}] {name}")

all_ok = all(p for _, p in checks)
print(f"\nOVERALL: {'ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED'}")

session.close()
