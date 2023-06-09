from pydantic import BaseModel
from datetime import datetime

class ProjectCreate(BaseModel):
    project_name: str
    deadline: str
    editor: str

class UserCreate(BaseModel):
    login: str
    username: str
    password: str
    role: str
    status: str | None
    efficiency: float | None
    is_active: bool

class UserBase(BaseModel):
    login: str
    username: str
    role: str
    status: str | None


class TokenBase(BaseModel):
    access_token: str
    token_type: None | str = "bearer"

    class Config:
        allow_population_by_field_name = True

class TokenData(BaseModel):
    id: str | None

class User(UserBase):
    token: TokenBase = {}

class ActivityModel(BaseModel):
    activity_name: str
    project_name: str
    translators: str | None
    editor: str
    deadline: datetime
    project_status: str
    completeness: float
    status: str

class LoginForm(BaseModel):
    login: str
    password: str