import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from datetime import timedelta
from ..db.models import User
from ..db.session import SessionDep
from ..schemas.auth import Token, GoogleUserData
from ..auth.jwt_manager import create_access_token
from ..services.auth_service import get_current_active_user, authenticate_user, authenticate_with_google, create_google_user, create_google_oauth_flow, get_google_authorization_url

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


@router.post("/login", responses={
    400: {
        "description": "Incorrect username or password",
        "content": {
            "application/json": {
                "example": {"detail": "Incorrect username or password"}
            }
        }
    },
    401: {
        "description": "Invalid token",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid token"}
            }
        }
    },
    500: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
})
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep,
) -> Token:
    user = authenticate_user(
        username=form_data.username, password=form_data.password, session=session)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/google/login")
async def google_login():
    """Inicia el flujo de autenticación con Google"""
    auth_data = get_google_authorization_url()
    return RedirectResponse(auth_data["url"])


@router.get("/google/callback")
async def google_callback(
    code: str,
    session: SessionDep,
):
    """Maneja la respuesta de Google después de la autenticación"""
    try:
        flow = create_google_oauth_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials

        user_info = await authenticate_with_google(credentials.id_token, session)

        if isinstance(user_info, dict):
            if user_info.get('age'):
                user = await create_google_user(
                    session=session,
                    google_data=user_info
                )
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": user.username, "scopes": ["me"]},
                    expires_delta=access_token_expires,
                )
                return Token(access_token=access_token, token_type="bearer")
            else:
                # Si no tenemos la edad, pedimos información adicional
                return {
                    "status": "pending",
                    "message": "Additional information required",
                    "google_data": user_info,
                    "required_fields": ["age"]
                }

        # Usuario existente
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_info.username, "scopes": ["me"]},
            expires_delta=access_token_expires,
        )
        return Token(access_token=access_token, token_type="bearer")

    except Exception as e:
        print(f"Error detallado: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error during Google authentication: {str(e)}"
        )


@router.post("/google/complete-registration")
async def complete_google_registration(
    google_data: dict,
    user_data: GoogleUserData,
    session: SessionDep
):
    try:
        user = await create_google_user(
            session=session,
            google_data=google_data,
            additional_data={"age": user_data.age}
        )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "scopes": ["me"]},
            expires_delta=access_token_expires,
        )
        return Token(access_token=access_token, token_type="bearer")

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error completing registration: {str(e)}"
        )
