from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBaseDTO(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreateDTO(UserBaseDTO):
    password_hash: str
    family_size: int


class UserResponseDTO(UserBaseDTO):
    user_id: int
    join_date: datetime

    class Config:
        from_attributes = True
class UserUpdateDTO(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password_hash: str | None = None