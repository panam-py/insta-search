from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT

from .config import settings

class JWTSettings(BaseModel):
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_secret_key: str = settings.JWT_SECRET_KEY

@AuthJWT.load_config
def get_config():
    return JWTSettings()