class CutAllocationService:

    def __init__(self, budget_service, saving_repo, standard_repo):
        self.budget_service = budget_service
        self.saving_repo = saving_repo
        self.standard_repo = standard_repo

    # =========================
    # יעד חיסכון
    # =========================
    def extract_saving_target(self, allocations, net_budget):

        return sum(max(0, allocation.allocated_amount or 0) for allocation in allocations)

    # =========================
    # תקציב סטנדרטי
    # =========================
    def get_standard_pressure(self, user_id, family_size):

        rows = self.standard_repo.get_all()

        return sum(
            r.amount_per_person * family_size
            for r in rows
        )

    # =========================
    # #10 CORE ENGINE
    # =========================
    def calculate_total_cut_needed(
            self,
            ranking,
            net_budget,
            stress_score,
            user_id,
            family_size=1,
            year=None,
            month=None
    ):

        base_budget = net_budget.get("net_budget", 0)

        # =========================
        # 1. גירעון אמיתי (חדש)
        # =========================
        last_deficit = self.budget_service.get_previous_month_deficit(
            user_id,
            year,
            month
        ) or 0
        # =========================
        # 2. גירעון + לחץ
        # =========================
        deficit_part = min(max(last_deficit, 0), base_budget * 0.5)

        stress_multiplier = 0.2 if family_size <= 2 else 0.3
        stress_part = base_budget * (stress_score / 100) * stress_multiplier
        # =========================
        # 3. יעד חיסכון
        # =========================
        allocations = self.saving_repo.get_for_month(user_id, year, month)
        saving_part = self.extract_saving_target(allocations, net_budget)

        # =========================
        # 4. סטנדרט חיים
        # =========================
        standard_budget = self.get_standard_pressure(user_id, family_size)
        standard_pressure = max(0, standard_budget - base_budget) * 0.2

        # =========================
        # 5. חישוב כולל
        # =========================
        total_cut_needed = (
                deficit_part +
                stress_part +
                saving_part +
                standard_pressure
        )

        # =========================
        # 6. מניעת מצב לא ריאלי
        # =========================
        total_possible_cut = sum(
            item["current_amount"] * (item.get("max_pct", 100) / 100)
            for item in ranking
        )

        total_cut_needed = min(total_cut_needed, total_possible_cut)

        return round(max(total_cut_needed, 0), 2)
    # =========================
    # #10 - חלוקה בפועל (מתוקן לגמרי)
    # =========================
    def allocate_cuts(self, ranking, total_cut):

        working = []

        base_total = 0

        for r in ranking:
            effective_pct = min(r["recommended_cut_pct"], r.get("max_pct", 100))
            base_cut = r["current_amount"] * (effective_pct / 100)

            working.append({
                "category_id": r["category_id"],
                "category_name": r["category_name"],
                "current_amount": r["current_amount"],
                "effective_pct": effective_pct,
                "base_cut": base_cut,
                "cut_amount": 0
            })

            base_total += base_cut

        if base_total == 0:
            return {
                "total_cut_needed": total_cut,
                "actual_cut": 0,
                "remaining_to_cut": total_cut,
                "allocation": []
            }

        max_possible_cut = sum(
            r["current_amount"] * (r.get("max_pct", 100) / 100)
            for r in ranking
        )

        if total_cut > max_possible_cut:
            total_cut = max_possible_cut

        scale = total_cut / base_total

        actual_cut = 0

        for item in working:
            max_cut = item["current_amount"] * (item["effective_pct"] / 100)
            cut = min(item["base_cut"] * scale, max_cut)
            cut = round(cut, 2)

            item["cut_amount"] = cut
            actual_cut += cut

        remaining = round(total_cut - actual_cut, 2)

        if remaining > 0:
            capacity_list = []

            for item in working:
                max_cut = item["current_amount"] * (item["effective_pct"] / 100)
                available = max(0, max_cut - item["cut_amount"])
                if available > 0:
                    capacity_list.append(item)

            if remaining > 0:

                while remaining > 0:

                    capacity_list = []

                    for item in working:
                        max_cut = item["current_amount"] * (item["effective_pct"] / 100)
                        available = max_cut - item["cut_amount"]

                        if available > 0:
                            capacity_list.append((item, available))

                    if not capacity_list:
                        break

                    total_capacity = sum(av for _, av in capacity_list)

                    if total_capacity == 0:
                        break

                    for item, available in capacity_list:

                        add = remaining * (available / total_capacity)

                        # בלי round כאן!
                        add = min(add, available)

                        item["cut_amount"] += add
                        remaining -= add

                        if remaining <= 0:
                            break
        final_cut = round(sum(i["cut_amount"] for i in working), 2)

        difference = round(total_cut - final_cut, 2)

        if difference > 0:
            for item in working:
                if difference <= 0:
                    break

                max_cut = item["current_amount"] * (item["effective_pct"] / 100)
                available = round(max_cut - item["cut_amount"], 2)

                if available <= 0:
                    continue

                add = min(available, difference)
                item["cut_amount"] = round(item["cut_amount"] + add, 2)
                difference = round(difference - add, 2)

        elif difference < 0:
            for item in reversed(working):
                if difference >= 0:
                    break

                if item["cut_amount"] <= 0:
                    continue

                reduce = min(item["cut_amount"], abs(difference))
                item["cut_amount"] = round(item["cut_amount"] - reduce, 2)
                difference = round(difference + reduce, 2)

        final_cut = round(sum(i["cut_amount"] for i in working), 2)

        return {
            "total_cut_needed": round(total_cut, 2),
            "actual_cut": final_cut,
            "remaining_to_cut": round(max(0, total_cut - final_cut), 2),
            "allocation": working
        }


















































































































































