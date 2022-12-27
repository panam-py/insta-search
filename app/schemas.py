from pydantic import BaseModel, EmailStr, constr

class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length = 8)


class OnBoardIn(BaseModel):
    username: str
    follower_count: int
    bio: constr(max_length = 100)