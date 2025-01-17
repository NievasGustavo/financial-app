
import os
from typing import Annotated, Optional, Union
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import httpx
import jwt
from pydantic import ValidationError
from sqlmodel import select

from app.db.models import User
from app.db.session import SessionDep
from app.schemas.auth import TokenData
from app.utils.auth import get_password_hash, verify_password

oaut2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
load_dotenv(override=True)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


def authenticate_user(session: SessionDep, username: str, password: str):
    """Autentica un usuario en función de su nombre de usuario y contraseña"""
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user(db: SessionDep, username: str):
    """Obtiene un usuario en función de su nombre de usuario"""
    return db.exec(select(User).where(User.username == username)).first()


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oaut2_scheme)],
    session: SessionDep
):
    """Obtiene el usuario actual en función de los scopes y el token"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (jwt.InvalidTokenError, ValidationError) as exc:
        raise credentials_exception from exc
    user = get_user(session, token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
):
    return current_user


def get_google_authorization_url() -> dict:
    """Genera la URL de autorización de Google"""
    flow = create_google_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return {
        "url": authorization_url,
        "state": state
    }

def create_google_oauth_flow() -> Flow:
    """Crea y configura el flujo de OAuth para Google"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI],
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/user.birthday.read"
        ]
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow

async def get_user_profile(access_token: str):
    # Hacer la solicitud a la People API
    url = "https://people.googleapis.com/v1/people/me?personFields=birthdays,emailAddresses,names,photos"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    return response.json()


async def authenticate_with_google(token: str, session: SessionDep) -> Optional[Union[User, dict]]:
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID)

        if idinfo['aud'] != GOOGLE_CLIENT_ID:
            raise ValueError('Invalid audience')
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')

        email = idinfo['email']
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')

        access_token = token
        user_profile = await get_user_profile(access_token)
        
        age = None
        if "birthdays" in user_profile and user_profile["birthdays"]:
            from datetime import datetime
            birthday = user_profile["birthdays"][0].get("date", {})
            if birthday and "year" in birthday:
                birth_year = int(birthday["year"])
                current_year = datetime.now().year
                age = current_year - birth_year

        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            return {
                'email': email,
                'given_name': given_name,
                'family_name': family_name,
                'age': age
            }

        return user

    except Exception as e:
        print(f"Error authenticating with Google: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

async def create_google_user(
    session: SessionDep,
    google_data: dict,
    additional_data: dict = None
) -> User:
    """Crea un nuevo usuario con datos de Google y datos adicionales"""
    # Genera una contraseña aleatoria segura
    random_password = get_password_hash(os.urandom(32).hex())
    
    age = additional_data.get('age') if additional_data else google_data.get('age')
    
    if age is None:
        age = 18
    
    user = User(
        email=google_data['email'],
        username=google_data['email'].split('@')[0],
        first_name=google_data.get('given_name', '').split(' ')[0],
        last_name=google_data.get('family_name', '').split(' ')[0],
        age=age,
        password=random_password
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user