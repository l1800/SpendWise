class RecommendationTextService:
    """
    שלב 12 — שכבת Decision → Explanation.

    שירות טהור — ללא גישה ל-DB.
    מקבל תוכנית חודשית (פלט שלב 11) ומחזיר טקסטים בעברית.
    """

    # =========================
    # MAIN API
    # =========================
    def generate(self, plan):
        """
        מייצר טקסטים בעברית מתוך תוכנית תקציבית.

        Args:
            plan: dict — פלט BudgetBuilderService.build_next_month_budget()

        Returns:
            dict עם headline, sections[], raw_messages[]
        """

        status = plan.get("status", "OK")
        budget = plan.get("budget", [])
        remaining_balance = plan.get("remaining_balance", 0)
        health_score = plan.get("budget_health_score", 0)
        remaining_deficit = plan.get("remaining_deficit", 0)

        sections = []

        # =========================
        # 1. HEADLINE
        # =========================
        headline = self._build_headline(status, remaining_balance)

        # =========================
        # 2. TOP CUTS
        # =========================
        top_cut_section = self._build_top_cuts(budget)
        if top_cut_section:
            sections.append(top_cut_section)

        # =========================
        # 3. PROTECTED
        # =========================
        protected_section = self._build_protected(budget)
        if protected_section:
            sections.append(protected_section)

        # =========================
        # 4. HEALTH TIP
        # =========================
        sections.append(self._build_health_tip(health_score))

        # =========================
        # 5. DEFICIT WARNING
        # =========================
        if remaining_deficit > 0:
            sections.append(self._build_deficit_warning(remaining_deficit))

        raw_messages = [headline] + [s["body"] for s in sections]

        return {
            "headline": headline,
            "sections": sections,
            "raw_messages": raw_messages,
        }

    # =========================
    # HEADLINE
    # =========================
    def _build_headline(self, status, remaining_balance):

        if status == "OK":
            return (
                f"✅ התקציב שלך מאוזן. "
                f"היתרה הצפויה: ₪{remaining_balance:,.0f}"
            )

        if status == "LIMIT_EXCEEDED":
            return (
                f"⚠️ התקציב חורג מתקרת ההוצאה "
                f"ב-₪{abs(remaining_balance):,.0f}"
            )

        if status == "IMPOSSIBLE_BUDGET":
            return (
                "🚨 לא ניתן לאזן את התקציב — "
                "ההוצאות הבסיסיות עולות על ההכנסה"
            )

        return "📊 סטטוס תקציב לא ידוע"

    # =========================
    # TOP CUTS
    # =========================
    def _build_top_cuts(self, budget):

        reduced = [
            b for b in budget
            if b.get("status") == "reduced" and b.get("cut_amount", 0) > 0
        ]

        if not reduced:
            return None

        top = sorted(reduced, key=lambda x: x.get("cut_amount", 0), reverse=True)[:3]

        parts = [
            f"{item['category_name']} (₪{item['cut_amount']:,.0f})"
            for item in top
        ]

        if not parts:
            return None

        return {
            "icon": "🔻",
            "title": "קטגוריות שקוצצו",
            "body": "הקיצוץ העיקרי: " + ", ".join(parts),
            "severity": "info",
        }

    # =========================
    # PROTECTED
    # =========================
    def _build_protected(self, budget):

        names = [
            b["category_name"]
            for b in budget
            if b.get("status") == "protected"
        ]

        if not names:
            return None

        return {
            "icon": "🔒",
            "title": "קטגוריות מוגנות",
            "body": f"{len(names)} קטגוריות מוגנות: {', '.join(names)}",
            "severity": "info",
        }

    # =========================
    # HEALTH TIP
    # =========================
    def _build_health_tip(self, health_score):

        if health_score >= 0.2:
            body = f"המצב התקציבי יציב (ציון {health_score}). כל הכבוד!"
            severity = "info"

        elif health_score >= 0:
            body = (
                f"ציון הבריאות התקציבית גבולי ({health_score}). "
                f"מומלץ לעקוב אחרי ההוצאות."
            )
            severity = "warning"

        elif health_score >= -0.5:
            body = (
                f"ציון הבריאות התקציבית נמוך ({health_score}). "
                f"כדאי לשקול צמצום הוצאות לא חיוניות."
            )
            severity = "warning"

        else:
            body = (
                f"מצב חירום תקציבי ({health_score}). "
                f"נדרשת התערבות מיידית."
            )
            severity = "critical"

        return {
            "icon": "💡",
            "title": "המלצה",
            "body": body,
            "severity": severity,
        }

    # =========================
    # DEFICIT WARNING
    # =========================
    def _build_deficit_warning(self, remaining_deficit):

        return {
            "icon": "📌",
            "title": "פער שלא נסגר",
            "body": (
                f"לא ניתן היה לסגור את מלוא הפער — "
                f"חסרים ₪{remaining_deficit:,.0f} ליעד החיסכון."
            ),
            "severity": "warning",
        }