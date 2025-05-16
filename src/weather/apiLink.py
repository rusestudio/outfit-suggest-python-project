import requests
import datetime
import json
from get_data import get_location
from typing import Tuple

# get weather from API
def get_weather_manual( pos : Tuple[float,float], date : int, time : int 
                       , number_of_rows : int = 10, page_number : int = 1 
                       , data_type : str = 'JSON', day : int = 0 ):
    # key and url
    with open(".key/.sevicekey_decode",'r') as f:
        service_key = f.read()
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
 
    params = {
        'serviceKey' : service_key,
        'numOfRows' : number_of_rows,
        'pageNo' : page_number,
        'dataType' : data_type,
        'base_date' : date + day,
        'base_time' : time,
        'nx' : pos[0],
        'ny' : pos[1]
    }

    return requests.get(url,params)

def get_weather_auto( day : int = 0 ):
    pos = get_location()
    
    num_of_rows = 10
    
    date_int = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    
    corrent_time = (date_int%10000)/100
    corrent_time = int(corrent_time - ((corrent_time-2)%3))%24
    corrent_time = f'{corrent_time:02d}00'
    
    data_type = "JSON"

    page_no = 1
    return get_weather_manual( pos, date_int, corrent_time )

if __name__ == __main__:
    get_weather_auto()