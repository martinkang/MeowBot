from datetime import datetime
import aiomysql
import asyncio
import configparser

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import functions as _func
from . import databaseFuncs as _dbFunc
from . import settings as _set
from . import time as _time
from . import type as _type

from typing import List


PSS_API_KEY_VERSION = 1

async def _init():
    sInitConfSuccess = _initConf()
    if sInitConfSuccess:
        print("init Database configure success")
    else:
        raise Exception( "init Database configure failure" )
        return

    sInitPoolSuccess = await _initPool()
    if sInitPoolSuccess:
        print( "create pool success")
        _dbFunc._create_schema()
        print( "create schema success")
        await _dbFunc._initSchema()
        print( "init schema success")

        print( "init pool success")
    else:
        raise Exception( "init pool failure" )
    
    
def _initConf():  
    global gConfig
    global gUser
    global gPW
    global gHost
    global gPort
    global gDB
    global gMaxPoolSize
    global gAutocommit
    global gLoop
    global gPoolCount
    global gCharSet

    sSuccess = False
    try:
        gConfig = configparser.ConfigParser()
        gConfig.read('conf/db.conf', encoding='utf-8')
        gUser = gConfig['DATABASE']['USER']
        gPW = gConfig['DATABASE']['PASSWORD']
        gHost = gConfig['DATABASE']['HOST']
        gPort = int( gConfig['DATABASE']['PORT'] )
        gAutocommit = gConfig['DATABASE']['AUTOCOMMIT']
        gDB = gConfig['DATABASE']['DB']
        gMaxPoolSize = gConfig['DATABASE']['MAX_POOL_SIZE']
        gLoop = asyncio.get_event_loop()
        gCharSet = 'utf8mb4' # 특수문자 입력을 위해서
        gPoolCount = 0
        sSuccess = True
    except Exception as sEx:
        _func.debug_log( "_initConf", sEx )
        sSuccess = False

    return sSuccess


async def _initPool():
    global gConnectPool

    sSuccess = False
    try:
        gConnectPool = await aiomysql.create_pool( host=gHost, 
                                                   port=gPort, 
                                                   user=gUser, 
                                                   password=gPW, 
                                                   db=gDB, 
                                                   autocommit=gAutocommit,
                                                   loop=gLoop,
                                                   charset=gCharSet )

        print( "initialize pool success")
        sSuccess = True
            
    except Exception as sEx:
        _func.debug_log( "_initPool", sEx )
        sSuccess = False
        
    return sSuccess


async def connect():
    sConnect = True

    sPool = await gConnectPool.acquire()
    if sPool is None:
        await _initPool()
        sPool = await gConnectPool.acquire()
        if sPool is not None:
            sConnect = True
        else:
            sConnect = False
  
            
    return sConnect, sPool

def release_Connection( aCur ):
    gConnectPool.release( aCur )

async def close_Connection():
    gConnectPool.close()
    await gConnectPool.wait_closed()


async def try_add_primary_key( aTableName: str,  aCols: List[str]) -> bool:
    sCols = ', '.join(aCols) 
    sSql = f'ALTER TABLE {aTableName} ADD PRIMARY KEY ( {sCols} );'
    sSuccess = await try_Execute_once( sSql )
    
    _func.debug_log( "try_add_primary_key", sSql )
    
    return sSuccess
    
    
async def try_Create_Table( aTableName: str, aColumnDefinitions: List[_dbFunc.ColumnDefinition]) -> bool:
    _func.debug_log( "try_Create_Table", aTableName )

    sCols = _dbFunc._getColumnListInDefination(aColumnDefinitions)
    sSql = f'CREATE TABLE IF NOT EXISTS {aTableName} ( {sCols} );'
    sSuccess = await try_Execute_once( sSql )
    
    return sSuccess

        
async def try_Execute_once( aSql : str ) -> bool:
    _func.debug_log( "try_Execute", aSql )
    
    sSuccess = True
    sIsConneted, sPool = await connect()
    if sIsConneted:
        async with sPool.cursor() as sCur:
            try:
                await sCur.execute( aSql )
                sResult = await sCur.fetchall()
                _func.debug_log( "try_Execute", aSql + " is Success" )
                sSuccess = True
            except Exception as sEx:
                print( "try_Execute_once Error : " +  str(sEx) )   
                sSuccess = False
        
        gConnectPool.release(sPool)    
    else:
        print( "try_Execute_once Error : try Execute connect error" )
        sSuccess = False      
    
    return sSuccess

async def try_Execute_with_Cursor( aCur, aSql : str ) -> bool:
    _func.debug_log( "try_Execute", aSql )

    sSuccess = False
    try:
        await aCur.execute( aSql )
        sResult = await aCur.fetchall()
        sSuccess = True  
        _func.debug_log( "try_Execute", aSql + " is Success" )
    except Exception as sEx:
        print( "Error try_Execute_With_Cursor Function : " + str(sEx) )   
        sSuccess = False
    
    return sSuccess
    

async def insertAccessKeyData( aKey:str, aLoginDate:datetime ):
    _func.debug_log( "insertAccessKeyData", "Key : " + aKey + " Date : " + str(aLoginDate) )
    sSql = f"INSERT INTO PSS_ACCESS_KEY_TABLE( Access_Key, Login_Date ) VALUES( '{aKey}', '{str(aLoginDate.strftime(_time.DATABASE_DATETIME_FORMAT))}' )"
    sSuccess = await try_Execute_once( sSql )
    return sSuccess


async def updateAccessKeyData( aKey:str, aLoginDate:datetime ):
    _func.debug_log( "updateAccessKeyData", "Key : " + aKey + " Date : " + str(aLoginDate) )
    sSql = f"UPDATE PSS_ACCESS_KEY_TABLE SET Access_Key='{aKey}', Login_Date='{str(aLoginDate.strftime(_time.DATABASE_DATETIME_FORMAT))}';"
    sSuccess = await try_Execute_once( sSql )
    return sSuccess


def getEntityData( aEntityData: _type.EntityInfo, aCol: str, aType: int ):      
    sResult = None
    
    if aCol in aEntityData:
        sResult = aEntityData[aCol]
    else:
        if aType == _type.INT_TYPE:
            sResult = 0
        elif aType == _type.STR_TYPE:
            sResult = ''
        elif aType == _type.DATE_TYPE:
            sResult = _time.datetime(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=_time._timezone.utc)
        else:
            sResult = None
            
    return sResult  


async def insertTourneyUserInfo( aUser: _type.EntityInfo, aYear: int, aMonth: int ):
    sUserID            = aUser['Id']
    sTourneyDate       = _time.datetime(year=aYear, month=aMonth, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=_time._timezone.utc)
    sUserName          = getEntityData( aUser, 'Name', _type.STR_TYPE )
    sStarScore         = getEntityData( aUser, 'AllianceScore', _type.INT_TYPE )
    sFleetID           = getEntityData( aUser, 'AllianceId', _type.INT_TYPE )
    sFleetJoinDate     = getEntityData( aUser, 'AllianceJoinDate', _type.DATE_TYPE )
    sFleetMembership   = getEntityData( aUser, 'AllianceMembership', _type.STR_TYPE )
    sTrophy            = getEntityData( aUser, 'Trophy', _type.INT_TYPE )
    sAtkWin            = getEntityData( aUser, 'PVPAttackWins', _type.INT_TYPE )
    sAtkLose           = getEntityData( aUser, 'PVPAttackLosses', _type.INT_TYPE )
    sAtkDraw           = getEntityData( aUser, 'PVPAttackDraws', _type.INT_TYPE )
    sDefWin            = getEntityData( aUser, 'PVPDefenceWins', _type.INT_TYPE )
    sDefLose           = getEntityData( aUser, 'PVPDefenceLosses', _type.INT_TYPE )
    sDefDraw           = getEntityData( aUser, 'PVPDefenceDraws', _type.INT_TYPE )
    sCrewDonated       = getEntityData( aUser, 'CrewDonated', _type.INT_TYPE )
    sCrewReceived      = getEntityData( aUser, 'CrewReceived', _type.INT_TYPE )
    sChampionshipScore = getEntityData( aUser, 'ChampionshipScore', _type.INT_TYPE )
    
    sSql = f"INSERT INTO PSS_TOURNEY_USER_TABLE( user_id, tourney_date, user_nick, star_score, \
    fleet_id, fleet_join_date, fleet_membership, trophy, \
    attack_win, attack_lose, attack_draw, \
    defence_win, defence_lose, defence_draw, \
    crew_donated, crew_received, championship_score ) \
    value( {sUserID}, '{sTourneyDate}', '{sUserName}', {sStarScore}, \
        {sFleetID}, '{sFleetJoinDate}', '{sFleetMembership}', {sTrophy}, \
            {sAtkWin}, {sAtkLose}, {sAtkDraw}, \
                {sDefWin}, {sDefLose}, {sDefDraw}, \
                    {sCrewDonated}, {sCrewReceived}, {sChampionshipScore} )"
 
                  
    sSuccess = await try_Execute_once( sSql )
    if sSuccess != True:
        print( "insertTourneyUserInfo Fail : " + sSql )
    return sSuccess

# async def insertTourneyUserInfo( aUserInfo: _func.EntityInfo ):
#     _func.debug_log( "insertTourneyUserInfo",  aUserInfo['Name'] )
#     sUserID = aUserInfo['Id']
#     sUserName = aUserInfo['Name']
#     # sFleet, _ = _format._get_FleetNClass( aUserInfo )
#     sTrophy = aUserInfo['Trophy']
    
#     sPvpAtkWin = aUserInfo['PVPAttackWins']
#     sPvpAtkLose = aUserInfo['PVPAttackLosses'] 
#     sPvpAtkDraw = aUserInfo['PVPAttackDraws'] 
#     sPvpDfcWin = aUserInfo['PVPDefenceWins'] 
#     sPvpDfcLose = aUserInfo['PVPDefenceLosses'] 
#     sPvpDfcDraw = aUserInfo['PVPDefenceDraws'] 
#     # sLastLogin = str( (_time.get_TimeAsTimeZone( aUserInfo['LastLoginDate'] )).strftime(_time.DATABASE_DATETIME_FORMAT) )
#     # sLastHeartbeat = str( _time.get_TimeAsTimeZone( aUserInfo['LastHeartBeatDate'] )).strftime(_time.DATABASE_DATETIME_FORMAT) )
#     # sImmunity = str( _time.get_TimeAsTimeZone( aUserInfo['ImmunityDate'] )).strftime(_time.DATABASE_DATETIME_FORMAT) )
    
#     # sSql = "INSERT INTO USER_LIST( User_ID, User_Nick, Set_Name, Fleet, Rank, Trophy, " \
#     #     + "Attack_Win, Attack_Lose, Attack_Draw, Defence_Win, Defence_Lose, Defence_Draw, " \
#     #     + "Last_Login_Date, Last_Heartbeat_Date, Immunity_Date  ) " \
#     #     + f'VALUES( {sUserID}, {sUserName}, {aSet}, {sFleet}, {aRank}, {sTrophy}, ' \
#     #     + f'{sPvpAtkWin}, {sPvpAtkLose}, {sPvpAtkDraw}, {sPvpDfcWin}, {sPvpDfcLose}, {sPvpDfcDraw} ' \
#     #     + f'{sLastLogin}, {sLastHeartbeat}, {sImmunity} )'
#     # _func.debug_log( "insertUserInfo", f'sql : {sSql}' )    
#     # sSuccess = await try_Execute( sSql )
#     return sSuccess


async def insertData( aTableName:str,  aDatas: _dbFunc.ColumnData ):
    _func.debug_log( "insertData", aTableName )
    return


async def updateData( aTableName:str,  aDatas:_dbFunc.ColumnData ):
    _func.debug_log( "updateData", aTableName )
    return
    
    
async def deleteData( aTableName:str ):
    _func.debug_log( "deleteData", aTableName )
    return


async def select_Table( aTableName: str, aColumnDefinitions: List[_dbFunc.ColumnDefinition] = None ):
    _func.debug_log( "select_Table", aTableName )
    
    sCols = None
    if aColumnDefinitions is None:
        sCols = '*'
    else:
        sCols = _dbFunc._getColumnListInDefination( aColumnDefinitions )
    sSql = f'SELECT {sCols} FROM {aTableName};'
    
    sIsConneted, sPool = await connect()
    
    sResult = []
    if sIsConneted:
        async with sPool.cursor() as sCur:
            try:
                await sCur.execute( sSql )
                sResult = await sCur.fetchall()

                _func.debug_log( "select_Table", sSql + " is Success" )
            except Exception as sEx:
                
                print( "select_Table Error : " + str(sEx) )   
            sSuccess = True

        gConnectPool.release(sPool)          
    else:
        print( "select_Table connect error" )
        sSuccess = False
        
    return sSuccess, sResult       

                
async def desc_Table( aTableName: str ):
    _func.debug_log( "desc_Table", aTableName )
    
    sSql = f'DESC {aTableName}';
    
    sIsConneted, sPool = await connect()
    sSuccess = False      
    sResult = []
    
    if sIsConneted:
        async with sPool.cursor() as sCur:
            try:
                await sCur.execute( sSql )
                sResult = await sCur.fetchall()

                _func.debug_log( "desc_Table", sSql + " is Success" )
            except Exception as sEx:
                print( "desc_Table Error : " + str(sEx) )   
            sSuccess = True    

        gConnectPool.release(sPool)
    else:
        print( "desc_Table connect error" )
        sSuccess = False
    
    return sSuccess, sResult