from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length = 8)


class OnBoardIn(BaseModel):
    username: str
    follower_count: int
    bio: Optional[constr(max_length = 100)] = None