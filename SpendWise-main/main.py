from datetime import date

import models.import_all

from db_connection import SessionLocal, engine
from models.base import Base

import os
from datetime import timedelta

from flask import Flask
from flask import request


# טעינת מודלים ויצירת טבלאות
Base.metadata.create_all(bind=engine)


# ==========================================
# Flask app
# ==========================================

from controller.core.categories_controller import categories_blueprint
from controller.core.users_controller import users_blueprint
from controller.core.CategoryStandard import category_standard_bp
from controller.core.UserCategoryGoal import user_goal_blueprint
from controller.core.UserCategoryPreference import user_preferences_blueprint
from controller.core.SavingsGoal import savings_blueprint
from controller.core.auth_controller import auth_blueprint, register_auth_middleware

from controller.Finance.Expenses import expenses_blueprint
from controller.Finance.ExpenseTypes import expense_types_blueprint
from controller.Finance.FinancialForecasts import financial_forecasts_blueprint
from controller.Finance.ForecastRanges import forecast_ranges_blueprint
from controller.Finance.IncomeFrequency import income_frequency_blueprint
from controller.Finance.Incomes import income_blueprint
from controller.Finance.IncomeCategories import income_categories_blueprint
from controller.Finance.budget_controller import budget_controller
from controller.Finance.budget_plan_controller import budget_plan_controller
from controller.Finance.financial_controller import financial_controller


from controller.Goals.GoalDetails import goal_details_blueprint
from controller.Goals.Goals import goals_bp

from controller.lookups.CategoryTypes import category_types_bp

from controller.reporting.Reports import reports_bp
from controller.reporting.ReportTypes import report_types_bp

from controller.survey.SatisfactionSurvey import satisfaction_survey_blueprint
from controller.survey.SurveyAnswers import survey_answers_blueprint

from controller.system.HolidayCategorySummary import holiday_summary_blueprint
from controller.system.SpecialPeriodSummary import special_period_summary_blueprint
from controller.system.SpecialDates import special_dates_blueprint
from controller.system.MonthlyExpensesSummary import monthly_expenses_summary_blueprint
from controller.Finance.EarlyWarning import early_warning_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SPENDWISE_SESSION_SECRET") or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("SPENDWISE_COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)

app.register_blueprint(categories_blueprint)
app.register_blueprint(users_blueprint)

app.register_blueprint(expenses_blueprint)
app.register_blueprint(expense_types_blueprint)

app.register_blueprint(financial_forecasts_blueprint)
app.register_blueprint(forecast_ranges_blueprint)

app.register_blueprint(income_frequency_blueprint)
app.register_blueprint(income_blueprint)
app.register_blueprint(income_categories_blueprint)

app.register_blueprint(goal_details_blueprint)
app.register_blueprint(goals_bp)

app.register_blueprint(category_types_bp)

app.register_blueprint(reports_bp)
app.register_blueprint(report_types_bp)

app.register_blueprint(satisfaction_survey_blueprint)
app.register_blueprint(survey_answers_blueprint)

app.register_blueprint(holiday_summary_blueprint)
app.register_blueprint(special_period_summary_blueprint)
app.register_blueprint(special_dates_blueprint)
app.register_blueprint(monthly_expenses_summary_blueprint)

app.register_blueprint(category_standard_bp)
app.register_blueprint(user_goal_blueprint)

app.register_blueprint(budget_controller)
app.register_blueprint(user_preferences_blueprint)
app.register_blueprint(savings_blueprint)
app.register_blueprint(auth_blueprint)

app.register_blueprint(budget_plan_controller)
app.register_blueprint(financial_controller)
app.register_blueprint(early_warning_bp)
register_auth_middleware(app)

print(app.url_map)

@app.route('/')
def home():
    return "Server is running!"


# ==========================================
# Run Server
# ==========================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True

    )