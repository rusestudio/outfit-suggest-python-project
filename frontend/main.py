from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel, Session, create_engine,select
from dummy_result_data import Result
import base64
from typing import List

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

#dummy database set to be implement  by 용한님
DATABASE_URL ="sqlite:///.databasetest.db"
engine = create_engine(DATABASE_URL, echo=True)

#dummy pydantic data
#will be implement as sqlmodel by 용한님님
class loginData(BaseModel):
    user_id: str
    password: str

class SignUp(BaseModel):
    user_id: str
    password: str
    sex: str
    age: int
    height: float
    weight: float
    body_temp: int
    clothes: List[str]

class FormData(BaseModel):
    when: str
    destination: str
    place: str

@app.get("/")
def get_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request":request})

#사용자에게 입력데이터 database으로 저장할 수있게게
@app.post("/signup")
async def submit_form(data: SignUp):
    #save the data to the database 용한님 refer
    print("Received signup data:", data)
    return {"message": "data received!", 
            "data": data} #sign up data

#/login to get to login page from sign up
@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


#to login and check data from db
@app.post("/login")
async def post_login(data: loginData):
    if data.user_id == "testuser" and data.password == "1234":   #to fetch data from db
        return {"message": "Login successful!", "access_token": "fake-jwt"}
    else:
        return {"detail": "Invalid credentials"}, 401

#/index main page 
@app.get("/index")
def get_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 사용자 입력 처리
@app.post("/submit")
async def submit_form(data: FormData):
    # 여기에 DB 저장 로직 등 추가 가능
    return {
        "message": "데이터를 성공적으로 받았습니다!",
        "data": data  #user data to send to db
    }

#create db tables
@app.get("/result")
def get_result():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(Result)).first():
            session.add_all([
                #dummy data to be implement  by 용한님
               # Option 1: Fill all fields in dummy data
                Result(explain1="abc", explain2="def", explain3="ghi", 
                       img1="img/img1.png", img2="img/img2.png", img3="img/img3.png")
            ])
            session.commit()

def get_session():
    with Session(engine) as session:
        yield session

def image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

#render html user page to show 가져온 데이터 to html
@app.get("/result", response_class=HTMLResponse)
def read_result(request: Request, session: Session = Depends(get_session)):
    results = session.exec(select(Result)).all()

      # Convert image paths to base64
    for result in results:
        if result.img1:
            result.img1 = image_to_base64(result.img1)
        if result.img2:
            result.img2 = image_to_base64(result.img2)
        if result.img3:
            result.img3 = image_to_base64(result.img3)

    return templates.TemplateResponse("result.html", {"request": request, "results":results })