import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_connection import SessionLocal
from controller.Finance.budget_plan_controller import _build_service
from services.Finance.EarlyWarningService import EarlyWarningService
from repositories.system.EarlyWarningAlert import EarlyWarningAlertRepository
from sqlalchemy import text

s = SessionLocal()
svc, plan_repo, ew = _build_service(s)
alert_repo = EarlyWarningAlertRepository(s)
ew_service = EarlyWarningService(s, alert_repo)

# Make sure user 99 has a budget plan for July 2025
svc.build_plan(user_id=99, year=2025, month=7)

print("=== SMART ALERTS TEST ===\n")

# Test 1: Normal expense
print("Test 1: Normal expense (100 NIS, cat 1027)")
r1 = ew_service.check_before_expense(99, 2025, 7, 100, 1027, "Food")
print(f"  has_warnings={r1['has_warnings']}")
for w in r1['warnings']:
    print(f"  [{w['type']}] cat={w.get('category_id')} msg_len={len(w['message'])}")
    if 'planned' in w:
        print(f"    planned={w['planned']:,.0f} spent={w['spent_so_far']:,.0f} after_expense={w['after_expense']:,.0f}")

print()

# Test 2: Huge expense
print("Test 2: Huge expense (5000 NIS, cat 1027)")
r2 = ew_service.check_before_expense(99, 2025, 7, 5000, 1027, "Food")
print(f"  has_warnings={r2['has_warnings']} over_cat={r2['is_over_category']} over_total={r2['is_over_total']} spike={r2['is_spike']}")
for w in r2['warnings']:
    print(f"  [{w['type']}] cat={w.get('category_id')}")
    if 'planned' in w:
        print(f"    planned={w['planned']:,.0f} spent={w['spent_so_far']:,.0f} after={w.get('after_expense',0):,.0f} overshoot={w.get('overshoot',0):,.0f}")
    if 'ratio' in w:
        print(f"    amount={w['amount']:,.0f} avg={w['avg_history']:,.0f} ratio={w['ratio']}x")

print()

# Test 3: Approaching limit
print("Test 3: Approaching limit")
from models.Finance.Expenses import Expense
from datetime import date
s.add(Expense(user_id=99, category_id=1027, amount=1500, date=date(2025,7,10), expense_type_id=2, is_one_time=False, covered_by_savings=False))
s.commit()
r3 = ew_service.check_before_expense(99, 2025, 7, 400, 1027, "Food")
print(f"  has_warnings={r3['has_warnings']} spent_before={r3['spent_so_far_in_category']:,.0f}")
for w in r3['warnings']:
    print(f"  [{w['type']}]")
    if 'after_expense' in w:
        print(f"    after_expense={w['after_expense']:,.0f} planned={w.get('planned',0):,.0f} remaining={w.get('remaining',0):,.0f}")

print()
print("=== PASSED ===")
s.close()
