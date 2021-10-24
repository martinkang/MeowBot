from gdrive import TourneyData, TourneyDataClient
from utils import settings as _settings
from utils import functions as _func
from utils import time as _time
from utils import database as _db
from utils import type as _type
from utils import path as _path
from utils import parse as _parse
from typing import List

import pss_lookups as lookups

#==============================================================================================
# Tournament Data from GDRIVE
#==============================================================================================
gTourneyDataClient: TourneyDataClient = TourneyDataClient(
    _settings.GDRIVE_PROJECT_ID,
    _settings.GDRIVE_PRIVATE_KEY_ID,
    _settings.GDRIVE_PRIVATE_KEY,
    _settings.GDRIVE_CLIENT_EMAIL,
    _settings.GDRIVE_CLIENT_ID,
    _settings.GDRIVE_SCOPES,
    _settings.GDRIVE_FOLDER_ID,
    _settings.GDRIVE_SERVICE_ACCOUNT_FILE,
    _settings.GDRIVE_SETTINGS_FILE,
    _settings.TOURNAMENT_DATA_START_DATE
)

ALLOWED_DIVISION_LETTERS: List[str] = sorted([letter for letter in lookups.DIVISION_CHAR_TO_DESIGN_ID.keys() if letter != '-'])

async def initTourneyDB():
    _func.debug_log( "initTourneyDB" )
    
    sSuccess = False
    sNow = _time.get_utc_now()

    await insertMonthTourneyData( int(_time.PSS_TOURNEY_START_DATETIME.year),
                                  int(_time.PSS_TOURNEY_START_DATETIME.month), 
                                  12 )
        
    for sYear in range( int(_time.PSS_TOURNEY_START_DATETIME.year) + 1, int(sNow.year) + 1):
        await insertMonthTourneyData( sYear,
                                      1, 
                                      12 )
    
    return sSuccess
     

async def insertMonthTourneyData( aYear: int, aStartMonth: int, aEndMonth: int):
    _func.debug_log( "initTourneyDB", f"Year : {aYear} Start Month : {aStartMonth} End Month : {aEndMonth}" )
    sNow = _time.get_utc_now()
    sNowYear = sNow.year
    sNowMonth = sNow.month 

    for sMonth in range( aStartMonth, aEndMonth + 1 ):
        if aYear == sNowYear and sNowMonth == sMonth:
            break

        _, sUserCount = await _db.checkAlreadyInTourneyUserData( aYear, sMonth )
        _, sFleetCount = await _db.checkAlreadyInTourneyFleetData( aYear, sMonth )
        
        if sFleetCount[0] > 0 and sUserCount[0] > 0:
            print( f'Load From {aYear} {sMonth} TourneyData Already Loaded' )
        else:
            try:
                sTourneyata = getTourneyData( aYear, sMonth )
                print( f'Load From {aYear} {sMonth} TourneyData Success' )
                
                if sUserCount[0] == 0:
                    await insertMonthTourneyUsersData( sTourneyata, aYear, sMonth )

                if sFleetCount[0] == 0:
                    await insertMonthTourneyFleetsData( sTourneyata, aYear, sMonth )
            except Exception as sEx:
                print( f"insertMonthTourneyData Year : {aYear} Month : {sMonth} is Error : {sEx}" )
         

async def insertMonthTourneyUsersData( aTourneyData:TourneyData , aYear: int, aMonth: int):
    _func.debug_log( "insertMonthTourneyUsersData", f"Year : {aYear} Month : {aMonth}" )

    sUserCount = 0
    sSuccessCount = 0  

    for sUser in aTourneyData.user_ids:
        sUserCount = sUserCount + 1
        try:
            sSuccess = await _db.insertTourneyUserInfo( aTourneyData.get_user_data_by_id(sUser), 
                                                        aYear, 
                                                        aMonth )                                        
            if sSuccess:
                sSuccessCount = sSuccessCount + 1
        except Exception as sEx:
            print("insertMonthTourneyData Error : " + sEx + " UserID : " + str(sUser))  
            sSuccess = False

    print( f"insertMonthTourneyData {aYear} {aMonth} success UserCount : {sUserCount} Insert Success Count : {sSuccessCount}" )   
    _, sUserCountInDB = await _db.selectCountTourneyUserData( aYear, aMonth )
    print("sUserCountInDB " + str(sUserCountInDB[0]))
    print("sUserCount " + str(sUserCount))
    if sUserCountInDB[0] == sUserCount:
        sSuccess = await _db.insertLastSavedTourneyUserData( aYear, aMonth, sUserCountInDB[0] )       



async def insertMonthTourneyFleetsData( aTourneyData:TourneyData , aYear: int, aMonth: int):
    _func.debug_log( "insertMonthTourneyFleetsData", f"Year : {aYear} Month : {aMonth}" )

    sFleetCount = 0
    sSuccessCount = 0
    
    for sFleet in aTourneyData.fleet_ids:
        sFleetCount = sFleetCount + 1
        try:
            sSuccess = await _db.insertTourneyFleetInfo( aTourneyData.get_fleet_data_by_id(sFleet), 
                                                            aYear, 
                                                            aMonth )                                        
            if sSuccess:
                sSuccessCount = sSuccessCount + 1
        except Exception as sEx:
            print("insertMonthTourneyData Error : " + sEx + " UserID : " + str(sFleet))  
            sSuccess = False

    print( f"insertMonthTourneyData {aYear} {aMonth} success FleetCount : {sFleetCount} Insert Success Count : {sSuccessCount}" )   
    _, sFleetCountInDB = await _db.selectCountTourneyFleetData( aYear, aMonth )
    print("sFleetCountInDB " + str(sFleetCountInDB[0]))
    print("sFleetCount " + str(sFleetCount))
    if sFleetCountInDB[0] == sFleetCount:
        sSuccess = await _db.insertLastSavedTourneyFleetData( aYear, aMonth, sFleetCountInDB[0] )       

def getTourneyData( aYear: int, aMonth: int ) -> TourneyData:
    sData: TourneyData = gTourneyDataClient.get_data( year = aYear, 
                                                      month = aMonth,
                                                      initializing=True )
    return sData

def isDivisionLetter( aStr: str ) -> bool:
    sResult = False
    if aStr is None:
        sResult = False
    else:
        sResult = aStr.lower() in [letter.lower() for letter in ALLOWED_DIVISION_LETTERS]
    return sResult


async def getStars():
    sPath = await _path.__get_search_all_fleets_stars()
    sRawData = await _func.get_data_from_path( sPath )

    sStars = _parse.__xmltree_to_dict( sRawData, 3 )
    
    return sStars


# async def getDivisionStars(ctx: Context, division: str = None, fleet_data: dict = None, retrieved_date: datetime = None, as_embed: bool = _settings.USE_EMBEDS) -> Union[List[Embed], List[str]]:
#     if division:
#         pss_assert.valid_parameter_value(division, 'division', min_length=1, allowed_values=ALLOWED_DIVISION_LETTERS)
#         if division == '-':
#             division = None
#     else:
#         division = None

#     if fleet_data is None or retrieved_date is None:
#         data = await core.get_data_from_path(STARS_BASE_PATH)
#         fleet_infos = utils.convert.xmltree_to_dict3(data)
#     else:
#         fleet_infos = fleet_data


