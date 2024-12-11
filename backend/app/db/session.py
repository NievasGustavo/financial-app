from os import getenv
from dotenv import load_dotenv
from typing import Annotated
from sqlmodel import Session, create_engine
from fastapi import Depends

load_dotenv()

DB_URL = getenv("SQL_URL")
if not DB_URL:
    raise ValueError("La variable de entorno SQL_URL no está configurada")

engine = create_engine(DB_URL)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
