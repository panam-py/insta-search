from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional

from sqlalchemy.orm import Session

from datetime import timedelta

from .schemas import RegisterIn, OnBoardIn

from .models import User, Influencer

from .utils import hash_password, compare_password

from .database import get_db

from .config import settings

from .auth import AuthJWT, authenticate

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


@app.get('/refresh')
async def refresh_token(response: Response, request: Request, Auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    """
    """
    try:
        Auth.jwt_refresh_token_required()

        user_id = Auth.get_jwt_subject()
        if not user_id:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Could not refresh access token')
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "User account deleted recently")

        access_token = Auth.create_access_token(subject = str(user.id), expires_time = timedelta(minutes = ACCESS_TOKEN_EXPIRES_IN))
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = e.__class__.__name__)

    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    response.status_code = status.HTTP_200_OK
    return {'access_token': access_token}


@app.get('/logout')
async def logout(response: Response, Auth: AuthJWT = Depends()):
    """
    """
    Auth.unset_jwt_cookies()
    response.status_code = status.HTTP_200_OK
    return {'status': 'success'}


@app.post('/onboarding')
async def onboard_influencer(data: OnBoardIn, response: Response, db: Session = Depends(get_db), user_id = Depends(authenticate)):
    """
    """
    influencer = db.query(Influencer).filter(Influencer.username == data.username).first()
    if influencer:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "An influencer with these details has already been recoreded")

    new_influencer = Influencer(user_id = user_id, **data.dict())
    db.add(new_influencer)
    db.commit()
    db.refresh(new_influencer)
    response.status_code = status.HTTP_201_CREATED
    return {'status': 'success', 'data': new_influencer}


@app.get('/search')
async def search_influencers(response: Response, db: Session = Depends(get_db), keyword: Optional[str] = None, min_followers: Optional[int] = None, max_followers: Optional[int] = None):
    """
    """
    all_influencers = db.query(Influencer).all()
    
    if max_followers:
        all_influencers = [influencer for influencer in all_influencers if influencer.follower_count <= max_followers]
    
    if min_followers:
        all_influencers = [influencer for influencer in all_influencers if influencer.follower_count >= min_followers]

    if keyword:
        all_influencers = [influencer for influencer in all_influencers if (influencer.bio and keyword in influencer.bio) or keyword in influencer.username]

    response.status_code = status.HTTP_200_OK
    return {'status': 'success', 'count': len(all_influencers), 'data': all_influencers}


        

    