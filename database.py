# -*- coding: utf-8 -*-
import json
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi import FastAPI
from fastapi import APIRouter

# DB에 저장할 데이터 모델 정의 | # Define the data model to be stored in the DB
class userData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(index=True, unique=True)
    password: str
    gender: str
    age: int
    height: float
    weight: float
    #bodyTemperature: int

# 의상 데이터 모델 정의 | # Define the clothing data model
class userClothes(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    clothes: str  # 의상 데이터는 문자열로 저장 (예: "(1, 1), (2, 2), ...") | # Clothing data is stored as a string (e.g., "(1, 1), (2, 2), ...")

# 평가 데이터 모델 정의 | # Define the score data model
class userScore(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(index=True, unique=True)
    score: int

# 선호도 데이터 모델 정의 | # Define the preference data model
class userFavorite(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login_id: str = Field(index=True, unique=True)
    favorite_1: str
    favorite_2: str
    favorite_3: str
    favorite_4: str
    favorite_5: str

# 이미지 데이터 모델 정의 | # Define the image data model
class resultImage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: str  # 이미지 데이터는 문자열로 저장 (예: base64 인코딩된 이미지) | # Image data is stored as a string (e.g., base64 encoded image)
    times: int  # 이미지가 생성된 횟차 | # The number of times the image was generated
    tag: str  # 이미지에 대한 태그 | # Tag for the image

# DB 접속 정보 | # DB connection information
db_host = "59.30.158.50"
user = "postgres"
password = "RaiCial"

# DB를 정렬하는 함수 | # Function to sort the DB
def sort_db(db_category: str, db_name: str, column_name: str):
    with Session(db_category) as session:
        statement = select(SQLModel.metadata.tables[db_name]).order_by(column_name)
        results = session.exec(statement).all()
        return results

# data DB에서 모든 사용자 데이터를 JSON 형식으로 내보내는 함수 | # Function to export all user data from the data DB in JSON format
def export_all_users_to_json():
    with Session(data) as session:
        statement = select(userData)
        results = session.exec(statement).all()
        users_list = [user.dict() for user in results]
        return json.dumps(users_list, ensure_ascii=False, indent=2)
    
# data DB에 사용자 데이터를 추가하는 함수 | # Function to add user data to the data DB
def add_user(user_info: userData):
    with Session(data) as session:
        session.add(user_info)
        session.commit()
        session.refresh(user_info)
        return user_info
    
# data DB에서 특정 사용자 데이터를 조회하는 함수 | # Function to retrieve specific user data from the data DB
def get_user_by_login_id(login_id: str):
    with Session(data) as session:
        statement = select(userData).where(userData.login_id == login_id)
        user = session.exec(statement).first()
        return user
    
# data DB에서 특정 사용자 데이터를 업데이트하는 함수 | # Function to update specific user data in the data DB
def update_user(user_info: userData):
    with Session(data) as session:
        session.add(user_info)
        session.commit()
        session.refresh(user_info)
        return user_info
    
# data DB에서 특정 사용자 데이터를 삭제하는 함수 | # Function to delete specific user data from the data DB
def delete_user_by_login_id(login_id: str):
    with Session(data) as session:
        statement = select(userData).where(userData.login_id == login_id)
        user = session.exec(statement).first()
        if user:
            session.delete(user)
            session.commit()
            return True
        return False
    
# score DB에 사용자 점수를 추가하는 함수 | # Function to add user score to the score DB
def add_user_score(user_score: userScore):
    with Session(score) as session:
        session.add(user_score)
        session.commit()
        session.refresh(user_score)
        return user_score

# score DB에서 특정 사용자 점수의 평균을 조회하는 함수 | # Function to retrieve the average score of a specific user from the score DB
def get_average_score():
    with Session(score) as session:
        statement = select(userScore)
        results = session.exec(statement).all()
        if results:
            total_score = sum(user.score for user in results)
            average_score = total_score / len(results)
            return average_score
        return 0
    
# favorite DB에 사용자의 선호도를 추가하는 함수 | # Function to add user preference to the favorite DB
def add_user_favorite(user_favorite: userFavorite):
    with Session(favorite) as session:
        session.add(user_favorite)
        session.commit()
        session.refresh(user_favorite)
        return user_favorite

# favorite DB에서 선호도가 5개 다 찼을때 비교하여 가장 낮은 선호도를 새로운 선호도로 업데이트하는 함수 | # Function to update user preference in the favorite DB when all 5 preferences are filled
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

# favorite DB에서 특정 사용자의 선호도를 반환하는 함수 | # Function to return user preference from the favorite DB
def get_user_favorite(login_id: str):
    with Session(favorite) as session:
        statement = select(userFavorite).where(userFavorite.login_id == login_id)
        user_favorite = session.exec(statement).first()
        return user_favorite
    
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

image = create_engine(
    f'postgresql+psycopg2://{user}:{password}@{db_host}/ResultImage_db'
)
SQLModel.metadata.create_all(image)

    
if __name__ == "__main__":
    print("Server is running...")

# DB 연결 오류 발생시 예외 처리 코드 | # Exception handling code for DB connection errors
try:
    data.connect()
    score.connect()
    clothes.connect()
    favorite.connect()
except Exception as e:
    print(f"DB connection error: {e}")
    exit(1)

    favorite = create_engine(
        f'postgresql+psycopg2://{user}:{password}@{db_host}/UserFavorite_db'
    )
    SQLModel.metadata.create_all(favorite)
# 받은 이미지를 Base64로 인코딩하는 함수 | # Function to encode the received image to Base64
def encode_image_to_base64(image_path: str) -> str:
    import base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

# 받은 이미지를 Base64로 인코딩 한 것을 image DB에 다른 정보와 함께 넣는 함수 | # Function to add the Base64 encoded image to the image DB along with other information
def add_image_to_db(image_data: str, times: int, tag: str):
    with Session(image) as session:
        new_image = resultImage(image=image_data, times=times, tag=tag)
        session.add(new_image)
        session.commit()
        session.refresh(new_image)
        return new_image
    
# DB에서 특정 이미지 데이터를 조회하는 함수 | # Function to retrieve specific image data from the image DB
def get_image_by_tag(tag: str):
    with Session(image) as session:
        statement = select(resultImage).where(resultImage.tag == tag)
        image_data = session.exec(statement).first()
        return image_data

# DB에서 조회한 이미지 데이터를 Base64로 디코딩하는 함수 | # Function to decode the retrieved image data from the DB to Base64
def decode_image_from_base64(encoded_image: str) -> bytes:
    import base64
    return base64.b64decode(encoded_image.encode('utf-8'))

# 디코딩한 이미지와 다른 정보를 함께 반환하는 함수 | # Function to return the decoded image along with other information
def get_decoded_image_with_info(tag: str):
    image_data = get_image_by_tag(tag)
    if image_data:
        decoded_image = decode_image_from_base64(image_data.image)
        return {
            "image": decoded_image,
            "times": image_data.times,
            "tag": image_data.tag
        }
    return None

# TODO

# DB 옷 데이터 결과물용 DB필요 (이미지, 글 2종 또는 이미지 변환 후 1종 보관) -완-
# DB와 api 로컬에서 연결 실험 후 원격 연결시도 -성공-
# DB 정렬 함수 추가 -완-
# DB 평균값 계산 추가 -미완-
# 나머지는 화요일 회의 후 추가적인 의견수렴
