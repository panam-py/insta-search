from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from .schemas import RegisterIn

from .models import Influencer

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
    new_influencer = Influencer(email = data.email, password = hash_password(data.password))
    db.add(new_influencer)
    db.commit()
    db.refresh(new_influencer)
    return new_influencer

