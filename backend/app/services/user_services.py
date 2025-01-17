from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
from ..utils.auth import get_password_hash
from ..db.session import SessionDep
from ..schemas.user_schema import UserCreate, UserResponse, UserUpdate
from ..db.models import User


def get_all_users(session: SessionDep) -> list[UserResponse]:
    try:
        users = session.exec(select(User)).all()
        return [UserResponse.model_validate(user) for user in users]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


def get_user_by_id(user_id: str, session: SessionDep) -> UserResponse:
    db_user = session.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(db_user)


def create_user(user_data: UserCreate, session: SessionDep) -> UserResponse:
    db_user = User.model_validate(user_data.model_dump())
    db_user.password = get_password_hash(db_user.password)
    if session.exec(select(User).where(User.email == db_user.email)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    if session.exec(select(User).where(User.username == db_user.username)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    if db_user.age < 18:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Age must be a positive number")
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(user_id: str, user: UserUpdate, session: SessionDep):
    db_user = session.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_data_dict = user.model_dump(exclude_unset=True)
    for key, value in user_data_dict.items():
        if key == "password":
            hashed_password = get_password_hash(value)
            setattr(db_user, key, hashed_password)
        if key == "age" and value < 18:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Age must be a positive number")
        else:
            setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(user_id: str, session: SessionDep):
    db_user = session.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.delete(db_user)
    session.commit()
