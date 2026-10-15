from datetime import datetime


# services/users_service.py
class UsersService:
    def __init__(self, repo):
        self.repo = repo

    def create_user(self, dto):
        from models.core.Users import User
        user = User(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            password_hash=dto.password_hash,
            join_date=dto.join_date if hasattr(dto, 'join_date') else datetime.utcnow()
        )
        self.repo.add(user)
        return user

    def get_all_users(self):
        return self.repo.get_all()

    def get_user_by_id(self, user_id):
        return self.repo.get_by_id(user_id)

    def update_user(self, user_id, dto):
        return self.repo.update(
            user_id,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            password_hash=dto.password_hash
        )

    def delete_user(self, user_id):
        return self.repo.delete_by_id(user_id)

    def register_user(self, first_name, last_name, email, password_hash, join_date):
        # אם המשתמש כבר קיים לפי אימייל, מונעים רישום כפול
        if self.repo.find_by_email(email):
            raise Exception("User already exists")

        # אפשר להוסיף בדיקה על אורך הסיסמה או אימייל תקין
        if len(password_hash) < 8:
            raise Exception("Password too short")

        return self.repo.create(
            first_name, last_name, email, password_hash, join_date
        )

    def get_user_full_name(self, user_id):
        # שילוב בין first_name ו-last_name במקום לתת רק את האובייקט גולמי
        user = self.repo.get_by_id(user_id)
        if user:
            return f"{user.first_name} {user.last_name}"
        return None

