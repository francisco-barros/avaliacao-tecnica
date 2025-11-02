from ..extensions import db
from .models import Project
from ..user.models import User


class ProjectRepository:
    @staticmethod
    def create(project: Project) -> Project:
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def get_by_id(project_id: str) -> Project | None:
        return Project.query.filter(Project.deleted_at.is_(None)).filter_by(id=project_id).first()

    @staticmethod
    def list_for_user(user_id: str) -> list[Project]:
        return (
            Project.query.filter(Project.deleted_at.is_(None))
            .join(Project.members, isouter=True)
            .filter((Project.owner_id == user_id) | (User.id == user_id))
            .all()
        )

    @staticmethod
    def update(project: Project) -> Project:
        db.session.commit()
        return project

    @staticmethod
    def delete(project: Project) -> None:
        project.soft_delete()
        db.session.commit()
