# -*- coding: utf-8 -*-
import json
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import FastAPI
from fastapi import APIRouter

# DB에 저장할 데이터 모델 정의
class userData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(index=True, unique=True)
    password: str
    gender: int
    age: int
    height: float
    weight: float
    bodyTemperature: float

class userClothes(SqlModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    #의상 종류들 집어넣기 값은 int 또는 bool

class userScore(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    score: int
    note: str

class userFavorite(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    favorite_1: str
    favorite_2: str
    favorite_3: str
    favorite_4: str
    favorite_5: str
    favorite_6: str
    favorite_7: str

# DB 접속 정보
db_host = "localhost"
user = "postgres"
password = "RaiCial"

# data DB에서 모든 사용자 데이터를 JSON 형식으로 내보내는 함수
def export_all_users_to_json():
    with Session(data) as session:
        statement = select(userData)
        results = session.exec(statement).all()
        users_list = [user.dict() for user in results]
        return json.dumps(users_list, ensure_ascii=False, indent=2)
    
# data DB에 사용자 데이터를 추가하는 함수
def add_user(user_info: userData):
    with Session(data) as session:
        session.add(user_info)
        session.commit()
        session.refresh(user_info)
        return user_info
    
# data DB에서 특정 사용자 데이터를 조회하는 함수
def get_user_by_login_id(login_id: str):
    with Session(data) as session:
        statement = select(userData).where(userData.login_id == login_id)
        user = session.exec(statement).first()
        return user
    
# data DB에서 특정 사용자 데이터를 업데이트하는 함수
def update_user(user_info: userData):
    with Session(data) as session:
        session.add(user_info)
        session.commit()
        session.refresh(user_info)
        return user_info
    
# data DB에서 특정 사용자 데이터를 삭제하는 함수
def delete_user_by_login_id(login_id: str):
    with Session(data) as session:
        statement = select(userData).where(userData.login_id == login_id)
        user = session.exec(statement).first()
        if user:
            session.delete(user)
            session.commit()
            return True
        return False
    
# score DB에 사용자 점수를 추가하는 함수
def add_user_score(user_score: userScore):
    with Session(score) as session:
        session.add(user_score)
        session.commit()
        session.refresh(user_score)
        return user_score

# score DB에서 특정 사용자 점수의 평균을 조회하는 함수
def get_average_score():
    with Session(score) as session:
        statement = select(userScore)
        results = session.exec(statement).all()
        if results:
            total_score = sum(user.score for user in results)
            average_score = total_score / len(results)
            return average_score
        return 0
    
# favorite DB에 사용자의 선호도를 추가하는 함수
def add_user_favorite(user_favorite: userFavorite):
    with Session(favorite) as session:
        session.add(user_favorite)
        session.commit()
        session.refresh(user_favorite)
        return user_favorite

# favorite DB에서 선호도가 5개 다 찼을때 비교하여 가장 낮은 선호도를 새로운 선호도로 업데이트하는 함수
def update_user_favorite(login_id: str, new_favorite: str):
    with Session(favorite) as session:
        statement = select(userFavorite).where(userFavorite.login_id == login_id)
        user_favorite = session.exec(statement).first()
        if user_favorite:
            favorites = [user_favorite.favorite_1, user_favorite.favorite_2,
                         user_favorite.favorite_3, user_favorite.favorite_4,
                         user_favorite.favorite_5]
            min_favorite = min(favorites)
            min_index = favorites.index(min_favorite)
            favorites[min_index] = new_favorite
            
            # Update the favorite fields
            user_favorite.favorite_1, user_favorite.favorite_2, \
            user_favorite.favorite_3, user_favorite.favorite_4, \
            user_favorite.favorite_5 = favorites
            
            session.add(user_favorite)
            session.commit()
            return user_favorite
        return None

# favorite DB에서 특정 사용자의 선호도를 반환하는 함수
def get_user_favorite(login_id: str):
    with Session(favorite) as session:
        statement = select(userFavorite).where(userFavorite.login_id == login_id)
        user_favorite = session.exec(statement).first()
        return user_favorite
    
if __name__ == "__main__":
    # DB 접속 및 테이블 생성
    data = create_engine(
        f'postgresql+psycopg2://{user}:{password}@{db_host}/UserData_db'
    )
    SQLModel.metadata.create_all(data)

    score = create_engine( 
        f'postgresql+psycopg2://{user}:{password}@{db_host}/UserScore_db'
    )
    SQLModel.metadata.create_all(score)

    clothes = create_engine(

      f'postgresql+psycopg2://{user}:{password}@{db_host}/UserClothes_db'
    )
    SQLModel.metadata.create_all(clothes)

    favorite = create_engine(
        f'postgresql+psycopg2://{user}:{password}@{db_host}/UserFavorite_db'
    )
    SQLModel.metadata.create_all(favorite)

# DB 오류 출력 코드작성 필요
# DB 옷 데이터 결과물용 DB필요 (이미지, 글 2종 또는 이미지 변환 후 1종 보관)
# DB와 api 로컬에서 연결 실험 후 원격 연결시도
# DB 정렬 함수 추가
# DB 평균값 계산 추가