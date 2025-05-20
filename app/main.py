from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

import weather.apiLink as apiLink

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 클라이언트에서 받을 위치 정보 모델
class Location(BaseModel):
    latitude: float
    longitude: float

# 예시: 위치 기반 날씨 조회 함수 (임시)
def your_weather_func(lat: float, lon: float):
    # 실제 구현 대신 샘플 데이터 반환
    return {
        "latitude": lat,
        "longitude": lon,
        "weather": "맑음",
        "temperature": "25도"
    }

@app.post("/weather")
async def get_weather(location: Location):
    lat = location.latitude
    lon = location.longitude
    weather_data = apiLink.get_weather_manual([lat,lon],20250520,2126)
    return weather_data

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}) 
