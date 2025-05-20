import re

#create prompt
def build_prompt(user_data,weather_data, clothes_data):
        #you are age, sex, height, body weight. //to be change based on user login data
        prompt = f"""
        your are a {user_data['sex']} who is
        {user_data['age']} years old,
        height  {user_data['height']} cm and
        weight {user_data['weight']} kg.
        
        Current weather conditions:
        - Temperature: {weather_data['temperature']}°C
        - Wind: {weather_data['wind']}
        - Rain: {weather_data['rain']}
        - Humidity: {weather_data['humidity']}%
        - Air Pressure: {weather_data['air_pressure']} hPa
        - Location: {weather_data['location_type']}

        Available clothing options include the following types:
        {', '.join(clothes_data['types'])}

        and the following materials:
        {', '.join(clothes_data['materials'])}

        Please suggest 3 outfits suitable for the conditions and location.
        for each outfit, provide:
        -suggestions materials,types, and colors in 3 points
        -simple explain why it fits the weather and location in one sentence
        -a short prompt for an image generation model to draw the outfit.

        Respond in clear text.
        """

        return prompt


#def return image prompt only
def image_prompt(result):
     #get only image prompt
     imageprompts = re.findall(r'\*\*Image Prompt:\*\*\s*"([^"]+)"', result)
    
    #fill  prompt
     throwback = "fashion outfit suitable for current weather and location"
     while len(imageprompts) < 3:
        imageprompts.append(throwback)
    
     return imageprompts[:3]