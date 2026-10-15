class CategoryBehaviorService:

    def calculate_category_behavior(self, monthly, long_term, essential):

        # =========================
        # שלב 1: שינוי חודשי (מאוזן + תגמול ירידה)
        # =========================
        abs_monthly = abs(monthly)

        if abs_monthly <= 5:
            base = 10
        elif abs_monthly <= 15:
            base = 22
        elif abs_monthly <= 30:
            base = 40
        else:
            base = 55

        # =========================
        # שלב 2: מגמה ארוכת טווח (חשוב יותר עכשיו)
        # =========================
        if long_term > 25:
            trend = 30
        elif long_term > 10:
            trend = 15
        elif long_term < -10:
            trend = -20   # 🔥 תגמול אמיתי על שיפור
        else:
            trend = 5

        score = base + trend

        # =========================
        # שלב 3: חיוניות (עדין ומאוזן)
        # =========================
        if essential:
            score *= 0.85   # חיוני = פחות פאניקה
        else:
            score *= 1.1    # לא חיוני = יותר רגישות

        # =========================
        # שלב 4: בלימת קיצון (Soft Clamp)
        # =========================
        # במקום קפיצה חדה ל-100 → עקומה חלקה
        score = 100 * (score / (score + 60))

        # =========================
        # שלב 5: נרמול סופי
        # =========================
        if score < 0:
            score = 0

        if score > 100:
            score = 100

        return round(score, 2)