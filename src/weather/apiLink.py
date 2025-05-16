import requests
import datetime
import json
from get_data import *
from typing import Tuple

def get_weather_manual( pos : Tuple[int,int], date : int, time : int 
                       , number_of_rows : int = 10, page_number : int = 1 
                       , data_type : str = 'JSON', day : int = 0 ): 
    """
    Get weather data

    Args:
        pos : Tuple[x cordinate, y cordinate]
            ATTANTION! x, y cordinate are NOT latitude and longitude.

        date : YYYYMMDD
            Y : Year
            M : Month
            D : Day

        time : HHmm
            H : Hour
            m : Min

        number_of_rows : rows when response

        page_number : page :)

        data_type : XML or JSON

        day : Get the weather for this number of days
            in the past   
    """
    try:
        with open("src\weather\.key\.servicekey_decode",'r') as f:
            service_key = f.read()
    except Exception as e:
        print(e)
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
 
    '''
    Even if you change the variable,
        DO NOT CHANGE THE FORMAT BELOW
    '''
    params = {
        'serviceKey' : service_key,
        'numOfRows' : number_of_rows,
        'pageNo' : page_number,
        'dataType' : data_type,
        'base_date' : int(date) + day,
        'base_time' : time,
        'nx' : pos[0],
        'ny' : pos[1]
    }
    print(params)
    result = requests.get(url,params)
    if result.ok:
        return result
    else:
        print(f'Fatal! : fail requests (status code : {result.status_code})')
        return result

def get_weather_auto( day : int = 0 ):
    '''
    Get weather easier

    Param:
        day : Get the weather for this number of days
            in the past 
    '''
    latlon = get_location()
    pos = latlon_to_grid(latlon)
    
    date_int = int((datetime.datetime.now() + datetime.timedelta(days=day)).strftime("%Y%m%d%H%M"))

    # It works!
    # may be... 
    # It does not work
    #   when the years change every year.
    # someone will be fix it :)
    corrent_time = (date_int%10000)/100 # get hour and min
    
    # It makes 2,5,8,11,14,17,20,23
    corrent_time = int(corrent_time - ((corrent_time-2)%3))%24
    
    # It makes 02,05,08,11,14,17,20,23
    corrent_time = f'{corrent_time:02d}00'
    
    # Think about it on your own
    # I don't want to comment >:(
    corrent_date = date_int/10000

    return get_weather_manual( pos, corrent_date, corrent_time )

def response_to_json(response):
    result = response.json()
    return result['response']['body']['items']['item']

def parse_weather_items(response):
    items = response_to_json(response)
    result = {}
    for item in items:
        category = item['category']
        val = item['fcstValue']
        result[category] = val
    return result

if __name__ == "__main__":
    val = get_weather_auto()
    print(val)
    print(parse_weather_items(val))