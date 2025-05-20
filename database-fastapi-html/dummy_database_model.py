from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(SQLModel, table=True):
    #dummy data
    #real database to be implement by 용한님
    id: int | None = Field(default=None, primary_key=True)
    password: str
    sex: str
    age: int
    height: float
    weight: float