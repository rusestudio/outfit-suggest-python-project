from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from typing import List, Optional

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

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

