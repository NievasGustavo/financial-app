import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from app.main import app
from app.db.session import get_session
from app.db.models import User

SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(SQLITE_URL, connect_args={
                       "check_same_thread": False}, poolclass=StaticPool)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(session):
    user_id = uuid.uuid4()
    user = User(id=user_id, username="testuser", password="testpassword", first_name="Test", last_name="User", email="test@example.com", age=25)
    session.add(user)
    session.commit()
    return user
