import requests
import datetime
import json

# key and url
service_key = ""
sevice_key_de = ""
url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# user data
num_of_rows = 10
base_date = datetime.datetime.now().strftime("%Y%m%d")
pos = [55,127]

# weather format
data_type = "JSON"
page_no = 1

# parameters for requests.get()

params = {
    'serviceKey' : service_key,
    'numOfRows' : num_of_rows,
    'pageNo' : 1,
    'dataType' : data_type,
    'base_date' : base_date,
    'base_time' : '0600',
    'nx' : pos[0],
    'ny' : pos[1]
}

request = requests.get(url,params)