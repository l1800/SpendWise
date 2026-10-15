import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_connection import SessionLocal
from controller.Finance.budget_plan_controller import _build_service
from sqlalchemy import text

s = SessionLocal()
svc, _, _ = _build_service(s)
s.execute(text('DELETE FROM Budget_Plans WHERE user_id=99'))
s.commit()

with open("debug_output.txt", "w", encoding="utf-8") as f:
    f.write("=== MONTH-BY-MONTH DETAILS ===\n\n")

    for yr, mo in [(2025,7),(2025,8),(2025,9)]:
        plan = svc.build_plan(user_id=99, year=yr, month=mo)
        f.write(f"{yr}-{mo:02d}: mode={plan['mode']} month={plan['program_month']} net={plan['net_budget']:,.0f} planned={plan['planned_spending']:,.0f}\n")
        f.write(f"  Phase 1 reductions (per-category):\n")
        phase1_total = 0
        for b in sorted(plan['budget'], key=lambda x: x['reduction'], reverse=True):
            if b['reduction'] > 0:
                phase1_total += b['reduction']
                f.write(f"    cat {b['category_id']:4d}: current={b['current_amount']:7,.0f} target={b['target_amount']:7,.0f} planned={b['planned_amount']:7,.0f} red={b['reduction']:7,.0f} ({b['reduction_pct']:5.1f}%) fix={b['is_fixed_cost']} ess={b['is_essential']}\n")
        f.write(f"  Phase 1 total reduction: {phase1_total:,.0f}\n")
        f.write(f"  Phase 2 (smart correction): planned went from 17,840 to {plan['planned_spending']:,.0f}\n")
        f.write(f"  Total reduction: {sum(b['reduction'] for b in plan['budget']):,.0f}\n")
        f.write(f"  Warnings: {plan.get('warnings')}\n\n")

s.close()
print("Done")
