# -*- coding: utf-8 -*-
from sqlmodel import Field, SQLModel, create_engine, Session, select


class test(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(index=True, unique=True)
    password: str
    gender: str
    age: int
    height: float
    weight: float

class userData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(index=True, unique=True)
    password: str


test_1 = test(id="1", login_id="alpha", password="alpah1", gender="male", age=30, height=175.5, weight=70.0)
test_2 = test(id="2", login_id="beta", password="beta2", gender="female", age=25, height=160.0, weight=55.0)
test_3 = test(id="3", login_id="gamma", password="gamma3", gender="non-binary", age=28, height=180.0, weight=80.0)

user_1 = userData(id="1", login_id="alpha", password="alpah1")

# DB 접속 정보
db_host = "localhost"
user = "postgres"
password = "RaiCial"

engine = create_engine(
    f'postgresql+psycopg2://{user}:{password}@{db_host}/test_db'
)
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(user_1)
    session.commit()

with Session(engine) as session:
    statement = select(test).where(test.login_id == "alpha")
    hero = session.exec(statement).first()
    print(hero)
    statement = select(userData).where(userData.login_id == "alpha")
    pain = session.exec(statement).first()
    print(pain)