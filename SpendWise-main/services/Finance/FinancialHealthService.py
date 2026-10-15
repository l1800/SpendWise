class FinancialHealthService:
    # מחזיר סיכום של רמת לחץ

    def __init__(self, spike_service, behavior_service, repo):
        self.spike_service = spike_service
        self.behavior_service = behavior_service
        self.repo = repo

    # =========================
    # שכבה 1: שליפת מדדים
    # =========================
    def get_metrics(self, user_id, year, month):

        spike = self.spike_service.calculate_spike_stress(user_id, year, month)
        behavior = self.behavior_service.calculate_behavior_stress(user_id, year, month)
        budget = self.repo.get_financial_pressure(user_id, year, month)

        return {
            "spike": spike.get("spike_stress", 0),
            "behavior": behavior.get("behavior_stress", 0),
            "budget": budget
        }

    # =========================
    # שכבה 2: חיבור לציון סופי
    # =========================
    def calculate_financial_score(self, user_id, year, month):

        m = self.get_metrics(user_id, year, month)

        score = (
            m["spike"] * 0.20 +
            m["behavior"] * 0.50 +
            m["budget"] * 0.30
        )

        score = max(0, min(100, int(score)))

        if score < 30:
            status = "סיכון נמוך"
        elif score < 60:
            status = "סיכון בינוני"
        elif score < 80:
            status = "סיכון גבוה"
        else:
            status = "סיכון קריטי"

        return {
            "ציון": score,
            "status": status,
            "explanation": self.build_smart_explanation_v2(m)
        }

    # =========================
    # שכבה 3: הסבר אנושי בסיסי
    # =========================
    def build_explanation(self, m):

        explanation = []

        if m["spike"] > 70:
            explanation.append("נמצאו קפיצות חדות בהוצאות בטווח הקצר")
        elif m["spike"] > 40:
            explanation.append("יש תנודות בינוניות בהוצאות החודשיות")
        else:
            explanation.append("הוצאות קצרות טווח יציבות יחסית")

        if m["behavior"] > 70:
            explanation.append("קיימת מגמת עלייה עקבית בהוצאות לאורך זמן")
        elif m["behavior"] > 40:
            explanation.append("יש שינוי מתון בהתנהגות הכלכלית")
        else:
            explanation.append("התנהגות כלכלית יציבה לאורך זמן")

        if m["budget"] > 70:
            explanation.append("קיים עומס פיננסי גבוה ביחס להכנסה")
        elif m["budget"] > 40:
            explanation.append("יש לחץ פיננסי בינוני")
        else:
            explanation.append("מצב פיננסי מאוזן יחסית")

        return explanation

    # =========================
    # שכבה 4: הסבר חכם V1 (משפט אחד)
    # =========================
    def build_smart_explanation(self, m):

        spike = m["spike"]
        behavior = m["behavior"]
        budget = m["budget"]

        dominant = max(
            [("spike", spike), ("behavior", behavior), ("budget", budget)],
            key=lambda x: x[1]
        )[0]

        sentence = "המצב הפיננסי יציב יחסית עם רמת סיכון נמוכה"

        if dominant == "behavior":
            sentence = "הסיכון נובע בעיקר ממגמת שינוי עקבית בהוצאות לאורך זמן"

        elif dominant == "budget":
            sentence = "הסיכון נובע בעיקר מלחץ פיננסי גבוה ביחס להכנסה"

        elif dominant == "spike":
            sentence = "הסיכון נובע בעיקר מקפיצות חדות בהוצאות בטווח הקצר"

        if spike > 70 and behavior > 70:
            sentence += " כאשר גם הטווח הקצר וגם הארוך מצביעים על החמרה"

        if budget > 70:
            sentence += " לצד עומס פיננסי גבוה שמחזק את הסיכון"

        return sentence

    # =========================
    # שכבה 5: הסבר חכם V2 (משופר, משולב)
    # =========================
    # =========================
    # שכבה 4: הסבר חכם V3 (משודרג)
    # =========================
    def build_smart_explanation_v2(self, m):

        spike = m["spike"]
        behavior = m["behavior"]
        budget = m["budget"]

        explanation = []

        # =========================
        # ניתוח מקבילי (לא elif!)
        # =========================

        if spike > 70:
            explanation.append("קפיצות חדות בהוצאות בטווח הקצר")

        if behavior > 70:
            explanation.append("מגמת עלייה עקבית בהוצאות לאורך זמן")

        if budget > 70:
            explanation.append("עומס פיננסי גבוה ביחס להכנסה")

        # =========================
        # שילובי סיכון (חשוב!)
        # =========================

        if spike > 70 and behavior > 70:
            explanation.append("⚠️ שילוב מסוכן: גם קפיצות וגם מגמה ארוכת טווח")

        if behavior > 70 and budget > 70:
            explanation.append("⚠️ לחץ מתמשך + עומס תקציבי")

        if spike > 70 and budget > 70:
            explanation.append("⚠️ תנודתיות יחד עם עומס פיננסי")

        # =========================
        # מצב רגוע
        # =========================

        if not explanation:
            explanation.append("המצב הפיננסי יציב יחסית")

        return ". ".join(explanation)