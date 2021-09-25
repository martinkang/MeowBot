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
        
    # for sYear in range( int(_time.PSS_TOURNEY_START_DATETIME.year) + 1, int(sNow.year) ):
    #     await insertMonthTourneyData( sYear,
    #                                   1, 
    #                                   12 )
    
    return sSuccess
     

async def insertMonthTourneyData( aYear: int, aStartMonth: int, aEndMonth: int):
    sSql = """
    INSERT INTO PSS_TOURNEY_USER_TABLE( user_id, tourney_date, user_nick, star_score, fleet_id, fleet_join_date, fleet_membership, trophy, attack_win, attack_lose, attack_draw, defence_win, defence_lose, defence_draw, crew_donated, crew_received, championship_score ) value( 73244, '2019-10-01 00:00:00+00:00', 'Ad'astra', 56,         
11947, '2019-09-01T14:16:57', 'Commander', 4257, 0, 0, 0, 0, 0, 0, 0, 0, 0 );
"""

 
                  
    sSuccess = await _db.try_Execute_once( sSql )
    print("insertMonthTourneyData")
    print(sSuccess)

    # for sMonth in range( aStartMonth, aEndMonth ):
    #     sUserCount = 0
    #     sSuccessCount = 0  
    #     sTourneyata = getToureyData( aYear, sMonth )

    #     for sUser in sTourneyata.users:
    #         sUserCount = sUserCount + 1
    #         try:
    #             sSuccess = await _db.insertTourneyUserInfo( sTourneyata.get_user_data_by_id(sUser), 
    #                                                         aYear, 
    #                                                         sMonth )                                        
    #             if sSuccess:
    #                 sSuccessCount = sSuccessCount + 1
    #         except Exception as sEx:
    #             print("insertMonthTourneyData Error : " + sEx + " UserID : " + str(sUser))  
    #             sSuccess = False

    #     print( f"insertMonthTourneyData {int(_time.PSS_START_DATETIME.year)} {sMonth} success UserCount : {sUserCount} Insert Success Count : {sSuccessCount}" )   

        


def getToureyData( aYear: int, aMonth: int ) -> TourneyData:
    sData: TourneyData = gTourneyDataClient.get_data( year = aYear, 
                                                      month = aMonth,
                                                      initializing=True )
    return sData
