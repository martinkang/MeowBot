
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
TOP_FLEETS_BASE_PATH: str = 'AllianceService/ListAlliancesByRanking?skip=0&take='

# ---------- USER ----------
INSPECT_SHIP_BASE_PATH = f'ShipService/InspectShip2'
LEAGUE_BASE_PATH = f'LeagueService/ListLeagues2?accessToken='
LEAGUE_INFO_DESCRIPTION_PROPERTY_NAME = 'LeagueName'
LEAGUE_INFO_KEY_NAME = 'LeagueId'
LEAGUE_INFOS_CACHE = []
SEARCH_USERS_BASE_PATH = f'UserService/SearchUsers?searchString='

STARS_BASE_PATH: str = 'AllianceService/ListAlliancesWithDivision'

DIVISION_DESIGN_BASE_PATH: str = 'DivisionService/ListAllDivisionDesigns2'
DIVISION_DESIGN_DESCRIPTION_PROPERTY_NAME: str = 'DivisionName'
DIVISION_DESIGN_KEY_NAME: str = 'DivisionDesignId'

SEARCH_FLEET_PATH: str = 'AllianceService/SearchAlliances?accessToken'
FLEET_USERS_BASE_PATH: str ='AllianceService/ListUsers?accessToken'
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

# 토너먼트에 참가하는 모든 함대의 별 갯수
async def __get_search_all_fleets_stars() -> str:
    sResult = f'{STARS_BASE_PATH}'
    _func.debug_log( "__get_search_all_fleets_stars", f'Path : {sResult}' )
    return sResult
    
# 함대의 총 별 갯수
async def __get_search_fleets_base_path( aAccessToken:str, aFleet_name: str) -> str:
    sResult = f'{SEARCH_FLEET_PATH}={aAccessToken}&skip=0&take=100&name={_convert.url_escape(aFleet_name)}'
    _func.debug_log( "__get_search_fleets_base_path", f'Path : {sResult}' )
    return sResult

# 함대내의 함대원 별 별 갯수
async def __get_search_fleet_users_base_path( aAccessToken:str, aFleet_id: str) -> str:
    result = f'{FLEET_USERS_BASE_PATH}={aAccessToken}&skip=0&take=100&allianceId={aFleet_id}'
    return result