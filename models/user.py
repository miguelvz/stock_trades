from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4


def generate_date():
    return str(datetime.now())


def generate_id():
    return str(uuid4())


class Symbols(BaseModel):
    user_id: str | None = None
    symbols: list
    created_at: str = Field(default_factory=generate_date)


class User(BaseModel):
    username: str
    password: str

    
