from passlib.hash import bcrypt
from ..extensions import db
from .models import User, UserRole
from sqlalchemy.exc import IntegrityError


class UserRepository:
    @staticmethod
    def create(name: str, email: str, password: str, role: str | None = None) -> User:
        try:
            user = User(
                name=name,
                email=email,
                password_hash=bcrypt.hash(password),
                role=UserRole(role) if role else UserRole.MEMBER,
            )
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError as e:
            db.session.rollback()
            error_msg = str(e).lower()
            if "unique constraint" in error_msg or "duplicate key" in error_msg or "uniqueviolation" in error_msg or "already exists" in error_msg:
                raise ValueError("Email already in use")
            raise

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
