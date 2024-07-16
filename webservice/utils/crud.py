from sqlalchemy.orm import Session, aliased
from utils import dependencies
import models, schemas
from fastapi import HTTPException
from typing import List
from datetime import datetime

def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: dict = None
) -> List[models.Task]:
    """Get a list of tasks from the database."""
    creator_alias = aliased(models.User, name="creator")
    assigner_alias = aliased(models.User, name="assigner")
    
    query = (
        db.query(
            models.Task.id,
            models.Task.subject,
            models.Task.criticality,
            models.Task.status,
            models.Task.html_file,
            models.Task.thread_id,
            models.Task.created_time,
            models.Task.last_reminder_sent_time,
            creator_alias.username.label("creator_name"),
            assigner_alias.username.label("assigner_name")
        )
        .join(creator_alias, models.Task.creator_id == creator_alias.id)
        .join(assigner_alias, models.Task.assigner_id == assigner_alias.id)
    )
    
    if filters:
        for key, value in filters.items():
            if "__contains" in key:
                field_name = key.split("__")[0]
                query = query.filter(getattr(models.Task, field_name).ilike(f"%{value}%"))
            else:
                query = query.filter(getattr(models.Task, key) == value)
    
    query = query.offset(skip).limit(limit)
    task_data_list = query.all()

    tasks = [
        schemas.Task(
            id=task_data.id,
            creator_name=task_data.creator_name,
            assigner_name=task_data.assigner_name,
            subject=task_data.subject,
            criticality=task_data.criticality,
            status=task_data.status,
            html_file=task_data.html_file,
            thread_id=task_data.thread_id,
            created_time=task_data.created_time,
            last_reminder_sent_time=task_data.last_reminder_sent_time
        )
        for task_data in task_data_list
    ]
    
    return tasks


def check_user_exists(db: Session, username: str) -> bool:
    """Check if a user exists in the database."""
    return db.query(models.User).filter(models.User.username == username).first() is not None

def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """Create a task in the database.""" 
    # replace the username with user_id
    creator = db.query(models.User).filter(models.User.username == task.creator_name).first()
    assigner = db.query(models.User).filter(models.User.username == task.assigner_name).first()
    
    if not creator:
        raise HTTPException(status_code=404, detail="Creator User not found")
    
    if not assigner:
        raise HTTPException(status_code=404, detail="Assigner User not found")
    
    input_task = task.model_dump()
    input_task["creator_id"] = creator.id
    input_task["assigner_id"] = assigner.id
    input_task.pop("creator_name")
    input_task.pop("assigner_name")
    db_task = models.Task(**input_task)  # Use the modified input_task dictionary
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int) -> schemas.Task:
    """Get a task from the database."""
    # join task with user to get creator and assigner names
    creator_alias = aliased(models.User, name="creator")
    assigner_alias = aliased(models.User, name="assigner")
    
    task_data = (
        db.query(
            models.Task.id,
            models.Task.subject,
            models.Task.criticality,
            models.Task.status,
            models.Task.html_file,
            models.Task.thread_id,
            models.Task.created_time,
            models.Task.last_reminder_sent_time,
            creator_alias.username.label("creator_name"),
            assigner_alias.username.label("assigner_name")
        )
        .join(creator_alias, models.Task.creator_id == creator_alias.id)
        .join(assigner_alias, models.Task.assigner_id == assigner_alias.id)
        .filter(models.Task.id == task_id)
        .first()
    )
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    task = {
        "id": task_data.id,
        "creator_name": task_data.creator_name,
        "assigner_name": task_data.assigner_name,
        "subject": task_data.subject,
        "criticality": task_data.criticality,
        "status": task_data.status,
        "html_file": task_data.html_file,
        "thread_id": task_data.thread_id,
        "created_time": task_data.created_time,
        "last_reminder_sent_time": task_data.last_reminder_sent_time
    }

    return schemas.Task(**task)

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate) -> models.Task:
    """Update a task in the database."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        return None
    for key, value in task.model_dump().items():
        if value is not None:
            setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task from the database."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def set_last_reminder_sent_time(db: Session, task_id: int) -> bool:
    """Set the last reminder sent time for a task."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.last_reminder_sent_time = datetime.now()
        db.commit()
        return True
    return False

#### User CRUDs ####

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get a list of users from the database."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a user in the database."""
    hashed_password = dependencies.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> models.User:
    """Get a user from the database."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> models.User:
    """Get a user by their username."""
    return db.query(models.User).filter(models.User.username == username).first()

def update_user(db: Session, user_id: int, user: schemas.UpdateUser) -> models.User:
    """Update a user in the database."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    for key, value in user.model_dump().items():
        if value is not None:
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user from the database."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
    
    