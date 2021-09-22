from gdrive import TourneyData, TourneyDataClient
from utils import settings as _settings

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


def getToureyData( aYear: int, aMonth: int ):
    return


def getUserFromTourneyData( aYear: int, aMonth: int, aUserID: int ):

    return
     

def getToureyRawData( aYear: int, aMonth: int ) -> TourneyData:
    sRawData: TourneyData = gTourneyDataClient.get_data( year = aYear, 
                                                         month = aMonth,
                                                         initializing=True )
    return sRawData
