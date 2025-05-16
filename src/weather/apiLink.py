import requests
import datetime
import json
from typing import List

# get weather from API
def get_weather( day : int, time : int, pos : List[int,int]) -> List:
    # key and url
    with open(".key/.sevicekey_decode",'r') as f:
        service_key = f.read()
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

    # user data
    num_of_rows = 10
    date_int = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    corrent_time = (date_int%10000)/100
    corrent_time = int(corrent_time - ((corrent_time-2)%3))%24
    corrent_time = f'{corrent_time:02d}00'

    # weather format
    data_type = "JSON"
    page_no = 1

    # parameters for requests.get()
    params = {
        'serviceKey' : service_key,
        'numOfRows' : num_of_rows,
        'pageNo' : 1,
        'dataType' : data_type,
        'base_date' : int(date_int/10000) + day,
        'base_time' : corrent_time,
        'nx' : pos[0],
        'ny' : pos[1]
    }
    request = requests.get(url,params)