import calendar

from gdrive import TourneyData, TourneyDataClient
from utils import settings as _settings
from utils import functions as _func
from utils import time as _time
from utils import database as _db
from utils import type as _type
from utils import path as _path
from utils import parse as _parse
from datetime import datetime
from utils import emojis as _emojis
from typing import List

import discord
from discord.utils import escape_markdown

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
DIVISION_DESIGN_DESCRIPTION_PROPERTY_NAME: str = 'DivisionName'
DIVISION_DESIGN_KEY_NAME: str = 'DivisionDesignId'


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


async def insertMonthTourneyOnlineUsersData( aTourneyData:TourneyData , aYear: int, aMonth: int, aDay: int):
    _func.debug_log( "insertMonthTourneyOnlineUsersData", f"Year : {aYear} Month : {aMonth} Day : {aDay}" )

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


async def getOnlineDivisionStarsData():
    sPath = await _path.__get_search_all_fleets_stars()
    sRawData = await _func.get_data_from_path( sPath )

    sFleet_infos = _parse.__xmltree_to_dict( sRawData, 3 )
    sDvisions = {}
    for division_design_id in lookups.DIVISION_DESIGN_ID_TO_CHAR.keys():
        if division_design_id != '0':
            sDvisions[division_design_id] = [fleet_info for fleet_info in sFleet_infos.values() if fleet_info[_path.DIVISION_DESIGN_KEY_NAME] == division_design_id]


    return sDvisions

def getOnlineTotalDivisionStars( aDivisionStars ):
    result = None

    if aDivisionStars:
        divisions_texts = []
        for division_design_id, fleet_infos in aDivisionStars.items():
            divisions_texts.append((division_design_id, __get_division_stars_as_text(fleet_infos)))

        sNow = _time.get_utc_now()
        sDivision = { '1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        for division_design_id, division_text in divisions_texts:
            sTitle = f'{sNow.month}월 토너먼트 {sDivision[division_design_id]}' 
            result.append(sTitle)
            result.extend(division_text)
            result.append(_type.ZERO_WIDTH_SPACE) 

    return result

def getOnlineDivisionStars( aDivisions, aDivisionStars ):
    result = None

    if aDivisionStars:
        divisions_texts = []
        sDivision = { '1': 'A', '2': 'B', '3': 'C', '4': 'D'}

        for division_design_id, fleet_infos in aDivisionStars.items():
            if sDivision[division_design_id] == aDivisions.upper():
                divisions_texts.append((division_design_id, __get_division_stars_as_text(fleet_infos)))

        sNow = _time.get_utc_now()  
        for division_design_id, division_text in divisions_texts:
            sTitle = f'{sNow.month}월 토너먼트 {sDivision[division_design_id]}' 
            result.append(sTitle)
            result.extend(division_text)
            result.append(_type.ZERO_WIDTH_SPACE) 
            break

    return result

def getOnlineFleetIDs( aDivisionStars ):
    sResult = []
    for division_design_id, fleet_infos in aDivisionStars.items():
        for i, fleet_info in enumerate(fleet_infos, start=1):
            fleet_id = escape_markdown(fleet_info['AllianceId'])
            sResult.append(fleet_id)
        
    return sResult



async def getStarsEachFleet( aFleetIDList, aNow ):
    sKey = await _func.get_access_key()

    for sFleetID in aFleetIDList:
        sPath = await _path.__get_search_fleet_users_base_path( sKey, sFleetID )
        sRawData = await _func.get_data_from_path( sPath )

        sFleet_infos = _parse.__xmltree_to_dict( sRawData, 3 )
        for user_info in sFleet_infos.values():
            #sLastScore = await _db.select_User_Last_Score( user_info["Id"], aNow.year, aNow.month )
            await _db.insertOnlineTourneyUserInfo(user_info, aNow.year, aNow.month, aNow.day)

        break

    # sDvisions = {}
    # for division_design_id in lookups.DIVISION_DESIGN_ID_TO_CHAR.keys():
    #     if division_design_id != '0':
    #         sDvisions[division_design_id] = [fleet_info for fleet_info in sFleet_infos.values() if fleet_info[_path.DIVISION_DESIGN_KEY_NAME] == division_design_id]


    # return sDvisions


def __get_division_stars_as_text(fleet_infos: List[_type.EntityInfo]) -> List[str]:
    lines = []
    fleet_infos = _func.sort_entities_by(fleet_infos, [('Score', int, True)])
    fleet_infos_count = len(fleet_infos)
    for i, fleet_info in enumerate(fleet_infos, start=1):
        fleet_name = escape_markdown(fleet_info['AllianceName'])
        additional_info: List[_type.Tuple[str, str]] = []
        trophies = fleet_info.get('Trophy')
        if trophies:
            additional_info.append((trophies, _emojis.trophy))
        member_count = fleet_info.get('NumberOfMembers')
        if member_count:
            additional_info.append((str(member_count), _emojis.members))
        stars = fleet_info['Score']
        if i < fleet_infos_count:
            difference = int(stars) - int(fleet_infos[i]['Score'])
        else:
            difference = 0
        if additional_info:
            additional_str = f' ({" ".join([" ".join(info) for info in additional_info])})'
        else:
            additional_str = ''
        lines.append(f'**{i:d}.** {stars} (+{difference}) {_emojis.star} {fleet_name}{additional_str}')
    return lines


def __get_division_title(division_design_id: str, divisions_designs_infos: _type.EntitiesData, include_markdown: bool, retrieved_date: datetime) -> str:
    title = divisions_designs_infos[division_design_id][DIVISION_DESIGN_DESCRIPTION_PROPERTY_NAME]
    if retrieved_date:
        title = f'{title} - {calendar.month_abbr[retrieved_date.month]} {retrieved_date.year}'
    if include_markdown:
        return f'__**{title}**__'
    else:
        return title


