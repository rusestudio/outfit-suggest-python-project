from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel, Session, create_engine,select
from dummy_database_model import User


#dummy database set to be implement  by 용한님
DATABASE_URL ="sqlite:///.databasetest.db"
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


#create db tables
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(User)).first():
            session.add_all([
                #dummy data to be implement  by 용한님
                User(password="123", sex="M", age=25, height=175.5, weight=70.2),
                User(password="456", sex="F", age=30, height=160.0, weight=55.0),
            ])
            session.commit()

def get_session():
    with Session(engine) as session:
        yield session


#@app.get("/")
#def get_page(request: Request):
    #return templates.TemplateResponse("user.html", {"request":request})

#render html user page to show 가져온 데이터 to html
@app.get("/", response_class=HTMLResponse)
def read_users(request: Request, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return templates.TemplateResponse("user.html", {"request": request, "users":users })