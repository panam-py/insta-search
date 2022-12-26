from pydantic import BaseModel, EmailStr, constr

class RegisterIn(BaseModel):
    email: EmailStr
    password: constr(min_length = 8)