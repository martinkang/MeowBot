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
    await _initUserList()
    
    
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
