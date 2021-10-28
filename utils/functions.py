# for get access key
from utils import time as _time
import uuid
import hashlib
import requests
from xml.etree import ElementTree as ET

import re
from typing import Dict, List , Union, Any as _Any, Awaitable, Callable, Iterable, Iterator, Optional, Tuple

import aiohttp

import logging as log

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import settings as _set
from . import database as _db
from . import type as _type
from . import parse as _parse


API_SERVER: str = "api2.pixelstarships.com"
DEFAULT_PRODUCTION_SERVER: str = 'api2.pixelstarships.com'

BASE_API_URL: str = 'https://api.pixelstarships.com/'



def init():
    global gAccessKey
    
    gAccessKey = {'Key':None, 'LastLogin':_time.PSS_START_DATETIME}
    return
        


async def get_access_key() -> str:
    debug_log( "get_access_key" )
    sAssessKey = await _get_Access_Key_From_Cache()

    if sAssessKey is None:
        sAssessKey, sNow = await _get_Access_Key_From_API_Server()
        gAccessKey['Key'] = sAssessKey
        gAccessKey['LastLogin'] = sNow
        sSuccess = await _db.updateAccessKeyData( gAccessKey['Key'], gAccessKey['LastLogin'] )
        
    sKey = gAccessKey['Key']
    sDate = gAccessKey['LastLogin']
    debug_log( "get_access_key", f'Key : {sKey} login date : {sDate}' )
    return sAssessKey
    


async def _get_Access_Key_From_Cache() -> str:
    sKey = None
    if gAccessKey['Key'] is not None:
        sNow = _time.get_utc_now()
        if _isAccessKeyIsExpired( sNow, gAccessKey['LastLogin'] ) is False:
            sKey = gAccessKey['Key']
            debug_log( "_get_Access_Key_From_Cache", "Cache Key Is Valid" )
        else:
            sKey = None
            debug_log( "_get_Access_Key_From_Cache", "Cache Key Is Invalid") 
    else:
        sKey = None
        debug_log( "_get_Access_Key_From_Cache", "Cache is None" )  
        
    return sKey


async def _get_Access_Key_From_API_Server():
    api_server = API_SERVER
    sNow = _time.get_utc_now()

    device_key: str = uuid.uuid1().hex[0:16]
    device_type: str = 'DeviceTypeMac'
    checksum = hashlib.md5((f'{device_key}{device_type}savysoda').encode('utf-8')).hexdigest()
    params = {
        'advertisingKey': '""', 'checksum': checksum,
        'deviceKey': device_key, 'deviceType': device_type,
        'isJailBroken': 'false', 'languageKey': 'en'
    }
    url = f'https://{api_server}/UserService/DeviceLogin8'
    data = requests.post(url, params=params).content.decode('utf-8')
    dataxml = ET.fromstring(data)
    access_token = dataxml.find('UserLogin').attrib['accessToken']

    return access_token, sNow


def _isAccessKeyIsExpired( aNow: _time.datetime, aKeyDate: _time.datetime) -> bool:
    sIsExpired = True
    sNow = _time.datetime.strptime( aNow.strftime(_time.DATABASE_DATETIME_FORMAT), \
        _time.DATABASE_DATETIME_FORMAT ).replace(tzinfo=_time._timezone.utc)
    sKeyDate = aKeyDate.replace(tzinfo=_time._timezone.utc)
    
    sKeyUntil = min( sKeyDate + _time.ACCESS_TOKEN_TIMEOUT, _time.get_next_day( sKeyDate ) ) - _time.ONE_SECOND
    
    if sNow < sKeyUntil:
        sIsExpired = False
        
    debug_log( "_isAccessKeyIsExpired", f'_isAccessKeyIsExpired {sNow} < {sKeyUntil} = {sNow < sKeyUntil} isExpired : {sIsExpired}')   
    return sIsExpired
        

async def __get_data_from_url(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text(encoding='utf-8')
    return data


async def get_data_from_path(path: str) -> str:
    if path:
        path = path.strip('/')
    base_url = await get_base_url()
    url = f'{base_url}{path}'
    debug_log( "get_data_from_path", url)

    sErrMsg = "errorMessage="
    sRawData = None
    sRawData = await __get_data_from_url(url)
    if sRawData.find( sErrMsg ) >= 0:
        sUrl = f'https://{DEFAULT_PRODUCTION_SERVER}/{path}'
        debug_log( "get_data_from_path", sUrl)
        sRawData = await __get_data_from_url(sUrl)
        if sRawData.find( sErrMsg ) >= 0:
            print( "get_data_from_path Error Message : " + str( sRawData ) )

   
    return sRawData


async def __get_inspect_ship_base_path(user_id: str) -> str:
    access_token = await get_access_key()

    result = f'ShipService/InspectShip2?accessToken={access_token}&userId={user_id}'
    return result


def sort_entities_by(entity_infos: List[_type.EntityInfo], order_info: List[Tuple[str, Callable[[_Any], _Any], bool]]) -> List[_type.EntityInfo]:
    """order_info is a list of tuples (property_name,transform_function,reverse)"""
    result = entity_infos
    if order_info:
        for i in range(len(order_info), 0, -1):
            property_name = order_info[i - 1][0]
            transform_function = order_info[i - 1][1]
            reverse = to_boolean(order_info[i - 1][2])
            if transform_function:
                result = sorted(result, key=lambda entity_info: transform_function(entity_info[property_name]), reverse=reverse)
            else:
                result = sorted(result, key=lambda entity_info: entity_info[property_name], reverse=reverse)
        return result
    else:
        return sorted(result)


def to_boolean(value: _Any, default_if_none: bool = False) -> bool:
    if value is None:
        return default_if_none
    if isinstance(value, str):
        try:
            value = bool(value)
        except:
            try:
                value = float(value)
            except:
                try:
                    value = int(value)
                except:
                    return len(value) > 0
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value > 0
    if isinstance(value, float):
        return value > 0.0
    if isinstance(value, (tuple, list, dict, set)):
        return len(value) > 0
    raise NotImplementedError


def debug_log( aFunc : str, aLog : str=None):
    if _set.PRINT_DEBUG:
        print( f'DEBUG {aFunc} : {aLog}' )
    

async def get_base_url() -> str:
    production_server = await __get_production_server()
    result = f'https://{production_server}/'
    return result


async def __get_production_server(language_key: str = 'en') -> str:
    latest_settings = await get_latest_settings(language_key=language_key, base_url=BASE_API_URL)

    return latest_settings['ProductionServer']

async def get_latest_settings(language_key: str = 'en', base_url: str = None) -> _type.EntityInfo:
    if not language_key:
        language_key = 'en'
    base_url = base_url or await get_base_url()
    url = f'{base_url}{_set.LATEST_SETTINGS_BASE_PATH}{language_key}'
    raw_text = await __get_data_from_url(url)
    result = _parse.__xmltree_to_dict( raw_text, 3 )
    maintenance_message = result.get('MaintenanceMessage')
  
    return result
