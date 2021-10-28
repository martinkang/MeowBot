from datetime import datetime, timedelta, timezone as _timezone, date as _date, tzinfo
import datetime as _datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import functions as _func
from pytz import timezone
import pytz as _pytz


# ---------- Time --------------
API_DATETIME_FORMAT_ISO: str = '%Y-%m-%dT%H:%M:%S'
DATABASE_DATETIME_FORMAT: str ='%Y-%m-%d %H:%M:%S'
PRINT_DATETIME_FORMAT: str ='%m/%d %H:%M'
DEFAULT_TIME_ZONE: timezone = timezone('Asia/Seoul')


# ----------- TIME CONSTANT -----------
FIVE_MINUTES: timedelta = timedelta(minutes=5)
ONE_YEAR: timedelta = timedelta(days=365)
ONE_MONTH: timedelta = timedelta(days=30)
ONE_DAY: timedelta = timedelta(days=1)
ONE_HOUR: timedelta = timedelta(hours=1)
ONE_MINUTE: timedelta = timedelta(minutes=1)
ONE_SECOND: timedelta = timedelta(seconds=1)
ONE_WEEK: timedelta = timedelta(days=7)


# ---------- PSS ----------
PSS_START_DATE: _date = _date(year=2016, month=1, day=6)
PSS_START_DATETIME: datetime = datetime(year=2016, month=1, day=6)

PSS_TOURNEY_START_DATETIME: datetime = datetime(year=2019, month=10, day=1)


# ---------- TIMEOUT-----------
ACCESS_TOKEN_TIMEOUT: timedelta = timedelta(hours=12)
LOGIN_CHECK_TIMEOUT: timedelta = timedelta(minutes=10)
SEARCH_IMMUNITY_TIMEOUT: timedelta = timedelta(minutes=10)
SEARCH_IMMUNITY_PRINT_TIMEOUT: timedelta = timedelta(minutes=180)
SEARCH_IMMUNITY_SOON_TIMEOUT: timedelta = timedelta(minutes=60)
BOT_REPLY_TIMEOUT_SEC: int = 10



def init():
    global gTimeZone

    gTimeZone = DEFAULT_TIME_ZONE

    
def get_now() -> datetime:
    return datetime.now(gTimeZone)


def get_utc_now() -> datetime:
    return datetime.now(_timezone.utc)


def get_time_zone():
    return gTimeZone


def get_TimeAsTimeZone( aTime: datetime )->datetime:
    sTimeZone = get_time_zone()
    sTime = datetime.strptime( aTime, API_DATETIME_FORMAT_ISO ).astimezone(sTimeZone)
    return sTime


def get_BotTimeUTCFormat( aTime: datetime )->datetime:
    sTimeZone = _timezone.utc
    print(aTime)
    sTime = datetime.strptime( aTime, API_DATETIME_FORMAT_ISO ).replace(tzinfo=sTimeZone)

    return sTime


def get_time_diff( aStart: datetime, aEnd: datetime)->datetime: #str:
    return abs(aEnd- aStart)
    
    
def get_next_day( aDate: datetime = None ) -> datetime:
    sDate = aDate or get_utc_now()
    sResult = datetime(sDate.year, sDate.month, sDate.day, tzinfo=_timezone.utc)
    sResult = sResult + ONE_DAY
    return sResult

def getLastDayOfMonth( aYear:int, aMonth:int ) -> datetime:
    sNextMonth = getFirstDayOfNextMonth( aYear, aMonth )

    return sNextMonth - ONE_DAY


def getFirstDayOfNextMonth( aYear:int, aMonth:int ) -> datetime:
    sNextMonth = 0
    sYear = 0
    if ( aMonth == 12 ):
        sNextMonth = 1
        sYear = aYear + 1
    else:
        sNextMonth = aMonth + 1
        sYear = aYear

    sFirstDayOfNextMonth = getDateTimeFormatFromDate( sYear, sNextMonth, 1 )

    return sFirstDayOfNextMonth


def isTourneyStart() ->bool:
    return True
    sUtcNow = get_utc_now()
    sTourneyFirstDay = getTourneyStartDate( sUtcNow )

    return sUtcNow > sTourneyFirstDay
    
    
def getTourneyStartDate( aUtcNow:datetime ):
    sFirstDayNExtMonth  = getFirstDayOfNextMonth( aUtcNow.year, aUtcNow.month )
    result = sFirstDayNExtMonth - ONE_WEEK
    return result


def isStilLogin( aNow:datetime, aLastLoginDate:datetime, aLastHeartBeat:datetime  ):
    sIsLogin = True
    
    sLastLoginDate = get_BotTimeUTCFormat( aLastLoginDate )
    sLastHeartBeat = get_BotTimeUTCFormat( aLastHeartBeat )
    
    sIsLogin = True
    sTime = None
    if sLastHeartBeat > sLastLoginDate:
        sTime = sLastHeartBeat
    else:
        sTime = sLastLoginDate
    
    if aNow - sTime > LOGIN_CHECK_TIMEOUT:
        sIsLogin = False
        
    _func.debug_log( "isStilLogin", f'NOW : {aNow} HB : {sLastHeartBeat} Login : {sLastLoginDate} sisLogin : {sIsLogin}' )
    return sIsLogin


def getDateTimeFormatFromDate( aYear: int = PSS_START_DATE.year, aMonth: int = PSS_START_DATE.month, aDay: int = 1 ):
    return datetime(year=aYear, month=aMonth, day=aDay, hour=0, minute=0, second=0, microsecond=0, tzinfo= _timezone.utc) 