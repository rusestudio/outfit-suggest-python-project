import asyncio
import json
import logging as log
from datetime import datetime, timedelta
from typing import Dict

import httpx
import pandas
import requests

from config import SERVICE_KEY, VWORLD_KEY

if __name__ == "__main__":
    import get_data
else:
    from . import get_data

logger = log.getLogger(__name__)

class APIResponseError(Exception):
    def __init__(self, name, code, message):
        super().__init__(f"API({name}) Error Code {code}: {message}")
        self.name = name
        self.code = code
        self.message = message

async def fetch_address_from_latlon( lat : float , lon : float , type : str = "PARCEL", timeout : int = 10):
    '''
    get address from latitude and longitude
    ***This function use Vworld API.***
    Params:
        lat (float): Latitude
        lon (float): Longitude
        type (str): address system
    
    Returns:
        json
    '''
    apiurl = "https://api.vworld.kr/req/address?"	
    params = {	
        "service": "address",	
        "request": "getaddress",	
        "crs": "epsg:4326",	
        "point": f"{lon},{lat}",	
        "format": "json",	
        "errorFormat" : "json",
        "type": "PARCEL",	
        "key": VWORLD_KEY	
    }	
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(apiurl, params=params)	
        if response.status_code != 200:
            raise httpx.HTTPError
        return response.json()

def get_gangwon_WE(city: str) -> str:
    '''
    If city is in the 강원도 영서, it return 영서
    If city is in the 강원도 영동, it return 영동

    Params:
        city (str): city that in 강원특별자치도

    Return:
        str: 영서 or 영동
    
    Raises:
        ValueError:
            If city is not in the 강원특별자치도
    '''
    yeongseo = {
        '춘천시', '원주시', '홍천군', '횡성군', '평창군',
        '영월군', '정선군', '철원군', '화천군', '양구군', '인제군'
    }
    yeongdong = {
        '강릉시', '동해시', '속초시', '삼척시', '고성군', '양양군'
    }
    if city in yeongseo:
        return '영서'
    elif city in yeongdong:
        return '영동'
    else:
        raise ValueError

def parse_address_from_latlon(response:json):
    '''
    Parsing datas that get from VWorld API

    Params:
        response: data that get from VWorld

    Returns:
        Dictionary:
            Parsed data 
    
    Rasies:
        APIResponseError:
            So many reason of this Error
    '''
    result = response["response"]
    status = result["status"]
    if status != "OK": 
        error = result["error"]
        if status == "NOT_FOUND":
            APIResponseError("VWorld", error["code"], "Can not find Data")
        else:
            APIResponseError("VWorld", error["code"], error["message"])
    result = result.get("result",[])            
    structure = result[0].get("structure",{})
    level1 = structure["level1"]
    level2 = structure["level2"]
    return level1 , level2

async def get_address_from_latlon( lat: float , lon : float ):
    '''
    get address 

    Params:
        lat (float): Latitude
        lon (float): Longitude
    Return:
        str:
            level1(도, 특별자치시, 특별자치도, 광역시)
            level2(시, 군, 구)
    Exception:
        APIResponseError:
            when response code is 2xx, response datas are not good
    '''
    try:
        result = await fetch_address_from_latlon(lat,lon)
        return parse_address_from_latlon(result)
    except Exception as e:
        raise

async def get_KMA_land_code(lat:float,lon:float):
    '''
    get land code for getting 4-10 days land data
    '''
    level1, level2 = await get_address_from_latlon(lat,lon)
    if level1 == '강원특별자치도':
        level1 = get_gangwon_WE(level2)
    region_to_code_map = {
        "11B00000": ["서울특별시", "인천광역시", "경기도"],
        "11D10000": ["영서"], # 강원도
        "11D20000": ["영동"], # 강원도
        "11C20000": ["대전광역시", "세종특별자치시", "충청남도"],
        "11C10000": ["충청북도"],
        "11F20000": ["광주광역시", "전라남도"],
        "11F10000": ["전북특별자치도"],
        "11H10000": ["대구광역시", "경상북도"],
        "11H20000": ["부산광역시", "울산광역시", "경상남도"],
        "11G00000": ["제주특별자치도"],
    }

    for code, regions in region_to_code_map.items():
        if level1 in regions:
            return code
    return None     

def logging_KMA_api_response_error(error:APIResponseError):
    '''
    function for APIResponseError logging
    
    Params:
        error (APIResponseError): error that will be handled
    
    Return:
        errorcode (str): It can change to int
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

def get_corrent_date_hour_vil() -> tuple[str,str]:
    '''
    get date and time that FsctVil API data refresh on recent
    (0210, 0510, 0810, 1110, 1410, 1710, 2010, 2310)

    Returns:
        str: date(YYYYmmdd)
        str: time(HHMM)
    '''
    dt = datetime.now()
    hour = (dt.hour - (dt.hour - 2) % 3 + 24) % 24
    if (hour == dt.hour and dt.minute < 10):
        hour -= 3
    if dt.hour < 2:
        hour = hour % 24
        dt = dt - timedelta(days=1)
    base_time = dt.replace(day=dt.day + (-1 if dt.hour < 2 else 0),hour=hour, minute=10)
    date = base_time.strftime("%Y%m%d")
    time = base_time.strftime("%H%M")
    return date, time

def get_corrent_date_hour_mid() -> str:
    '''
    get date and time that FsctVil API data refresh on recent
    (0600, 1500)

    Returns:
        str: date and time(YYYYmmddHHMM)
    '''
    dt = datetime.now()
    hour = (dt.hour - (dt.hour - 6) % 12 + 24) % 24
    if dt.hour < 6:
        hour = hour % 24
        dt = dt - timedelta(days=1)
    base_time = dt.replace(day=(dt.day) + (-1 if dt.hour < 6 else 0), hour = hour, minute=0)
    return base_time.strftime("%Y%m%d%H%M") 

async def recive_weather_info( params : Dict, url:str, timeout: int = 100):
    """
    Recive weather data in url

    Args:
        params (Dict): parameters to send to the KMA API
        url (str): KMA service category
        timeout (int): time out flag
    
    Returns: 
        Json:
            Weather data
    
    Raises:
        httpx.HTTPError: If API response is not vaild value
        APIResponseError: If API response data is not vaild value
        Exception: If an unknown error occurs
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            result = await client.get("http://apis.data.go.kr/1360000/"+url,params=params, timeout=10)
            result.raise_for_status()
            result = result.json()

        head = result.get("response",{}).get("header",{})
        result_code = head.get("resultCode")
        
        if result_code != "00":
            result_msg = head.get("resultMsg") 
            raise APIResponseError("KMA",result_code, result_msg)
    except httpx.ReadTimeout as e:
        log.error(f"ReadTimeout: {e}")
        raise
    except httpx.TimeoutException as e:
        log.error(f"TimeoutException: {e}")
        raise
    except httpx.HTTPError as e:
        log.error(f"httpx.HTTPError : {e}")
        raise
    except APIResponseError as e:
        log.error(f"APIResponseError : {e}")
        raise
    except Exception as e:
        log.error(f"UnexpectedError : {e}")
        raise
    return result

def parse_weather_mid_land_items( response, hour) :
    '''
    parse weather data that is got from Mid_land

    Params:
        response (dict): data
        hour (str): time of KMA API data is refreshed
    '''
    items = response['response']['body']['items']['item'][0]
    result = {}
    
    for day in range(4,11) if hour != "18" else range(5,11):
        day_key = f"{day}"
        day_info = {}

        if day <= 7:
            rn_am = items.get(f'rnSt{day}Am') 
            rn_pm = items.get(f'rnSt{day}Pm')

            wf_am = items.get(f'wf{day}Am')
            wf_pm = items.get(f'wf{day}Pm')
            
            day_info['rnst'] = {'am': rn_am, 'pm' : rn_pm}
            day_info['wf'] = {'am': wf_am, 'pm' : wf_pm}
        else:
            rn = items.get(f'rnSt{day}')
            wf = items.get(f'wf{day}')
            day_info['rnst'] = rn
            day_info['wf'] = wf
        result[day_key] = day_info
    
    return result

def parse_weather_mid_tmpr_items(response,hour):
    """
    Get temperature in dictionary
    
    Params:
        response (dict): KMA data
    
    Returns:
        dict: {
            "4": {"taMin": int, "taMax": int},
            "10": {"taMin": int, "taMax": int}
        }
    """
    items = response['response']['body']['items']['item'][0]
    result = {}
    for day in range(4, 11) if hour != "18" else range(5,11):
        day_key = f"{day}"
        ta_min = items.get(f'taMin{day}')
        ta_max = items.get(f'taMax{day}')
        result[day_key] = {
            'taMin': ta_min,
            'taMax': ta_max
        }
    return result

def parse_weather_vil_items(response, t_date : str):
    '''
    parsing that weather items getting from Fcstvil
    
    Params:
        response (dict): weather data
        t_date (str): time that you want to know weather on

    Return:
        Dictionary
    '''
    items = response['response']['body']['items']['item']
    result = {}
    for item in items:
        date = item['fcstDate']
        if date != t_date:
            log.info(f"Skipping item with date {date}, expected {t_date}")
            continue  # 원하는 날짜와 다르면 건너뜀
        time = item['fcstTime']
        category = item['category']
        val = item['fcstValue']
        if date not in result:
            result[date] = {}
        if time not in result[date]:
            result[date][time] = {}
        result[date][time][category] = val
    return result

def get_weather_data_items(result: dict,item : str ,date:str,time:str):
    '''
    get average probavility of percipitation

    Params:
        result (dict): waether data that got from KMA Fcst vilage api
        item (str): name of item you want to get
        date (str): date that you want to know weather on
        time (str): time that you want to get weather from to 23

    Return:
        float : average of item
        float : maximum of item
        float : minimum of item
    '''

    hour = (int(time[:2]) + 1 )%24
    maximum = -999.0
    minimum = 999.0
    average = 0.0
    count = 0
    try:
        for time in range(hour,23):
            count += 1
            data = float(result[date][f"{time:02d}00"][item])
            average += data
            maximum = max(data,maximum)
            minimum = min(data,minimum)
        average /= count
        average = round(average,2)
    except Exception as e:
        log.error(f"error: {e}")
        raise
    return average, maximum, minimum

def get_mid_temp_average(data):
    '''
    get data average from KMA mid-temperature data

    Params:
        data (dict): data 
    
    Returns:
        float:
            average of data
    '''
    tmp = 0
    tmp += data.get("taMin")
    tmp += data.get("taMax")
    tmp = tmp/2
    return tmp

def get_mid_weather_average(tm_data,we_data,delt_time):
    '''
    get data average from KMA mid-land and mid-temp data

    Params:
        tm_data (dict): temperature data 
        we_data (dict): land data  
        delt_time (int): target time
    
    Returns:
        dictionary:
            temperature: str(float)
            wind : Null
            rain: str(float)
            huminity : Null
    '''
    tmp_avg = get_mid_temp_average(tm_data)
    rin_avg = 0
    if delt_time < 8 :
        rin_avg += we_data.get("rnst").get("am")
        rin_avg += we_data.get("rnst").get("pm")
        rin_avg = float(rin_avg/2)
    else:
        rin_avg = we_data.get("rnst")
    weather_data = {
        "temperature": str(tmp_avg),
        "wind" : "Null",
        "rain": str(rin_avg),
        "huminity" : "Null"
    }
    return weather_data 

def get_weather_vil_average(result,target_date,target_time):
    
    '''
    get average of tmp, wsd, reh, pop

    Params:
        result : parsed Fsct vilage datas
        target_date : date that you want to get
        target_time : time that you want to get
    
    Returns:
        temperature: str(float),  # Celsius
        wind: str(float) 
        rain: str(float) 
        humidity: str(float)
    '''
    tm_av, _,_ = get_weather_data_items(result, "TMP", target_date, target_time)
    ws_av, _,_ = get_weather_data_items(result, "WSD", target_date, target_time)
    rh_av, _,_ = get_weather_data_items(result, "REH", target_date, target_time) 
    pp_av, _,_ = get_weather_data_items(result, "POP", target_date, target_time)

    weather_data = {
        "temperature": str(tm_av),  # Celsius
        "wind": str(ws_av),  # or value in km/h
        "rain": str(pp_av), #%
        "humidity": str(rh_av),
    }
    return weather_data

async def fetch_weather_mid( regid : str, date : str
                       , number_of_rows : int = 10, page_number : int = 1 
                       , api_type : str = "MidTa"): 
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
        httpx.HTTPError: If API Response is not vaild value
        APIResponseError: If API response data is not vaild value
        Exception: If an unknown error occurs
        
    """
    url = "MidFcstInfoService/"+api_type
 
    # Even if you change the variable,
    #   DO NOT CHANGE THE FORMAT BELOW

    params = {
        'serviceKey' : SERVICE_KEY,
        'numOfRows' : number_of_rows,
        'pageNo' : page_number,
        'dataType' : 'JSON',
        'regId' : regid,
        'tmFc' : date
    }
    try:
        return await recive_weather_info(params,url)
    except httpx.HTTPError as e:
        log.error(f"httpx.HTTPError : {e}")
        raise
    except APIResponseError as e:
        log.error(f"APIResponseError : {e}")
        raise
    except Exception as e:
        log.error(f"UnexpectedError : {e}")
        raise

async def fetch_weather_vil( xpos : int , ypos : int , date : str , time : str 
                       , number_of_rows : int = 12 , page_number : int = 1 ): 
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
        return await recive_weather_info(params,url)
    except httpx.ReadTimeout as e:
        raise
    except httpx.TimeoutException as e:
        raise
    except httpx.HTTPError as e:
        raise
    except APIResponseError as e:
        logging_KMA_api_response_error(e)
        log.error(f"APIResponseError : {e}")
        log.info(f"Params: {params.get('base_date')}, {params.get('base_time')}, {params.get('nx')}, {params.get('ny')}, {params.get('numOfRows')}, {params.get('pageNo')}")
        raise
    except Exception as e:
        raise

async def get_weather_vil( lat : float , lon : float , date : str , time : str ,
                    delt_day : int = 0) -> Dict:
    '''
    Get vilage fcst weather

    Param:
        day : Get the weather for this number of days
            in the past 

        Dictionary : 
            key : 
    '''
    xgrid, ygrid = get_data.combert_latlon_to_grid(lat,lon)
    hour = int(time[0:2])
    page , more_page, line, front_pad, back_pad = get_data.get_efficient_params_vil(hour, delt_day)
    try: 
        if more_page == 0: 
            result = await fetch_weather_vil( xgrid, ygrid, date, time, number_of_rows=line,page_number=page)
        else:
            result = {"response": {"body": {"items": {"item": []}}}}
            tasks = [
                fetch_weather_vil(xgrid, ygrid, date, time, number_of_rows=line, page_number=i)
                for i in range(page - more_page, page + 1)
            ]
            responses = await asyncio.gather(*tasks)
            for result_page in responses: 
                items = result_page.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                if not isinstance(items, list):
                    items = [items]
                result["response"]["body"]["items"]["item"].extend(items)
    except httpx.ReadTimeout as e:
        raise
    except httpx.TimeoutException as e:
        raise
    except httpx.HTTPError as e:
        raise
    except APIResponseError as e:
        raise
    except RecursionError as e:
        raise   
    return result

async def get_weather_mid( lat : float , lon : float , day : int = 0 ) -> Dict:
    '''
    Get vilage fcst weather

    Param:
        day : Get the weather for this number of days
            in the past 

        Dictionary : 
            key
    '''
    date = get_corrent_date_hour_mid()
    tmpr_code = get_data.get_nearest_Fcstcodes(lat,lon) 
    try: 
        land_code = await get_KMA_land_code(lat,lon)
        r_land, r_tmpr = await asyncio.gather(fetch_weather_mid(land_code, date, api_type="getMidLandFcst")
                                              , fetch_weather_mid(tmpr_code, date, api_type="getMidTa"))
        return r_land, r_tmpr
    except httpx.HTTPError as e:
        raise
    except APIResponseError as e:
        logging_KMA_api_response_error(e)
        raise
    except RecursionError as e:
        raise   

async def get_weather( lat : float , lon : float , delt_day : int = 0):
    '''
    get weather

    Params:
        lat (float): latitude
        lon (float): longitude
        delt_day (int): day that you want to get weather on from today
    
    Returns:
        dictionary:
            temperature: str(float)
            wind: str(float) | None
            rain: str(float) | None
            humidity: str(float)

    Raise
        httpx.ReadTimeout:
            when Too Much times
        httpx.TimeoutException:
            when time over
        APIResponseError:
            when response ok but data is not ok
        RecursionError:
            when Too Much Functions
        ValueError:
            when input data is wrong
    '''
    if delt_day <= 3 :
        date, time = get_corrent_date_hour_vil()
        target_date = str(int(date)+delt_day)
        target_time = ("0000" if (target_date != date) else time)
            
        log.info(f"{date}{time},{target_date}{target_time}")
        try:
            response = await get_weather_vil(lat, lon, date, time, delt_day)
            result = parse_weather_vil_items(response,target_date) 
            data = get_weather_vil_average(result,target_date,target_time) 
        except httpx.ReadTimeout as e:
            raise
        except httpx.TimeoutException as e:
            raise
        except APIResponseError as e:
            raise
        except RecursionError as e:
            raise   
        except ValueError as e:
            raise
        except Exception as e:
            raise
        return data
    elif delt_day <= 10:
        date = get_corrent_date_hour_mid()
        hour = date[8:10]
        try:
            mid_response_land, mid_response_tmpr = await get_weather_mid(lat, lon, date)
            mid_tmpr = parse_weather_mid_tmpr_items(mid_response_tmpr,hour)
            mid_land = parse_weather_mid_land_items(mid_response_land,hour)
            mid_tmpr = mid_tmpr.get(str(delt_day))
            mid_land = mid_land.get(str(delt_day))
            data = get_mid_weather_average(mid_tmpr, mid_land,delt_day)
        except httpx.ReadTimeout as e:
            raise
        except httpx.TimeoutException as e:
            raise
        except APIResponseError as e:
            raise
        except RecursionError as e:
            raise
        except ValueError as e:
            raise
        except Exception as e:
            raise
        return data
    else:
        raise ValueError