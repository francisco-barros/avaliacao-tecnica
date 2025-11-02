import pytest
from src.factory import create_app
from src.settings import AppConfig
from src.extensions import db
from src.user.repository import UserRepository
from src.user.models import UserRole


class TestConfig(AppConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    REDIS_URL = "redis://localhost:6379/15"


class MockCache:
    def __init__(self):
        self._store = {}
    
    def init_app(self, app):
        pass
    
    def get(self, key: str):
        return self._store.get(key)
    
    def set(self, key: str, value: str, ex: int | None = None):
        self._store[key] = value
        return True


@pytest.fixture()
def app():
    from src.cache import cache
    
    mock_cache_instance = MockCache()
    
    cache.client = None
    original_get = cache.get
    original_set = cache.set
    cache.get = mock_cache_instance.get
    cache.set = mock_cache_instance.set
    
    app = create_app(TestConfig())
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    cache.client = None
    cache.get = original_get
    cache.set = original_set


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_user():
    return UserRepository.create("Admin", "admin@x.com", "pass", role=UserRole.ADMIN.value)


@pytest.fixture()
def manager_user():
    return UserRepository.create("Manager", "manager@x.com", "pass", role=UserRole.MANAGER.value)


@pytest.fixture()
def member_user():
    return UserRepository.create("Member", "member@x.com", "pass", role=UserRole.MEMBER.value)


@pytest.fixture()
def test_user():
    return UserRepository.create("Test User", "test@example.com", "password123", role=UserRole.MEMBER.value)


@pytest.fixture()
def auth_token(client):
    def _auth_token(email: str, password: str) -> str:
        resp = client.post("/api/auth/login", json={"email": email, "password": password})
        return resp.get_json()["access_token"]
    return _auth_token


@pytest.fixture()
def admin_token(auth_token, admin_user):
    return auth_token(admin_user.email, "pass")


@pytest.fixture()
def manager_token(auth_token, manager_user):
    return auth_token(manager_user.email, "pass")


@pytest.fixture()
def member_token(auth_token, member_user):
    return auth_token(member_user.email, "pass")


@pytest.fixture()
def project_data():
    return {"name": "Project 1", "description": "Description 1"}


@pytest.fixture()
def task_data():
    return {
        "title": "Task 1",
        "description": "Task description",
    }
