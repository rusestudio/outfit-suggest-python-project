import json

# weather data, dummy test data
weather_data = {
    "temperature": 30,  # Celsius
    "wind": "2",  # or value in km/h
    "rain": "no rain", #%
    "humidity": 30,
    "air_pressure": 1017,
}

# dummy user data
user_data = {
    "sex": "male",
    "age": 20,
    "height": 160,
    "weight": 60,
    "body_temp": 2, #normal=0 #추의=1 #더의=2
    "clothes_info": "t-shirt"
}

user_preference_dday = {
   "location_type": "",  # outdoor or 'indoor'실내 이용목적
}

user_preference_fday={
    "goals_to_wear": "beach vacation" #이용목적 예:바다여행
}

# clothes data
# Load clothes data from files
with open("../clothes_data/all_clothing_types.json", "r") as f1:
    clothing_types = json.load(f1)

with open("../clothes_data/all_material_data.json", "r") as f2:
    material_data = json.load(f2)

# Combine into a structured dictionary
clothes_data = {"types": clothing_types, "materials": material_data}
