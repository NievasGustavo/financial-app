from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..auth.jwt_manager import verify_jwt_token
from ..db.models import User
from ..services.user_services import get_user_by_id
from ..db.session import SessionDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        # Verificar el token y obtener el usuario
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")  # 'sub' contiene el ID del usuario
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: 'sub' no encontrado en el payload",
            )
        # Obtener el usuario desde la base de datos
        user = get_user_by_id(user_id, SessionDep)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from e
