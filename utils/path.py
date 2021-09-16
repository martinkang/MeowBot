
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import convert as _convert
from . import functions as _func

BASE_INVITE_URL: str = 'https://discordapp.com/oauth2/authorize?scope=bot&permissions=388160&client_id='
DEFAULT_PRODUCTION_SERVER: str = 'api2.pixelstarships.com'

LATEST_SETTINGS_BASE_PATH: str = 'SettingService/GetLatestVersion3?deviceType=DeviceTypeAndroid&languageKey='

# ---------- RANKING ----------
TOP_CAPTAIN_PATH: str = 'LadderService/ListUsersByRanking?accessToken'
INCPECT_SHIP_PATH: str = 'ShipService/InspectShip2?accessToken'

# ---------- USER ----------
INSPECT_SHIP_BASE_PATH = f'ShipService/InspectShip2'
LEAGUE_BASE_PATH = f'LeagueService/ListLeagues2?accessToken='
LEAGUE_INFO_DESCRIPTION_PROPERTY_NAME = 'LeagueName'
LEAGUE_INFO_KEY_NAME = 'LeagueId'
LEAGUE_INFOS_CACHE = []
SEARCH_USERS_BASE_PATH = f'UserService/SearchUsers?searchString='
USER_DESCRIPTION_PROPERTY_NAME = 'Name'
USER_KEY_NAME = 'Id'

_safe_quoters = {}

async def __get_top_captains_path( aAccessToken: str, aSkip: int, aTake: int) -> str:
    sResult = f'{TOP_CAPTAIN_PATH}={aAccessToken}&from={aSkip}&to={aTake}'
    _func.debug_log( "__get_top_captains_path", f'Path : {sResult}' )
    return sResult

async def __get_inspect_ship_base_path( aAccessToken:str, aUserId: str) -> str:
    sResult = f'{INCPECT_SHIP_PATH}={aAccessToken}&userId={aUserId}'
    _func.debug_log( "__get_inspect_ship_base_path", f'Path : {sResult}' )
    return sResult
    
async def __get_users_data_path(user_name: str) -> str:
    sResult = f'{SEARCH_USERS_BASE_PATH}{_convert.url_escape(user_name)}'
    _func.debug_log( "__get_users_data_path", f'Path : {sResult}' )
    return sResult
