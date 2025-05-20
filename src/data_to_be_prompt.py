import json


#weather data, dummy test data
weather_data ={
    "temperature": 19,       # Celsius
    "wind": "4",      # or value in km/h
    "rain": "heavy rain",
    "humidity": 77,
    "air_pressure": 1011,
    "location_type": "outdoor",  # or 'indoor'
}

#dummy user data
user_data = {
    "sex": "male",
    "age": 10,
    "height": 140,
    "weight": 40,
}

#dummy user input data from html
#do we need? KIV
#user_preference = {}

#clothes data
# Load clothes data from files
with open("../clothes_data/all_clothing_types.json", "r") as f1:
    clothing_types = json.load(f1)

with open("../clothes_data/all_material_data.json", "r") as f2:
    material_data = json.load(f2)

# Combine into a structured dictionary
clothes_data = {
    "types": clothing_types,
    "materials": material_data
}
