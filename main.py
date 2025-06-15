from fastapi import FastAPI, Request, Form, HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import userData, add_user, get_user_by_login_id, get_password_by_login_id
from llm_model_suggest import main 
from data_to_be_prompt import weather_data, clothes_data
from prompt import build_prompt
import os
import logging as log
from fastapi.staticfiles import StaticFiles

import base64
from typing import List
import json

from .weather import apiLink

def setup_log():
    log.basicConfig(
        level=log.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            log.FileHandler('server.log'),
            log.StreamHandler()
        ]
    )


app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

#weather
logger = log.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

class SubmitRequest(BaseModel):
    when: str
    destination: str


@app.get("/")
def get_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request":request})

#사용자에게 입력데이터 database으로 저장할 수있게게              #--send to database user sign up
@app.post("/signup")
async def submit_form(data: userData):
    #save the data to the database 용한님 refer 
    add_user(data)
    print("Received signup data:", data)
    return {"message": "data received!", 
            "data": data} #sign up data

#/login to get to login page from sign up
@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


#to login and check data from db                          #--send to database user sign up
@app.post("/login")
async def post_login(data: userData):
    if(data.login_id != None or data.password != None):
        data.login_id = str(data.login_id)
        data.password = str(data.password)
        password_data = get_password_by_login_id(data.login_id)
        password = json.loads(password_data).get("password")
    elif(data.login_id == None or data.password == None):
        data.password = "1234"
        password = "1234"
    else:
        return {"detail": "Invalid credentials", "message": "!"}, 401
    if password == data.password: #to fetch data from db
        return {"message": "Login successful!", "access_token": "fake-jwt"}
    else:
        return {"detail": "Invalid credentials", "message": "!"}, 401
    
#/index main page 
@app.get("/index")
def get_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


logger = log.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 클라이언트에서 받을 위치 정보 모델
class Location(BaseModel):
    latitude: float
    longitude: float

# Combined endpoint that handles form submission and gets weather data
@app.post("/submit")
async def submit_form(submit_data: SubmitRequest, request: Request, location: Location):
    user_input = {
        "when": submit_data.when,
        "destination": submit_data.destination,
    }
    
    try:
        # Get weather data using location coordinates
        lat = location.latitude
        lon = location.longitude
        print(f"Getting weather for coordinates: {lat},{lon}")
        

        # Build prompt with user data, weather data, and clothes data
        prompt = build_prompt(userData, weather_data, clothes_data, user_input)
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "prompt": prompt,
            "weather_data": weather_data,  # Optional: pass weather data to template
            "user_input": user_input       # Optional: pass user input to template
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

   
@app.get("/result", response_class=HTMLResponse)
async def show_result(request: Request):
    suggestions = main()
    return templates.TemplateResponse("result.html", {"request": request, "suggestions": suggestions})