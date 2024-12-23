from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from ..db.session import SessionDep
from ..services import user_services
from ..schemas.user_schema import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_users(session: SessionDep) -> list[UserResponse]:
    try:
        return user_services.get_all_users(session)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/{user_id}")
async def get_user_by_id(user_id: UUID, session: SessionDep) -> UserResponse:
    try:
        return user_services.get_user_by_id(user_id, session)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             responses={
                 400: {
                     "description": "Bad Request - El correo electrónico o el nombre de usuario ya existe en la base de datos.",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Email already exists"
                             }
                         }
                     }
                 }
             })
async def create_user(user: UserCreate, session: SessionDep) -> UserResponse:
    try:
        return user_services.create_user(user, session)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.patch("/{user_id}")
async def update_user(user_id: UUID, user: UserCreate, session: SessionDep) -> UserResponse:
    try:
        return user_services.update_user(user_id, user, session)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: SessionDep):
    try:
        user_services.delete_user(user_id, session)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
