import requests
import datetime
import json
from get_data import *
from typing import Tuple
import os


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
        with open(".key/.servicekey_decode",r):
            service_key = "S1BaX+xBN5BHD/KvjHaEAjAUw0cifZi2CdoDIeShd6bQ+EWcanogJq5s4v5t32PLhSdymB6jglQwMW9+8O1QFw=="
    except Exception as e:
        print(e)
        return None
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
    result = requests.get(url,params)
    if result.ok:
        return result
    else:
        print(f'Fatal! : fail requests (status code : {result.status_code})')
        return result
    return 

def get_weather_auto( day : int = 0 ):
    latlon = get_location()
    pos = latlon_to_grid(latlon)
    
    num_of_rows = 10
    
    date_int = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    
    corrent_time = (date_int%10000)/100
    corrent_time = int(corrent_time - ((corrent_time-2)%3))%24
    corrent_time = f'{corrent_time:02d}00'
    corrent_date = date_int/10000
    data_type = "JSON"

    page_no = 1
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