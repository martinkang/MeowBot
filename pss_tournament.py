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
           
    await insertMonthTourneyData( int(_time.PSS_START_DATETIME.year),
                                 int(_time.PSS_START_DATETIME.month), 
                                 12 )
        
    for sYear in range( int(_time.PSS_START_DATETIME.year) + 1, int(sNow.year) ):
        await insertMonthTourneyData( sYear,
                                      1, 
                                      12 )
    
    return sSuccess
     

async def insertMonthTourneyData( aYear: int, aStartMonth: int, aEndMonth: int):
    for sMonth in range( aStartMonth, aEndMonth ):
        sUserCount = 0
        sSuccessCount = 0  
        sTourneyata = getToureyData( aYear, sMonth )
        for sUser in sTourneyata.users:
            sUserCount = sUserCount + 1
            sSuccess = await insertTourneyData( aYear, 
                                                sMonth, 
                                                sTourneyata.get_user_data_by_id(sUser) )
            if sSuccess:
                sSuccessCount = sSuccessCount + 1
        
        print( f"{int(_time.PSS_START_DATETIME.year)} {sMonth} success UserCount : {sUserCount} Insert Success Count : {sSuccessCount}" )  
        
        
async def insertTourneyData( aYear: int, aMonth: int, aUser: _type.EntityInfo ):
    sSuccess = False
    try:  
        sSuccess = await _db.insertTourneyUserInfo( aUser, aYear, aMonth )   
    except Exception as sEx:
        print(sEx + " UserID : " + str(aUser))
        sSuccess = False
        
    return sSuccess    
    

def getToureyData( aYear: int, aMonth: int ) -> TourneyData:
    sData: TourneyData = gTourneyDataClient.get_data( year = aYear, 
                                                      month = aMonth,
                                                      initializing=True )
    return sData
