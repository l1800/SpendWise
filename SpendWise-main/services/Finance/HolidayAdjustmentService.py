"""
Service for adjusting a monthly budget plan based on holiday periods.
Queries Special_Dates and Holiday_Category_Summary to find active
holiday periods in a given month and applies change_ratio adjustments
to matching categories.
"""
from datetime import date, timedelta
from models.system.SpecialDate import SpecialDate
from models.system.HolidayCategorySummary import HolidayCategorySummary


class HolidayAdjustmentService:
    """
    Pure lookup service — no side effects.
    Given a year and month, returns adjustments per category
    based on active holiday periods.
    """

    def __init__(self, session):
        self.session = session

    # ── public API ──

    def get_holiday_adjustments(self, year: int, month: int) -> dict:
        """
        Returns {category_id: (change_ratio, holiday_name)} for all categories
        that have a holiday adjustment in the given month.
        If multiple holidays affect the same category, picks the highest ratio.
        """
        periods = self._find_active_periods(year, month)
        if not periods:
            return {}

        adjustments = {}
        for period in periods:
            rows = self._get_summaries_for_period(period.type_id)
            for row in rows:
                cid = row.category_id
                ratio = float(row.change_ratio)
                name = period.holiday_name
                if cid not in adjustments or ratio > adjustments[cid][0]:
                    adjustments[cid] = (ratio, name)

        return adjustments

    def adjust_budget_items(self, budget_items: list, year: int, month: int) -> list:
        """
        Takes budget items (list of dicts with category_id and planned_amount)
        and applies holiday adjustments. Returns the modified list.
        Each adjusted item gets a 'holiday_adjustment' amount and 'holiday_name'.
        Categories not in any holiday — untouched (adjustment=0, name=None).
        """
        adjustments = self.get_holiday_adjustments(year, month)

        for item in budget_items:
            cid = item.get("category_id")
            entry = adjustments.get(cid)

            if entry:
                ratio, holiday_name = entry
                base = item.get("planned_amount", 0)
                extra = round(base * ratio, 2)
                item["planned_amount"] = round(base + extra, 2)
                item["holiday_adjustment"] = extra
                item["holiday_name"] = holiday_name
            else:
                item["holiday_adjustment"] = 0
                item["holiday_name"] = None

        return budget_items

    # ── helpers ──

    def _find_active_periods(self, year: int, month: int) -> list:
        """
        Returns SpecialDate rows whose date range overlaps
        any part of the given month.
        """
        month_start = date(year, month, 1)
        # last day of month
        if month == 12:
            month_end = date(year, 12, 31)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)

        return (
            self.session.query(SpecialDate)
            .filter(
                SpecialDate.start_date <= month_end,
                SpecialDate.end_date >= month_start,
            )
            .all()
        )

    def _get_summaries_for_period(self, period_type_id: int) -> list:
        """Returns HolidayCategorySummary rows for a given special_period_id."""
        return (
            self.session.query(HolidayCategorySummary)
            .filter(
                HolidayCategorySummary.special_period_id == period_type_id
            )
            .all()
        )
