class AllocationDTO:
    """פריט הקצאה בודד."""
    def __init__(self, goal_id, amount):
        self.goal_id = goal_id
        self.amount = amount


class UpdateAllocationsRequest:
    """בקשה לעדכון הקצאות."""
    def __init__(self, allocations):
        self.allocations = allocations  # [{"goal_id": 1, "amount": 1000}, ...]


class MonthlySavingsResponse:
    """תשובה — מצב חיסכון חודשי."""
    def __init__(self, user_id, year, month, saved_this_month, allocations):
        self.user_id = user_id
        self.year = year
        self.month = month
        self.saved_this_month = saved_this_month
        self.allocations = allocations  # list of UserSavingGoal
