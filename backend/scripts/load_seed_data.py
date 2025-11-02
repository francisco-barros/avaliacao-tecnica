#!/usr/bin/env python3

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.factory import create_app
from src.extensions import db
from src.user.models import User, UserRole
from src.project.models import Project
from src.task.models import Task, TaskStatus
from src.user.repository import UserRepository


def load_users(seed_file: Path) -> int:
    if User.query.count() > 0:
        print(f"  ℹ️  Users already exist, skipping user seed data")
        return 0
    
    with open(seed_file) as f:
        data = json.load(f)
    
    count = 0
    for user_data in data['users']:
        if User.query.filter_by(email=user_data['email']).first():
            continue
            
        user = UserRepository.create(
            name=user_data['name'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role']
        )
        count += 1
    
    if count > 0:
        print(f"  ✅ Created {count} users")
    else:
        print(f"  ℹ️  No new users to create")
    
    return count


def load_projects(seed_file: Path, owner_id: str) -> int:
    if Project.query.count() > 0:
        print(f"  ℹ️  Projects already exist, skipping project seed data")
        return 0
    
    with open(seed_file) as f:
        data = json.load(f)
    
    count = 0
    for project_data in data['projects']:
        project = Project(
            name=project_data['name'],
            description=project_data['description'],
            owner_id=owner_id
        )
        db.session.add(project)
        count += 1
    
    if count > 0:
        db.session.commit()
        print(f"  ✅ Created {count} projects")
    else:
        print(f"  ℹ️  No new projects to create")
    
    return count


def load_tasks(seed_file: Path, project_id: str, assignee_id: str = None) -> int:
    with open(seed_file) as f:
        data = json.load(f)
    
    projects = Project.query.all()
    if not projects:
        print(f"  ℹ️  No projects found, skipping task seed data")
        return 0
    
    count = 0
    project_idx = 0
    
    for task_data in data['tasks']:
        project = projects[project_idx % len(projects)]
        project_idx += 1
        
        if Task.query.filter_by(title=task_data['title'], project_id=project.id).first():
            continue
        
        task = Task(
            title=task_data['title'],
            description=task_data['description'],
            status=TaskStatus(task_data.get('status', 'pending')),
            project_id=project.id,
            assignee_id=assignee_id if assignee_id else project.owner_id
        )
        db.session.add(task)
        count += 1
    
    if count > 0:
        db.session.commit()
        print(f"  ✅ Created {count} tasks")
    else:
        print(f"  ℹ️  No new tasks to create")
    
    return count


def main():
    print("🌱 Loading seed data...")
    print("-" * 60)
    
    app = create_app()
    
    seed_dir = Path(__file__).parent.parent / 'seed'
    
    with app.app_context():
        try:
            print("\n📝 Loading users...")
            user_count = load_users(seed_dir / 'users.json')
            
            admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
            if not admin_user:
                print("  ⚠️  No admin user found, skipping projects and tasks")
                print("\n✅ Seed data loading completed with warnings")
                return
            
            if user_count > 0 or Project.query.count() == 0:
                print("\n📁 Loading projects...")
                project_count = load_projects(seed_dir / 'projects.json', admin_user.id)
                
                print("\n✅ Loading tasks...")
                task_count = load_tasks(seed_dir / 'tasks.json', admin_user.id)
            else:
                project_count = 0
                task_count = 0
            
            print("-" * 60)
            print("✅ Seed data loading completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error loading seed data: {e}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    main()

