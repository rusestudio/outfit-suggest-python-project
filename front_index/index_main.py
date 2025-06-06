from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

app = FastAPI()

# HTML 템플릿 디렉터리
templates = Jinja2Templates(directory="templates")

class FormData(BaseModel):
    when: str
    destination: str
    place: str

# 루트 페이지 제공
@app.get("/")
def get_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 사용자 입력 처리
@app.post("/submit")
async def submit_form(data: FormData):
    # 여기에 DB 저장 로직 등 추가 가능
    return {
        "message": "데이터를 성공적으로 받았습니다!",
        "data": data.dict()
    }