from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

    #dummy data to print result at html 
    #real database to be implement by 용한님
class Result(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    explain1: str
    explain2: str
    explain3: str
    img1 :str
    img2 : str
    img3 : str

