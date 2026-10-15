import sqlalchemy as sa

engine = sa.create_engine(
    'mssql+pyodbc://@D403-013/smart_Encomy'
    '?driver=ODBC+Driver+17+for+SQL+Server'
    '&trusted_connection=yes'
)

with engine.connect() as conn:
    conn.execute(sa.text("DELETE FROM EarlyWarning_Alerts"))
    conn.commit()

    conn.execute(sa.text("""
        INSERT INTO EarlyWarning_Alerts
            (user_id, category_id, year, month, alert_type, severity, title, message, budget_amount, spent_so_far, status, created_at)
        VALUES
            (1, 2, 2026, 7, 'OVERSPENT', 'HIGH', N'Food', N'Over budget!', 3000, 3500, 'ACTIVE', GETDATE()),
            (1, 3, 2026, 7, 'DANGEROUS_TREND', 'MEDIUM', N'Transport', N'High rate', 2000, 1200, 'ACTIVE', GETDATE()),
            (1, NULL, 2026, 7, 'DANGEROUS_TREND', 'MEDIUM', N'General', N'Spending too fast', 15000, 8250, 'ACTIVE', GETDATE()),
            (2, 4, 2026, 7, 'OVERSPENT', 'HIGH', N'Housing', N'Over budget housing!', 4000, 5000, 'ACTIVE', GETDATE()),
            (2, NULL, 2026, 6, 'OVERSPENT', 'HIGH', N'General', N'Month over', 10000, 12000, 'RESOLVED', GETDATE())
    """))
    conn.commit()

    rows = conn.execute(sa.text(
        "SELECT alert_id, user_id, category_id, alert_type, severity, status FROM EarlyWarning_Alerts"
    )).fetchall()

    print("=== INSERTED ===")
    for r in rows:
        print(f"id={r[0]}, user={r[1]}, cat={r[2]}, type={r[3]}, sev={r[4]}, status={r[5]}")

    print(f"\nTotal: {len(rows)} rows")
