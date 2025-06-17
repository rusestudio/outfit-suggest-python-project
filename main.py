import base64
import json
import logging as log
import os
from typing import List

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from data_to_be_prompt import clothes_data
from database import (add_user, get_password_by_login_id, get_user_by_login_id,
                      userData)
from llm_model_suggest import main
from prompt import build_prompt
from weather import apiLink


def setup_log():
    log.basicConfig(
        level=log.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            log.FileHandler('server.log'),
            log.StreamHandler()
        ]
    )
setup_log()

logger = log.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

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
    if not data.login_id:
        raise HTTPException(status_code=400, detail="Missing login_id")
    if not data.password:
        raise HTTPException(status_code=400, detail="Missing password")
    password_data = get_password_by_login_id(data.login_id)
    if not password_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    password = json.loads(password_data).get("password")
    if password == data.password:
        return {
            "message": "Login successful!",
            "access_token": "fake-jwt"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

#/index main page 
@app.get("/index")
def get_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class SubmitData(BaseModel):
    when: str
    destination: str
    environment: str

class Location(BaseModel):
    latitude: float
    longitude: float

class SubmitRequest(BaseModel):
    submit_data: SubmitData
    location: Location


# Combined endpoint that handles form submission and gets weather data
@app.post("/submit")
async def submit_form( submit: SubmitRequest, request: Request):
    user_input = {
        "when": submit.submit_data.when,
        "destination": submit.submit_data.destination,
    }
    
    try:
        # Get weather data using location coordinates
        lat = submit.location.latitude
        lon = submit.location.longitude
        print(f"Getting weather for coordinates: {lat},{lon}")
        date, time = apiLink.get_corrent_date_hour_vil()
        day = int(date[7:])
        date_temp = int(user_input["when"][9:])
        delt_date = date_temp - day
        weather_data  = await apiLink.get_weather(lat,lon,delt_date)
        day = str(int(date) + delt_date)
        time = "0000"

        #avg, _,_  = apiLink.get_weather_TMX_TMN(weather_data2,day,time)
        #weather_datad["temperature"] = avg

        user = get_user_by_login_id(userData.login_id)

        # Build prompt with user data, weather data, and clothes data
        suggestions = main(user, weather_data, clothes_data, user_input)

        return templates.TemplateResponse("result.html", {
            "request": request,
            "suggestions": suggestions,
            "weather_data": weather_data,  # Optional: pass weather data to template
            "user_input": user_input,       # Optional: pass user input to template
            "user":user
        })
        
    except Exception as e:
        log.error(f"err: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
   
@app.get("/result", response_class=HTMLResponse)
async def show_result(request: Request):
    suggestions = main()
    return templates.TemplateResponse("result.html", {"request": request, "suggestions": suggestions})