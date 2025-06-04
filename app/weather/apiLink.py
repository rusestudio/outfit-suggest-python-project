import requests
from requests.exceptions import HTTPError
import logging as log
import datetime
from typing import Dict
import json

from config import SERVICE_KEY
from . import get_data

class APIResponseError(Exception):
    def __init__(self, code, message):
        super().__init__(f"API Error Code {code}: {message}")
        self.code = code
        self.message = message

def handle_api_response_error(error:APIResponseError):
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

    return error.code
    

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
    try:
        result = requests.get("http://apis.data.go.kr/1360000/"+url,params, timeout=1)
        result.raise_for_status()
        result = result.json()

        head = result.get("response",{}).get("header",{})
        result_code = head.get("resultCode")
        
        if result_code != "00":
            result_msg = head.get("resultMsg") 
            raise APIResponseError(result_code, result_msg)
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

def fetch_weather_manual_Mid( time : str , regid : str
                       , number_of_rows : int = 10, page_number : int = 1 ): 
    """
    Get Middle term weather data

    Args:
        time (str): HHmm ( H: hour, m: minute)
        regid (str): location number
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

def fetch_weather_manual_Vil( xpos : int, ypos : int, date : str, time : str 
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
 
    '''
    Even if you change the variable,
        DO NOT CHANGE THE FORMAT BELOW
    '''
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
        return None
    except APIResponseError as e:
        handle_api_response_error(e)
        return None
    except RecursionError as e:
        return None

def get_weather_vil( lat : float , lon : float , day : int = 0 ) -> Dict:
    '''
    Get vilage fcst weather

    Param:
        day : Get the weather for this number of days
            in the past 

        Dictionary : 
            key
    '''
    xgrid, ygrid = get_data.latlon_to_grid(lat,lon)
    
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
    # API provide data at 10min
    corrent_time = f'{corrent_time:02d}10'
    
    # Think about it on your own
    # I don't want to comment >:(
    corrent_date = date_int/10000

    try: 
        result = fetch_weather_manual_Vil( xgrid, ygrid , corrent_date, corrent_time )

    except HTTPError as e:
        pass
    except APIResponseError as e:
        pass
    
    
    return result

