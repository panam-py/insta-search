from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from .schemas import RegisterIn

from .models import User

from .utils import hash_password

from .database import get_db

app = FastAPI()

# CORS Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.post("/register")
async def register(data: RegisterIn, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user collecting email and
    password
    """
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"A user already exists with the email {data.email}")
    new_user = User(email = data.email, password = hash_password(data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

