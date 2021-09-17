from datetime import datetime
from getpass import getuser
import aiomysql
import asyncio
import pymysql
import configparser

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import functions as _func
from . import databaseFuncs as _dbFunc
from . import settings as _set
from . import time as _time
# from . import format as _format
from typing import Any, Callable, Dict, List, Tuple, Union


PSS_API_KEY_VERSION = 1

async def _init():
    _initConf()
    sInitPoolSuccess = await _initPool()
    if sInitPoolSuccess:
        print( "init pool success")
        _dbFunc._create_schema()
        await _dbFunc._initSchema()
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
                                                   loop=gLoop )

        print( "initialize pool success")
        sSuccess = True
            
    except Exception as sEx:
        _func.debug_log( "_initialize_pool", sEx )
        sSuccess = False
        
    return sSuccess


async def connect():
    sConnect = True
    
    sPool = await gConnectPool.acquire()
    if sPool is None:
        sConnect = await _initPool()
        sPool = await gConnectPool.acquire()
            
    return sConnect, sPool


async def try_Create_Table( aTableName: str, aColumnDefinitions: List[_dbFunc.ColumnDefinition]) -> bool:
    _func.debug_log( "try_Create_Table", aTableName )

    sCols = _dbFunc._getColumnListInDefination(aColumnDefinitions)
    sSql = f'CREATE TABLE IF NOT EXISTS {aTableName} ( {sCols} );'
    sSuccess = await try_Execute( sSql )
    return sSuccess
        
        
async def try_Execute( aSql : str ) -> bool:
    _func.debug_log( "try_Execute", aSql )
    
    sSuccess = True
    
    sIsConneted, sPool = await connect()
    if sIsConneted:
        async with sPool.cursor() as sCur:
            try:
                await sCur.execute( aSql )
                sResult = await sCur.fetchall()
                _func.debug_log( "try_Execute", aSql + " is Success" )
            except Exception as sEx:
                print( sEx )   
            sSuccess = True         
    else:
        print( "try Execute connect error" )
        sSuccess = False
    
    sPool.close()
    
    return sSuccess


async def insertAccessKeyData( aKey:str, aLoginDate:datetime ):
    _func.debug_log( "insertAccessKeyData", "Key : " + aKey + " Date : " + str(aLoginDate) )
    sSql = f"INSERT INTO PSS_ACCESS_KEY_TABLE( Access_Key, Login_Date ) VALUES( '{aKey}', '{str(aLoginDate.strftime(_time.DATABASE_DATETIME_FORMAT))}' )"
    sSuccess = await try_Execute( sSql )
    return sSuccess


async def updateAccessKeyData( aKey:str, aLoginDate:datetime ):
    _func.debug_log( "updateAccessKeyData", "Key : " + aKey + " Date : " + str(aLoginDate) )
    sSql = f"UPDATE PSS_ACCESS_KEY_TABLE SET Access_Key='{aKey}', Login_Date='{str(aLoginDate.strftime(_time.DATABASE_DATETIME_FORMAT))}';"
    sSuccess = await try_Execute( sSql )
    return sSuccess


# async def insertUserInfo( aSet:str, aRank:int, aUserInfo: _func.EntityInfo ):
#     _func.debug_log( "insertUserInfo", "Rank : " + aRank + " Name : " + aUserInfo['Name'] )
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
    
    
async def deleteData( aTableName:str):
    _func.debug_log( "deleteData", aTableName )
    return


async def select_Table( aTableName: str, aColumnDefinitions: List[_dbFunc.ColumnDefinition] = None):
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
                print( sEx )   
            sSuccess = True         
    else:
        print( "select_Table connect error" )
        sSuccess = False
        
    return sSuccess, sResult

                
