from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from datetime import timedelta

from .schemas import RegisterIn

from .models import User

from .utils import hash_password, compare_password

from .database import get_db

from .config import settings

from .auth import AuthJWT

ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

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
async def register(data: RegisterIn, response: Response, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user collecting email and
    password
    """
    data.email = data.email.lower()
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"A user already exists with the email {data.email}")
    new_user = User(email = data.email, password = hash_password(data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    del new_user.password
    response.status_code = status.HTTP_201_CREATED
    return {'status': 'success', 'data': new_user}


@app.post("/login")
async def login(data: RegisterIn, response: Response, db: Session = Depends(get_db), Auth: AuthJWT = Depends()):
    """
    """
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if (not user) or (not compare_password(data.password, user.password)):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Incorrect email or password')

    access_token = Auth.create_access_token(subject = str(user.id), expires_time = timedelta(minutes = ACCESS_TOKEN_EXPIRES_IN))
    refresh_token = Auth.create_refresh_token(subject = str(user.id), expires_time = timedelta(minutes = REFRESH_TOKEN_EXPIRES_IN))

    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    del user.password
    response.status_code = status.HTTP_200_OK
    return {'status': 'success', 'access_token': access_token, 'refresh_token': refresh_token, 'data': user}