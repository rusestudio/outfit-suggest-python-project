import requests
from requests.exceptions import HTTPError
import logging as log
from datetime import datetime, timedelta
from typing import Dict
import json

from config import SERVICE_KEY, VWORLD_KEY
if __name__ == "__main__":
    import get_data
else:
    from . import get_data

class APIResponseError(Exception):
    def __init__(self, name, code, message):
        super().__init__(f"API({name}) Error Code {code}: {message}")
        self.name = name
        self.code = code
        self.message = message

def fetch_address_from_latlon( lat : float , lon : float ):
    apiurl = "https://api.vworld.kr/req/address?"	
    params = {	
        "service": "address",	
        "request": "getaddress",	
        "crs": "epsg:4326",	
        "point": f"{lon},{lat}",	
        "format": "json",	
        "errorFormat" : "json",
        "type": "ROAD",	
        "key": VWORLD_KEY	
    }	
    response = requests.get(apiurl, params=params)	
    if response.status_code != 200:
        print("wow")
    return response.json()

def parse_address_from_latlon(result:json):
    status = result["status"]
    if status != "OK": 
        error = result["error"]
        if status == "NOT_FOUND":
            APIResponseError("VWorld", error["code"], "Can not find Data")
        else:
            APIResponseError("VWorld", error["code"], error["message"])
            

def get_address_from_latlon( lat: float , lon : float ):
    try:
        return fetch_address_from_latlon(lat,lon)
    except Exception as e:
        log.critical(f"FUCK : {e}")

def logging_api_response_error(error:APIResponseError):
    '''
    function for APIResponseError logging

    Params:
        error(APIResponseError): error that will be handled
    
    Return:
        errorcode(str): It can change to int
    '''
    match error.code:
        case "01":
            log.error(f"Application_error: {error}")
        case "02":
            log.error(f"DB_error: {error}")
        case "03":
            log.warning(f"NODATA_ERROR: {error}")
        case "04":
            log.error(f"HTTP_ERROR: {error}")
        case "05":
            log.critical(f"SERVICETIME_OUT: {error}")
        case "10":
            log.warning(f"INVALID_REQUEST_PARAMETER_ERROR: {error}")
        case "11":
            log.warning(f"NO_MANDATORY_REQUEST_PARAMETERS_ERROR: {error}")
        case "12":
            log.warning(f"NO_OPENAPI_SERVICE_ERROR: {error}")
        case "20":
            log.error(f"SERVICE_ACCESS_DENIED_ERROR: {error}")
        case "21":
            log.warning(f"TEMPORARILY_DISABLE_THE_SERVICEKEY_ERROR: {error}")
        case "22":
            log.warning(f"LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR: {error}")
        case "30":
            log.critical(f"SERVICE_KEY_IS_NOT_REGISTERED_ERROR: {error}")
        case "31":
            log.critical(f"DEADLINE_HAS_EXPIRED_ERROR: {error}")
        case "32":
            log.critical(f"UNREGISTERED_IP_ERROR: {error}")
        case "33":
            log.critical(f"UNSIGNED_CALL_ERROR: {error}")
        case _:
            log.error(f"UNKNOWN_ERROR: {error}")

def get_date_time(delta_time : int = 0):
    dt = datetime.now() + timedelta(days=delta_time)
    hour = dt.hour - (dt.hour - 2) % 3
    days_delta = hour // 24
    hour = (hour + 24) % 24
    dt = dt + timedelta(days=days_delta)
    base_time = dt.replace(hour=hour, minute=10, second=0, microsecond=0)
    date = base_time.strftime("%Y%m%d")
    time = base_time.strftime("%H%M")
    return date, time

def recive_weather_info( params : Dict, url:str, timeout: int = 1):
    """
    recive weather data

    Args:
        params (Dict): parameters to send to the KMA API
        url (str): KMA service category
        timeout (int): time out flag
    
    Returns: 
        Json
    
    Raises:
        HTTPError: If API Response is not vaild value
        APIResponseError: If API response data is not vaild value
        Exception: If an unknown error occurs
    """
    print(params)
    try:
        result = requests.get("http://apis.data.go.kr/1360000/"+url,params, timeout=1)
        result.raise_for_status()
        result = result.json()

        head = result.get("response",{}).get("header",{})
        result_code = head.get("resultCode")
        
        if result_code != "00":
            result_msg = head.get("resultMsg") 
            raise APIResponseError("KMA",result_code, result_msg)
    except HTTPError as e:
        log.error(f"HTTPError : {e}")
        raise
    except APIResponseError as e:
        log.error(f"APIResponseError : {e}")
        raise
    except Exception as e:
        log.error(f"UnexpectedError : {e}")
        raise
    return result

def parse_weather_Mid_items( response ) :
    items = response['response']['body']['items']['item']
    result = {}
    
    for day in range(4,11):
        day_key = f"{day}"
        day_info = {}

        if day < 7:
            rn_am = items.get(f'rnSt{day}AM') 
            rn_pm = items.get(f'rnSt{day}PM')

            wf_am = items.get(f'wf{day}AM')
            wf_pm = items.get(f'wf{day}PM')
            
            day_info['rnst'] = {'am': rn_am, 'pm' : rn_pm}
            day_info['wf'] = {'am': wf_am, 'pm' : wf_pm}
        else:
            rn = items.get(f'rnSt{day}')
            wf = items.get(f'wf{day}')
            day_info['rnst'] = rn
            day_info['wf'] = wf
        result[day_key] = day_info

    return result

def parse_weather_vil_items(response):
    items = response['response']['body']['items']['item']
    result = {}
    for item in items:
        category = item['category']
        val = item['fcstValue']
        result[category] = val
    return result

def fetch_weather_Mid( regid : str, date : str , time : str
                       , number_of_rows : int = 10, page_number : int = 1 ): 
    """
    Get Middle term weather data

    Args:
        regid (str): location number
        date (str): date
        time (str): HHmm ( H: hour, m: minute)
        number_of_rows (int): rows of response result
        page_number (int): page :)

    Returns :
        JSON
    
    Raises:
        HTTPError: If API Response is not vaild value
        APIResponseError: If API response data is not vaild value
        Exception: If an unknown error occurs
        
    """
    url = "VilageFcstInfoService_2.0/getVilageFcst"
 
    # Even if you change the variable,
    #   DO NOT CHANGE THE FORMAT BELOW
    params = {
        'serviceKey' : SERVICE_KEY,
        'numOfRows' : number_of_rows,
        'pageNo' : page_number,
        'dataType' : 'JSON',
        'regid' : regid,
        'tmFc' : time
    }
    try:
        return recive_weather_info(params,url)
    except HTTPError as e:
        log.error(f"HTTPError : {e}")
        raise
    except APIResponseError as e:
        log.error(f"APIResponseError : {e}")
        raise
    except Exception as e:
        log.error(f"UnexpectedError : {e}")
        raise

def fetch_weather_Vil( xpos : int, ypos : int, date : str, time : str 
                       , number_of_rows : int = 10, page_number : int = 1 ): 
    """
    Get vilage weather data

    Args:
        xpos (float): x KMA grid coordinate NOT latitude
        ypos (float): y KMA grid coordinate NOT longitude
        date (str): YYYYMMDD ( Y: year, M: month, D: day )
        time (str): HHmm ( H: hour, m: minute)
        number_of_rows (int): rows of response result
        page_number (int): page :)
        day (int): Get the weather for this number of days in the past   

    Returns :
        JSON format
    
    Raises:
        APIResponseError : If api sends an invaild value.
        
    """ 
    url = "VilageFcstInfoService_2.0/getVilageFcst"
 
    # Even if you change the variable,
    #    DO NOT CHANGE THE FORMAT BELOW
    params = {
        'serviceKey' : SERVICE_KEY,
        'numOfRows' : number_of_rows,
        'pageNo' : page_number,
        'dataType' : 'JSON',
        'base_date' : date,
        'base_time' : time,
        'nx' : xpos,
        'ny' : ypos
    }

    try:
        return recive_weather_info(params,url)
    except HTTPError as e:
        raise
    except APIResponseError as e:
        logging_api_response_error(e)
        raise
    except RecursionError as e:
        raise

def get_weather_vil( lat : float , lon : float , delt_day : int = 0 ) -> Dict:
    '''
    Get vilage fcst weather

    Param:
        day : Get the weather for this number of days
            in the past 

        Dictionary : 
            key
    '''
    xgrid, ygrid = get_data.combert_latlon_to_grid(lat,lon)
    
    day, time = get_date_time(delt_day)

    try: 
        result = fetch_weather_Vil( xgrid, ygrid, day, time)
    except HTTPError as e:
        raise
    except APIResponseError as e:
        raise
    except RecursionError as e:
        raise   
    return result

def get_weather_Mid( lat : float , lon : float , day : int = 0 ) -> Dict:
    '''
    Get vilage fcst weather

    Param:
        day : Get the weather for this number of days
            in the past 

        Dictionary : 
            key
    '''
    xgrid, ygrid = get_data.combert_latlon_to_grid(lat,lon)
    
    dt = datetime.now() + timedelta(days=day)
    hour = dt.hour - (dt.hour - 2) % 3
    hour = (hour + 24) % 24
    dt = dt + timedelta(days=(hour//24))
    base_time = dt.replace(hour=hour, minute=10, second=0, microsecond=0)
    corrent_date = base_time.strftime("%Y%m%d")
    corrent_time = base_time.strftime("%H%M")

    try: 
        result = fetch_weather_Mid( xgrid, ygrid , corrent_date, corrent_time )
    except HTTPError as e:
        raise
    except APIResponseError as e:
        logging_api_response_error(e)
        raise
    except RecursionError as e:
        raise   
    return result
     
def get_weather( lat : float , lon : float , date : int):
    '''
    get weather
    '''
    if SERVICE_KEY == None:
        raise FileNotFoundError

    if date <= 3:
        result = get_weather_vil(lat, lon, date)
        result = parse_weather_vil_items(result)
    elif date <= 7:
        result = get_weather_Mid(lat, lon, date)
        result = parse_weather_Mid_items(result)
    elif date <=10:
        result = get_weather_Mid(lat, lon, date)
    else:
        pass

    return result

if __name__ == "__main__":
    lat, lon= 37.564214, 127.001699
    print(f"lat : {lat}")
    print(f"lon : {lon}")
    print(f"================================")
    xpos, ypos = get_data.combert_latlon_to_grid(lat, lon)
    result = fetch_weather_Vil(xpos,ypos,"20250606","1110", 1000,0)
    result = parse_weather_vil_items(result)
    print(f"result : {result}")