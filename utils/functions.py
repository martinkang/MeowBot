# for get access key
from utils import time as _time
import uuid
import hashlib
import requests
from xml.etree import ElementTree as ET

import re
from typing import Dict, List , Union

import aiohttp

import logging as log

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import settings as _set
from . import database as _db


API_SERVER: str = "api2.pixelstarships.com"
DEFAULT_PRODUCTION_SERVER: str = 'api2.pixelstarships.com'


EntityInfo = Dict[str, 'EntityInfo']
EntitiesData = Dict[str, EntityInfo]
_EntityDict = Union[List['_EntityDict'], Dict[str, '_EntityDict']]


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
        await _db.updateAccessKeyData( gAccessKey['Key'], gAccessKey['LastLogin'] )
        
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
        

async def get_base_url(use_default: bool = False) -> str:
    production_server = DEFAULT_PRODUCTION_SERVER
    result = f'https://{production_server}/'
    return result


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
    return await __get_data_from_url(url)


async def __get_inspect_ship_base_path(user_id: str) -> str:
    access_token = await get_access_key()

    result = f'ShipService/InspectShip2?accessToken={access_token}&userId={user_id}'
    return result

def debug_log( aFunc : str, aLog : str=None):
    if _set.PRINT_DEBUG:
        print( f'DEBUG {aFunc} : {aLog}' )
    





