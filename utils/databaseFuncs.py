from typing import Any, Callable, Dict, List, Tuple, Union

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import database as db
from . import settings as _set
from . import functions as _func
from . import time as _time

# column name, type, primary key, not null
ColumnDefinition = Tuple[str, str, bool, bool]
ColumnData = Tuple[str, any]


def _create_schema() -> bool:
    global gColumn_Definitions_Settings
    global gColumn_Definitions_Daily
    global gColumn_Definitions_PSS_ACCESS_KEY
    global gColumn_Definitions_USER_LIST
    global gColumn_Definitions_LAST_SAVED_TOURNEY_USERS_DATA
    global gColumn_Definitions_LAST_SAVED_TOURNEY_FLEETS_DATA
    global gColumn_Definitions_TOURNEY_USER_LIST
    global gColumn_Definitions_TOURNEY_FLEET_LIST
    
    
    gColumn_Definitions_PSS_ACCESS_KEY = [
        ('Access_Key', 'TEXT(50)', False, True),
        ('Login_Date', 'TEXT(50)', False, True)
    ]
    
    gColumn_Definitions_Settings = [
        ('setting_version', 'int', True, True),
        ('modifydate', 'DATETIME', False, True),
        ('timezone', 'TEXT(20)', False, True),
        ('settingfloat', 'FLOAT', False, False),
        ('settingint', 'INT', False, False),
        ('settingtext', 'TEXT', False, False),
        ('setting_date', 'DATETIME', False, True)
    ]
    
    gColumn_Definitions_LAST_SAVED_TOURNEY_USERS_DATA= [
        ('Tourney_Date', 'DATETIME', True, True),   
        ('Number_of_Players', 'INT', False, True)    
    ]
    
    gColumn_Definitions_LAST_SAVED_TOURNEY_FLEETS_DATA= [
        ('Tourney_Date', 'DATETIME', True, True),   
        ('Number_of_Fleets', 'INT', False, True)    
    ]
         
    gColumn_Definitions_TOURNEY_USER_LIST = [
        ('User_ID', 'INT', False, True),
        ('Tourney_Date', 'DATETIME', False, True),
        ('User_Nick', 'TEXT(20)', False, True),
        ('Star_Score', 'INT', False, False),
        ('Fleet_ID', 'INT', False, True),
        ('Fleet_Join_Date', 'DATETIME', False, False),
        ('Fleet_Membership', 'TEXT(20)', False, False),
        ('Trophy', 'INT', False, True),
        ('Attack_Win', 'INT', False, False),
        ('Attack_Lose', 'INT', False, False),
        ('Attack_Draw', 'INT', False, False),
        ('Defence_Win', 'INT', False, False),
        ('Defence_Lose', 'INT', False, False),
        ('Defence_Draw', 'INT', False, False),
        ('Crew_Donated', 'INT', False, False),
        ('Crew_Received', 'INT', False, False),
        ('Championship_Score', 'INT', False, False)
    ]
    
    gColumn_Definitions_TOURNEY_FLEET_LIST = [
        ('Fleet_ID', 'INT', False, True),
        ('Tourney_Date', 'DATETIME', False, True),
        ('Fleet_Name', 'TEXT(20)', False, True),
        ('Star_Score', 'INT', False, False),
        ('Trophy', 'INT', False, True),
        ('Tourney_Division', 'TEXT(2)', False, True),
        ('Number_Members', 'INT', False, True),
        ('Championship_Score', 'INT', False, False)        
    ]
    
    gColumn_Definitions_USER_LIST = [
        ('User_ID', 'INT', True, True),
        ('User_Nick', 'TEXT(20)', False, True),
        ('Set_Name', 'TEXT(50)', False, True),
        ('Fleet', 'TEXT(50)', False, True),
        ('Rank', 'INT', False, True),
        ('Trophy', 'INT', False, True),
        ('Attack_Win', 'Int', False, True),
        ('Attack_Lose', 'Int', False, True),
        ('Attack_Draw', 'Int', False, True),
        ('Defence_Win', 'Int', False, True),
        ('Defence_Lose', 'Int', False, True),
        ('Defence_Draw', 'Int', False, True),
        ("Last_Login_Date", 'TEXT(50)', False, True),
        ("Last_Heartbeat_Date", 'TEXT(50)', False, True),
        ("Immunity_Date", 'TEXT(50)', False, True)
    ]

async def _initSchema():
    await _initAccessKey()
    await _initTourneyData()
    #await _initUserList()
    
    
async def _initAccessKey():
    await db.try_Create_Table( "PSS_ACCESS_KEY_TABLE", gColumn_Definitions_PSS_ACCESS_KEY )
    sSuccess, sResultList = await db.select_Table( "PSS_ACCESS_KEY_TABLE" )
    
    if len(sResultList) == 0:
        await db.insertAccessKeyData( "AccessKey", _time.PSS_START_DATETIME )
    else:
        for sKey, sLastLogin in sResultList:
            _func.gAccessKey['Key'] = sKey
            _func.gAccessKey['LastLogin'] = _time.datetime.strptime( sLastLogin, _time.DATABASE_DATETIME_FORMAT )
    
    _func.debug_log( "_initAccessKey", f'Success : {sSuccess}' )

  
async def _initTourneyData():
    _func.debug_log( "LAST_SAVED_TOURNEY_USER_DATA" )
    sSuccess = await db.try_Create_Table( "LAST_SAVED_TOURNEY_DATA", gColumn_Definitions_LAST_SAVED_TOURNEY_USERS_DATA )
    
    _func.debug_log( "LAST_SAVED_TOURNEY_FLEET_DATA" )
    sSuccess = await db.try_Create_Table( "LAST_SAVED_TOURNEY_DATA", gColumn_Definitions_LAST_SAVED_TOURNEY_FLEETS_DATA )
    
    _func.debug_log( "PSS_TOURNEY_USER_TABLE" )
    sSuccess = await db.try_Create_Table( "PSS_TOURNEY_USER_TABLE", gColumn_Definitions_TOURNEY_USER_LIST )
    if sSuccess:
        sSuccess, sResultList = await db.select_Table( "PSS_TOURNEY_USER_TABLE" )
        
        await db.try_add_primary_key( "PSS_TOURNEY_USER_TABLE", ['User_ID', 'Tourney_Date'] )
        sSuccess, sResultList = await db.desc_Table( "PSS_TOURNEY_USER_TABLE" )
        
    _func.debug_log( "PSS_TOURNEY_USER_TABLE", f'Success : {sSuccess}' )
    sSuccess = await db.try_Create_Table( "PSS_TOURNEY_FLEET_TABLE", gColumn_Definitions_TOURNEY_FLEET_LIST )
    if sSuccess:
        sSuccess, sResultList = await db.select_Table( "PSS_TOURNEY_FLEET_TABLE" )

        await db.try_add_primary_key( "PSS_TOURNEY_FLEET_TABLE", ['Fleet_ID', 'Tourney_Date'] )
        sSuccess, sResultList = await db.desc_Table( "PSS_TOURNEY_FLEET_TABLE" )
        
    _func.debug_log( "PSS_TOURNEY_FLEET_TABLE", f'Success : {sSuccess}' )
    
    
              
async def _initUserList():
    await db.try_Create_Table( "USER_LIST", gColumn_Definitions_USER_LIST )
    sSuccess, _ = await db.select_Table( "USER_LIST" )
    
    _func.debug_log( "_initUserList", f'Success : {sSuccess}' )
    
    
def _getColumnInDefination( aColName: str, aColType: str, aColIsPrimary: bool = False, aColIsNotNull: bool = False ) -> str:
    sCols = []
    sColNameTxt = aColName.lower()
    sColTypeTxt = aColType.upper()

    if aColIsPrimary:
        sCols.append('PRIMARY KEY')
    if aColIsNotNull:
        sCols.append('NOT NULL')

    sResult = f'{sColNameTxt} {sColTypeTxt}'
    if sCols:
        sResult += ' ' + ' '.join(sCols)
    return sResult.strip()

    
def _getColumnListInDefination( aColumnDefinitions: List[ColumnDefinition] ) ->str:
    sColList = []
    for sColName, sColType, sColIsPrimary, sColIsNotNull in aColumnDefinitions:
        sColList.append( _getColumnInDefination( sColName, sColType, sColIsPrimary, sColIsNotNull ) )
    
    return ', '.join(sColList)
