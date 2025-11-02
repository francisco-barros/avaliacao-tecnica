from passlib.hash import bcrypt
from ..extensions import db
from .models import User, UserRole


class UserRepository:
    @staticmethod
    def create(name: str, email: str, password: str, role: str | None = None) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=bcrypt.hash(password),
            role=UserRole(role) if role else UserRole.MEMBER,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.query.filter(User.deleted_at.is_(None)).filter_by(email=email).first()

    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        return User.query.filter(User.deleted_at.is_(None)).filter_by(id=user_id).first()

    @staticmethod
    def list_all() -> list[User]:
        return User.query.filter(User.deleted_at.is_(None)).order_by(User.created_at.desc()).all()

    @staticmethod
    def delete(user_id: str) -> None:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return
        user.soft_delete()
        db.session.commit()
