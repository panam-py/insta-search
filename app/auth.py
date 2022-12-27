from pydantic import BaseModel

from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT, exceptions

from .database import get_db, Session

from .models import User

from .config import settings

class JWTSettings(BaseModel):
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_secret_key: str = settings.JWT_SECRET_KEY
    authjwt_cookie_csrf_protect: bool = False

@AuthJWT.load_config
def get_config():
    return JWTSettings()

def authenticate(db: Session = Depends(get_db), Auth: AuthJWT = Depends()):
    """
    Function to protect routes so as to enable only authenticated
    users proceed to routes
    """
    try:
        Auth.jwt_required()
        user_id = Auth.get_jwt_subject()
        user = db.query(User).filter(User.id == user_id).first()


        if not user:
            raise Exception('User account deleted recently')
    except Exception as e:
        print(e.message, e.__class__.__name__)
        # return None
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = e.message)
    return user_id