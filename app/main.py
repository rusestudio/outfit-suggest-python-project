from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from .weather import apiLink

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 클라이언트에서 받을 위치 정보 모델
class Location(BaseModel):
    latitude: float
    longitude: float

# get weather
@app.post("/weather")
async def get_weather(location: Location):
    lat = location.latitude
    lon = location.longitude
    print(f"{lat},{lon}")
    weather_data = apiLink.get_weather_auto("20250527","0800")
    weather_data = apiLink.parse_weather_items(weather_data)
    return weather_data

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}) 
