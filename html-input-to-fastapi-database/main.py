from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

class loginData(BaseModel):
    id: str
    password: str
    sex: str
    age: int
    height: float
    weight: float


@app.get("/")
def get_page(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})

#사용자에게 입력데이터 저장할 수있게게
@app.post("/submit")
async def submit_form(data: loginData):
    #save the data to the database 용한님 refer
    return {"message": "data received!", 
            "data": data}