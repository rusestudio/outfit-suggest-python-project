from fastapi import FastAPI, Request, Form, HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import userData, add_user, get_user_by_login_id
from llm_model_suggest import main 
from data_to_be_prompt import weather_data, clothes_data
from prompt import build_prompt
import os
import logging as log
from fastapi.staticfiles import StaticFiles

import base64
from typing import List

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

#weather
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
    user = get_user_by_login_id(data.login_id)
    if user and user.password == data.password: #to fetch data from db
        return {"message": "Login successful!", "access_token": "fake-jwt"}
    else:
        return {"detail": "Invalid credentials"}, 401

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

# get weather
@app.post("/weather")
async def get_weather(location: Location):
    lat = location.latitude
    lon = location.longitude
    print(f"{lat},{lon}")
    
    return weather_data

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

        weather_datad = {
            "temperature": 19,  # Celsius
            "wind": "5",  # or value in km/h
            "rain": "no rain", #%
            "humidity": 71,
        }   
        
        date, time = apiLink.get_corrent_date_hour_vil()
        day = int(date[7:])
        date_temp = int(user_input["when"][9:])
        log.info(f"date_temp = {date_temp},{day}")
        delt_date = date_temp - day
        log.warning(f"sdaf{delt_date}")
        weather_data2 = await apiLink.get_weather(lat,lon,delt_date)

        log.info(weather_data2)
        day = str(int(date) + delt_date)
        time = "0000"

        avg, _,_  = apiLink.get_weather_TMX_TMN(weather_data2,day,time)
        weather_datad["temperature"] = avg
        
        user = get_user_by_login_id(userData.login_id)
        # Build prompt with user data, weather data, and clothes data
        suggestions = main(user, weather_datad, clothes_data, user_input)

        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "suggestions": suggestions,
            "weather_data": weather_datad,  # Optional: pass weather data to template
            "user_input": user_input       # Optional: pass user input to template
        })
        
    except Exception as e:
        log.error(f"err: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


#create db tables
#@app.get("/result", response_class=HTMLResponse)
#def read_result(request: Request, session: Session = Depends(lambda: Session(engine))):
 #   SQLModel.metadata.create_all(engine)
    
    #show explaina1,2,3
    #show img1,2,3
  #  with session:
   #     results = session.exec(select(resultImage)).all()
   #     explain_result = session.exec(select(explain_data.explain)).all()

        # Convert images to base64
   #     for result in results:
   #       result.image = f"data:image/png;base64,{result.image}"
    #      explain_result = f"{result.explain_result}"

   
@app.get("/result", response_class=HTMLResponse)
async def show_result(request: Request):
    suggestions = main()
    return templates.TemplateResponse("result.html", {"request": request, "suggestions": suggestions})