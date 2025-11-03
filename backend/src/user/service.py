from passlib.hash import bcrypt
from .repository import UserRepository
from ..project.repository import ProjectRepository
from ..task.repository import TaskRepository
from .models import User, UserRole
from ..task.models import TaskStatus
from ..extensions import db
from ..cache import cache


class UserService:
    @staticmethod
    def create_user(name: str, email: str, password: str, role: str | None = None) -> User:
        try:
            user = UserRepository.create(name=name, email=email, password=password, role=role)
            cache.delete("users:all")
            return user
        except Exception as e:
            from sqlalchemy.exc import IntegrityError
            if isinstance(e, IntegrityError):
                raise
            raise

    @staticmethod
    def authenticate(email: str, password: str) -> User | None:
        user = UserRepository.get_by_email(email)
        if user and bcrypt.verify(password, user.password_hash):
            return user
        return None

    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        cache_key = f"user:{user_id}"
        cached = cache.get(cache_key)
        if cached:
            import json
            data = json.loads(cached)
            data["role"] = UserRole(data["role"])
            return User(**data)
        user = UserRepository.get_by_id(user_id)
        if user:
            import json
            cache.set(cache_key, json.dumps(user.to_dict()), ex=60)
        return user

    @staticmethod
    def list_users() -> list[User]:
        cache_key = "users:all"
        cached = cache.get(cache_key)
        if cached:
            import json
            users_data = json.loads(cached)
            return [User(**{**u, "role": UserRole(u["role"])}) for u in users_data]
        users = UserRepository.list_all()
        import json
        cache.set(cache_key, json.dumps([u.to_dict() for u in users]), ex=60)
        return users

    @staticmethod
    def update_user(user_id: str, data: dict) -> User:
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("user not found")
        if "role" in data:
            user.role = UserRole(data["role"])
        if "name" in data:
            user.name = data["name"]
        if "email" in data:
            user.email = data["email"]
        db.session.commit()
        cache.delete(f"user:{user_id}")
        cache.delete("users:all")
        return user

    @staticmethod
    def delete_user(user_id: str) -> None:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return
        
        for project in list(user.projects_owned):
            project.owner_id = None
        for task in list(user.tasks):
            task.status = TaskStatus.AWAITING_REASSIGNMENT
            task.assignee_id = None
        
        user.soft_delete()
        db.session.commit()
        
        cache.delete(f"user:{user_id}")
        cache.delete("users:all")
