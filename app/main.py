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

# Setting constants for Token expiry
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

# Declaring app
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
    # Setting email to always be lower case
    data.email = data.email.lower()
    # Checking if user already exists and returning appropriate error
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"A user already exists with the email {data.email}")
    # Create a new user and save to DB
    new_user = User(email = data.email, password = hash_password(data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    del new_user.password
    # Response Handling
    response.status_code = status.HTTP_201_CREATED
    return {'status': 'success', 'data': new_user}


@app.post("/login")
async def login(data: RegisterIn, response: Response, db: Session = Depends(get_db), Auth: AuthJWT = Depends()):
    """
    Route to login users
    """
    # Finding user by email
    user = db.query(User).filter(User.email == data.email.lower()).first()
    # Return error if user does not exist or password is incorrect
    if (not user) or (not compare_password(data.password, user.password)):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Incorrect email or password')

    # Creating tokens
    access_token = Auth.create_access_token(subject = str(user.id), expires_time = timedelta(minutes = ACCESS_TOKEN_EXPIRES_IN))
    refresh_token = Auth.create_refresh_token(subject = str(user.id), expires_time = timedelta(minutes = REFRESH_TOKEN_EXPIRES_IN))

    # Setting cookies with tokens created
    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    # Stripping user to be returned of the password as it is sensitive
    del user.password

    # Response Handling
    response.status_code = status.HTTP_200_OK
    return {'status': 'success', 'access_token': access_token, 'refresh_token': refresh_token, 'data': user}


@app.get('/refresh')
async def refresh_token(response: Response, request: Request, Auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    """
    Route to handle refreshing of tokens
    """
    # Try to get refresh token and create new access token based on this
    try:
        # Getting refresh token from request
        Auth.jwt_refresh_token_required()

        # Getting jwt subject(user_id) from token
        user_id = Auth.get_jwt_subject()

        # Return a bad response if user_id does not exist
        if not user_id:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Could not refresh access token')
        
        # Fetching the user from DB and returning a nad response if user does not exist
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "User account deleted recently")

        # Creating new access token
        access_token = Auth.create_access_token(subject = str(user.id), expires_time = timedelta(minutes = ACCESS_TOKEN_EXPIRES_IN))
    # If try block fails return a bad response with name of error
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = e.__class__.__name__)

    # Setting cookies with newly created access token
    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    # Handling response
    response.status_code = status.HTTP_200_OK
    return {'access_token': access_token}


@app.get('/logout')
async def logout(response: Response, Auth: AuthJWT = Depends()):
    """
    Route to logout user
    """
    # Delete tokens from cookies and return successful response
    Auth.unset_jwt_cookies()
    response.status_code = status.HTTP_200_OK
    return {'status': 'success'}


@app.post('/onboarding')
async def onboard_influencer(data: OnBoardIn, response: Response, db: Session = Depends(get_db), user_id = Depends(authenticate)):
    """
    Route to onboard(collect info) for an influencer who is already an authenticated user
    """
    # Return a bad response if there is already an influencer with this username
    influencer = db.query(Influencer).filter(Influencer.username == data.username).first()
    if influencer:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "An influencer with these details has already been recoreded")

    # Creating new influencer with data given and adding to the db
    new_influencer = Influencer(user_id = user_id, **data.dict())
    db.add(new_influencer)
    db.commit()
    db.refresh(new_influencer)

    # Handling response
    response.status_code = status.HTTP_201_CREATED
    return {'status': 'success', 'data': new_influencer}


@app.get('/search')
async def search_influencers(response: Response, db: Session = Depends(get_db), keyword: Optional[str] = None, min_followers: Optional[int] = None, max_followers: Optional[int] = None):
    """
    Endpoint to search for influencers based on some parameters
    """
    # Fetch all influencers from the DB at first
    all_influencers = db.query(Influencer).all()
    
    # Filter the list of influencers based on maximum amount of followers if the "max_followers" query parameter exists
    if max_followers:
        all_influencers = [influencer for influencer in all_influencers if influencer.follower_count <= max_followers]
    
    # Filter the list of influencers based on minimum amount of followers if the "min_followers" query parameter exists
    if min_followers:
        all_influencers = [influencer for influencer in all_influencers if influencer.follower_count >= min_followers]

    # Using the keyword to search bios and usernames of influencers
    if keyword:
        all_influencers = [influencer for influencer in all_influencers if (influencer.bio and keyword in influencer.bio) or keyword in influencer.username]

    # Handling response
    response.status_code = status.HTTP_200_OK
    return {'status': 'success', 'count': len(all_influencers), 'data': all_influencers}


        

    