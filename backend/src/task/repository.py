from ..extensions import db
from .models import Task


class TaskRepository:
    @staticmethod
    def create(task: Task) -> Task:
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def get_by_id(task_id: str) -> Task | None:
        return Task.query.filter(Task.deleted_at.is_(None)).filter_by(id=task_id).first()

    @staticmethod
    def list_for_project(project_id: str) -> list[Task]:
        return Task.query.filter(Task.deleted_at.is_(None)).filter_by(project_id=project_id).all()

    @staticmethod
    def update(task: Task) -> Task:
        db.session.commit()
        return task

    @staticmethod
    def delete(task: Task) -> None:
        task.soft_delete()
        db.session.commit()
