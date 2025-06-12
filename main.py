from fastapi import FastAPI, Request, Form, HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import userData, add_user, get_user_by_login_id
from llm_model_suggest import main 
from data_to_be_prompt import weather_data, clothes_data
from prompt import build_prompt

import base64
from typing import List


app = FastAPI()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

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
    user = get_user_by_login_id(data.login_id)
    if user and user.password == data.password: #to fetch data from db
        return {"message": "Login successful!", "access_token": "fake-jwt"}
    else:
        return {"detail": "Invalid credentials"}, 401

#/index main page 
@app.get("/index")
def get_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 사용자 입력 처리
@app.post("/submit")                                   
async def submit_form(submit_data: SubmitRequest, request: Request):
    user_input = {
        "when": submit_data.when,
        "destination": submit_data.destination,
    }
    
    try:
        prompt = build_prompt(userData, weather_data, clothes_data, user_input)
        return templates.TemplateResponse("result.html", {
            "request": request, 
            "prompt": prompt
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


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