from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    is_active: bool
    is_superuser: bool
    role: str

    class Config:
        orm_mode = True

class UpdateUser(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    username: str | None = None


class TaskStatus(str, Enum):
    OPEN = "OPEN"
    FIXED = "FIXED"
    CLOSED = "CLOSED"
    
class TaskCriticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
class TaskUpdate(BaseModel):
    creator_id: Optional[int]
    assigner_id: Optional[int]
    subject: Optional[str]
    criticality: Optional[TaskCriticality]
    status: Optional[TaskStatus]
    html_file: Optional[str]
    thread_id: Optional[str]

class TaskCreate(BaseModel):
    creator_name: str
    assigner_name: str
    subject: str
    criticality: TaskCriticality
    status: TaskStatus
    html_file: str
    thread_id: str

class Task(TaskCreate):
    id: int
    created_time: datetime
    last_reminder_sent_time: datetime | None

    class Config:
        orm_mode = True
