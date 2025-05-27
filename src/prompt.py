import re

#create prompt
def build_prompt(user_data,weather_data, clothes_data,user_preference_dday,user_preference_fday):
        #you are age, sex, height, body weight. //to be change based on user login data
        prompt = f"""
        your are a {user_data['sex']} who is
        {user_data['age']} years old,
        height  {user_data['height']} cm,
        weight {user_data['weight']} kg and
        have sensitive to temperature which if {user_data['body_temp']} is 0 
        consider as normal, else if {user_data['body_temp']} is 1 you feel more cold than the current temperature, 
        else if {user_data['body_temp']} is 2 you feel more hot than the current temperature.

        
        Current weather conditions:
        - Temperature: {weather_data['temperature']}°C
        - Wind: {weather_data['wind']}
        - Rain: {weather_data['rain']}
        - Humidity: {weather_data['humidity']}%
        - Air Pressure: {weather_data['air_pressure']} hPa

        Available clothing options include the following types:
        {', '.join(clothes_data['types'])}

        and the following materials:
        {', '.join(clothes_data['materials'])}

        and also, clothes that have in closet:
        {', '.join(user_data['clothes_info'])}

        Location to wear the outfit would be:
        either on the today {user_preference_dday['location_type']},
        or other day at {user_preference_fday['goals_to_wear']}.


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