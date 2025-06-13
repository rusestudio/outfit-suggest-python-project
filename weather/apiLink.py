import requests
import httpx
import asyncio


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

logger = log.getLogger(__name__)

class APIResponseError(Exception):
    def __init__(self, name, code, message):
        super().__init__(f"API({name}) Error Code {code}: {message}")
        self.name = name
        self.code = code
        self.message = message

def fetch_address_from_latlon( lat : float , lon : float , type : str = "PARCEL"):
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
    response = requests.get(apiurl, params=params)	
    if response.status_code != 200:
        print("wow")
    return response.json()

def parse_address_from_latlon(response:json):
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

def get_address_from_latlon( lat: float , lon : float ):
    try:
        result = fetch_address_from_latlon(lat,lon)
        return parse_address_from_latlon(result)
    except Exception as e:
        log.critical(f"FUCK : {e}")

def get_KMA_location_code( lat:float , lon : float):
    pass

def get_KMA_location_code( lat:float , lon : float):
    pass

def logging_KMA_api_response_error(error:APIResponseError):
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

def get_corrent_date_hour_vil() -> tuple[str,str]:
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
    dt = datetime.now()
    hour = (dt.hour - (dt.hour - 6) % 12 + 24) % 24
    if dt.hour < 6:
        hour = hour % 24
        dt = dt - timedelta(days=1)
    base_time = dt.replace(day=dt.day + (-1 if dt.hour < 6 else 0), hour = hour, minute=0)
    return base_time.strftime("%Y%m%d%H%M") 

def get_data_by_date(json_data, target_date):
    return json_data.get(target_date, {})

async def recive_weather_info( params : Dict, url:str, timeout: int = 100):
    """
    recive weather data

    Args:
        params (Dict): parameters to send to the KMA API
        url (str): KMA service category
        timeout (int): time out flag
    
    Returns: 
        Json
    
    Raises:
        httpx.HTTPError: If API Response is not vaild value
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

def parse_weather_vil_items(response, t_date):
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

def get_weather_TMX_TMN(result: dict,date:str,time:str):
    hour = (int(time[:2]) + 1)%24
    tmp_max = -999
    tmp_min = 999
    tmp_avg = 0
    count = 0
    try:
        for time in range(hour,23):
            count += 1
            tmp = int(result[date][f"{time:02d}00"]["TMP"])
            tmp_avg += tmp
            tmp_max = max(tmp,tmp_max)
            tmp_min = min(tmp,tmp_min)
        tmp_avg /= count
        tmp_avg = round(tmp_avg,2)
    except Exception as e:
        log.error(f"error: {e}")
        raise

    return tmp_avg, tmp_min, tmp_max

def get_weather_WSD(result: dict,date:str,time:str):
    hour = (int(time[:2]) + 1)%24
    wsd_avg = 0.0
    count = 0
    try:
        for time in range(hour,23):
            count += 1
            wsd = float(result[date][f"{time:02d}00"]["WSD"])
            wsd_avg += wsd
        wsd_avg /= count
        wsd_avg = round(wsd_avg,2)
    except Exception as e:
        log.error(f"error: {e}")
        raise
    return wsd_avg

def get_weather_POP(result: dict,date:str,time:str):
    hour = (int(time[:2]) + 1)%24
    pop_avg = 0.0
    count = 0
    try:
        for time in range(hour,23):
            count += 1
            pop = float(result[date][f"{time:02d}00"]["POP"])
            print(pop,pop_avg)
            pop_avg += pop
        pop_avg /= count
        pop_avg = round(pop_avg,2)
    except Exception as e:
        log.error(f"error: {e}")
        raise
    return pop_avg

def get_weather_REH(result: dict,date:str,time:str):
    hour = (int(time[:2]) + 1)%24
    reh_avg = 0.0
    count = 0
    try:
        for time in range(hour,23):
            count += 1
            reh = float(result[date][f"{time:02d}00"]["REH"])
            reh_avg += reh
        reh_avg /= count
        reh_avg = round(reh_avg,2)
    except Exception as e:
        log.error(f"error: {e}")
        raise
    return reh_avg

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
        httpx.HTTPError: If API Response is not vaild value
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
    print(params)
    try:
        return recive_weather_info(params,url)
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

def get_weather_Mid( lat : float , lon : float , day : int = 0 ) -> Dict:
    '''
    Get vilage fcst weather

    Param:
        day : Get the weather for this number of days
            in the past 

        Dictionary : 
            key
    '''
    date = get_corrent_date_hour_mid()
    geo_code = get_address_from_latlon(lat,lon)
    try: 
        result = fetch_weather_Mid( geo_code, date)
    except httpx.HTTPError as e:
        raise
    except APIResponseError as e:
        logging_KMA_api_response_error(e)
        raise
    except RecursionError as e:
        raise   
    return result
     
async def get_weather( lat : float , lon : float , delt_day : int = 0):
    '''
    get weather
    '''
    print("what?")
    if delt_day <= 3:
        date, time = get_corrent_date_hour_vil()
        log.warning(f"{date}{time}")
        try:
            result = await get_weather_vil(lat, lon, date, time, delt_day)
            result = parse_weather_vil_items(result,str(int(date)+delt_day))
            
        except httpx.ReadTimeout as e:
            raise
        except httpx.TimeoutException as e:
            raise
        except APIResponseError as e:
            raise
        except RecursionError as e:
            raise   
        return result
    elif delt_day <= 7:
        dt = datetime.now()
        hour = dt.hour - ((dt.hour - 2) % 12 + 24) %24
        result = get_weather_Mid(lat, lon, date)
        result = parse_weather_Mid_items(result, str(int(date)+delt_day))
    elif delt_day <=10:
        result = get_weather_Mid(lat, lon, date)
    else:
        return result

def main():
    lat, lon= 37.564214, 127.001699
    print(f"lat : {lat}")
    print(f"lon : {lon}")
    print(f"================================")

    xpos, ypos = get_data.combert_latlon_to_grid(lat, lon)
    date, time = get_corrent_date_hour_vil()

    print(f"xpos : {xpos}")
    print(f"ypos : {ypos}")

    print(f"================================")

    delt_day = 1
    log.info("fuck you")
    result = asyncio.run(get_weather(lat,lon,delt_day))
    # result = await get_weather_vil(lat, lon, date, time, delt_day)
    date = str(int(date)+delt_day)
    
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    avg, tmp_min, tmp_max = get_weather_TMX_TMN(result, date, time)
    wsd_avg = get_weather_WSD(result, date, time)
    pop = get_weather_POP(result, date, time)
    print(date,time)
    print(avg,tmp_min,tmp_max,wsd_avg)
    print(pop)

def test():
    l1, l2 = get_address_from_latlon(37.564214, 127.001699)
    print(l1)
    print(l2)

if __name__ == "__main__":
    log.basicConfig(filename="example.log", filemode="w",level=log.INFO)
    log.info("start __main__")
    test()