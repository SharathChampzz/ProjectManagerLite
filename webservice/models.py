from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    role = Column(String, default="user", nullable=False)
    created_time = Column(DateTime, server_default=func.now())
    
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String, index=True)
    criticality = Column(String)
    status = Column(String)
    thread_id = Column(String)
    html_file = Column(Text)
    created_time = Column(DateTime, server_default=func.now())
    last_reminder_sent_time = Column(DateTime, default=None) # Assume reminder sent time is set when task is created

    creator = relationship("User", foreign_keys=[creator_id])
    assigner = relationship("User", foreign_keys=[assigner_id])

class TaskProp(Base):
    __tablename__ = "taskprops"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    attrname = Column(String, nullable=False)
    attrval = Column(String, nullable=False)
    modified_time = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="props")

class TaskReminderHistory(Base):
    __tablename__ = "TaskReminderHistory"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    reminder_sent_time = Column(DateTime, server_default=func.now())

    task = relationship("Task", back_populates="reminderhistory")

Task.reminderhistory = relationship("TaskReminderHistory", order_by=TaskReminderHistory.id, back_populates="task")
Task.props = relationship("TaskProp", order_by=TaskProp.id, back_populates="task")
