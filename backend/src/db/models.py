from datetime import datetime
import re
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from pydantic import StringConstraints, field_validator
from typing import Annotated

Username = Annotated[
    str, StringConstraints(min_length=5, max_length=64)
]

def whitespace_filter(v: str):
    # imlpement seperate whitespace filter from string constraints for better error message
    if re.search(r'\s', v):
        raise ValueError('Invalid characters found in input. Cannot contain whitespace')
    return v


class UserBase(SQLModel):
    username: Username = Field(index=True, unique=True)
    username_filter = field_validator('username')(whitespace_filter)


class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, unique=True)
    password: bytes
    admin: bool = Field(default=False)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    admin: bool = False

    password_filter = field_validator('password')(whitespace_filter)


class UserUpdate(UserBase):
    username: Username | None = Field(default=None)
    password: str | None = Field(default=None)

    password_filter = field_validator('password')(whitespace_filter)


class UserPublic(UserBase):
    id: UUID
    admin: bool = False


class TaskBase(SQLModel):
    title: str = Field(index=True, min_length=1, max_length=256)
    description: str | None = Field(default=None, max_length=2048)
    assigned_to: UUID | None = Field(foreign_key="user.id")
    due: datetime | None = None


class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True, unique=True)
    created_by: UUID = Field(foreign_key="user.id")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)


class TaskCreate(TaskBase):
    assigned_to: UUID | None = None


class TaskUpdate(TaskBase):
    title: str | None = Field(default=None, min_length=1, max_length=256)
    description: str | None = Field(default=None, max_length=2048)
    assigned_to: UUID | None = None
    completed: bool | None = None
    due: datetime | None = None


class TaskPublic(TaskBase):
    id: UUID
    created_by: UUID
    completed: bool
    created_at: datetime
