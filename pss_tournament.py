from gdrive import TourneyData, TourneyDataClient
from utils import settings as _settings
from utils import functions as _func
from utils import time as _time
from utils import database as _db
from utils import type as _type

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


async def initTourneyDB():
    _func.debug_log( "initTourneyDB" )
    
    sSuccess = False
    sNow = _time.get_utc_now()
           
    await insertMonthTourneyData( int(_time.PSS_TOURNEY_START_DATETIME.year),
                                 int(_time.PSS_TOURNEY_START_DATETIME.month), 
                                 12 )
        
    for sYear in range( int(_time.PSS_TOURNEY_START_DATETIME.year) + 1, int(sNow.year) ):
        await insertMonthTourneyData( sYear,
                                      1, 
                                      12 )
    
    return sSuccess
     

async def insertMonthTourneyData( aYear: int, aStartMonth: int, aEndMonth: int):
    for sMonth in range( aStartMonth, aEndMonth ):
        sAlreadySaved = await _db.checkAlreadyInTourneyData( aYear, sMonth )
        if sAlreadySaved:
            print( f'Load From {aYear} {sMonth} TourneyData Already Loaded' )
        else:
            sTourneyata = getToureyData( aYear, sMonth )
            print( f'Load From {aYear} {sMonth} TourneyData Success' )
            
            #await insertMonthTourneyUsersData( sTourneyata, aYear, sMonth )
            await insertMonthTourneyFleetsData( sTourneyata, aYear, sMonth )
         

async def insertMonthTourneyUsersData( aTourneyData:TourneyData , aYear: int, aMonth: int):
        sAlreadySaved = _db.checkAlreadyInTourneyData( aYear, aMonth )
        sUserCount = 0
        sSuccessCount = 0  

        for sUser in aTourneyData:
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
        _, sUserCountInDB = _db.select_Table_Count( "PSS_TOURNEY_USER_TABLE" )
        if sUserCountInDB == sUserCount:
            sSuccess = await _db.insertLastSavedTourneyData( "LAST_SAVED_TOURNEY_USER_DATA", aYear, aMonth, sUserCountInDB )       


async def insertMonthTourneyFleetsData( aTourneyData:TourneyData , aYear: int, aMonth: int):
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
        _, sFleetCountInDB = await _db.select_Table_Count( "PSS_TOURNEY_FLEET_TABLE" )
        if sFleetCountInDB == sFleetCount:
            sSuccess = await _db.insertLastSavedTourneyData( "LAST_SAVED_TOURNEY_FLEET_DATA", aYear, aMonth, sFleetCountInDB )       



def getToureyData( aYear: int, aMonth: int ) -> TourneyData:
    sData: TourneyData = gTourneyDataClient.get_data( year = aYear, 
                                                      month = aMonth,
                                                      initializing=True )
    return sData
