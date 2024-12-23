from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
from ..db.session import SessionDep
from ..schemas.user_schema import UserCreate, UserResponse
from ..db.models import User


def get_all_users(session: SessionDep) -> list[UserResponse]:
    try:
        users = session.exec(select(User)).all()
        return [UserResponse.from_orm(user) for user in users]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


def get_user_by_id(user_id: str, session: SessionDep) -> UserResponse:
    db_user = session.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


def create_user(user_data: UserCreate, session: SessionDep) -> UserResponse:
    db_user = User.model_validate(user_data.model_dump())
    db_user.password = bcrypt.hashpw(
        db_user.password.encode("utf-8"), bcrypt.gensalt()
    )
    if session.exec(select(User).where(User.email == db_user.email)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    if session.exec(select(User).where(User.username == db_user.username)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(user_id: str, user: UserCreate, session: SessionDep):
    db_user = session.exec(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_data_dict = user.model_dump(exclude_unset=True)
    for key, value in user_data_dict.items():
        if key == "password":
            hashed_password = bcrypt.hashpw(
                value.encode("utf-8"), bcrypt.gensalt())
            value = hashed_password.decode("utf-8")
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
