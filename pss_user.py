from datetime import datetime
from re import A
from typing import Dict, List, Tuple, Optional

import asyncio
import pss_ship as _ship

from utils import functions as _func
from utils import type as _type
from utils import path as _path
from utils import parse as _parse
from utils import emojis as _emojis
from utils import discord as _discord
from utils import format as _format
from utils import time as _time

from discord.ext.commands import Context, context
from discord.utils import escape_markdown
from discord import Colour, Embed, Message

USER_DESCRIPTION_PROPERTY_NAME = 'Name'
USER_KEY_NAME = 'Id'



# SET ID, SET, USER ID, NICK, FLEET, TROPHY

async def _getUserInfoByFunction( aCtx:context, 
                                aExactName: str, 
                                aNow:datetime,
                                aUserInfos: List[_type.EntityInfo], 
                                aIsNeedShipInfo:bool, 
                                aSelectFunc, 
                                aFormatFunc ):
    sOptMsg = None
    sErrMsg = None
    sAliveInfos, sAliveInfosTxt = get_User_Alive_Infos( aCtx, aUserInfos )

    if len(aUserInfos) > 1:
        sOutputEmbed = Embed(title=f'{aExactName} 유저 리스트', description=sAliveInfosTxt, color=0x00aaaa)
        sOutputEmbed.set_footer(text="조회를 원하는 유저 번호를 입력해 주세요")
        sOptMsg = await aCtx.send(embed=sOutputEmbed, mention_author='mention_author')
        
        sErrMsg, sInfosTxt = await aSelectFunc( aCtx, aNow, sAliveInfos, aUserInfos )
            
        await sOptMsg.delete()
    else:  
        sShipInfo = None       
        sUSerInfo = aUserInfos[0]
        if aIsNeedShipInfo is True and \
            _time.isStilLogin( aNow, sUSerInfo['LastLoginDate'], sUSerInfo['LastHeartBeatDate']  ) is not True:
            sShipInfo = await _ship.get_Inspect_Ship_info( sUSerInfo['Id'] )
            
        sErrMsg, sInfosTxt = aFormatFunc( aNow, sUSerInfo, sShipInfo )
    
    return sErrMsg, sInfosTxt
        

async def get_Selected_User_Alive_Info( aCtx: Context, aNow:datetime,  aUserIDSet: Dict, aUserInfos: List[_type.EntityInfo] ):
    def check(m): 
        return m.author == aCtx.message.author and m.channel == aCtx.message.channel 

    sSelectMsg: Message = None
    sInfosTxt = None
    sErrMsg = None
    try:
        sSelectMsg = await aCtx.bot.wait_for('message', timeout=_time.BOT_REPLY_TIMEOUT_SEC, check=check)
        sErrMsg = None
    except asyncio.TimeoutError:
        sSelectMsg = None
        sErrMsg = f'{_time.BOT_REPLY_TIMEOUT_SEC} 초 안에 선택해야 합니다.'
    else:
        if int(sSelectMsg.content) in aUserIDSet:
            for sUserInfo in aUserInfos:
                if aUserIDSet[int(sSelectMsg.content)] == sUserInfo['Id']:
                    sErrMsg, sInfosTxt = _format.create_User_Alive( aNow, sUserInfo, None )
                    break    
    return sErrMsg, sInfosTxt
                    
                
def get_User_Alive_Infos( _: Context, aUserInfos: List[_type.EntityInfo] ):
    sALiveInfos = {}
    sInfosTxt = ''
    sNo = 0
    for sUserInfo in aUserInfos:
        sNo = sNo + 1    
        sALiveInfos[sNo] = sUserInfo['Id']
        sInfo = _format.create_User_List( sNo, sUserInfo )
        _func.debug_log( "getUserInfo", sInfo )
        sInfosTxt = sInfosTxt + sInfo + '\n'

    _func.debug_log( "getUserInfo", f'Number of Users : {sNo}' )
    return sALiveInfos, sInfosTxt


async def get_users_infos_by_name( _: Context, aUserName: str ) -> List[_type.EntityInfo]:
    user_infos = list( (await __get_users_data( aUserName ) ).values())
    return user_infos


async def __get_users_data( aUserName: str) -> _type.EntitiesData:
    sPath = await  _path.__get_users_data_path( aUserName )
    raw_data = await _func.get_data_from_path( sPath )
    user_infos = _parse.__xmltree_to_dict( raw_data, 3 )
    return user_infos



async def get_Selected_User_N_Ship_Info( aCtx: Context, aNow:datetime, aUserIDSet: Dict, aUserInfos: List[_type.EntityInfo] ):
    def check(m): 
        return m.author == aCtx.message.author and m.channel == aCtx.message.channel 

    sSelectMsg: Message = None
    sInfosTxt = None
    sErrMsg = None

    try:
        sSelectMsg = await aCtx.bot.wait_for('message', timeout=_time.BOT_REPLY_TIMEOUT_SEC, check=check)
        sErrMsg = None
    except asyncio.TimeoutError:
        sSelectMsg = None
        sErrMsg = f'{_time.BOT_REPLY_TIMEOUT_SEC} 초 안에 선택해야 합니다.'
    else:
        if int(sSelectMsg.content) in aUserIDSet:
            for sUserInfo in aUserInfos:
                if aUserIDSet[int(sSelectMsg.content)] == sUserInfo['Id']:
                    sShipInfo = None
                    if _time.isStilLogin( aNow, sUserInfo['LastLoginDate'], sUserInfo['LastHeartBeatDate']  ) is not True:
                        sShipInfo = await _ship.get_Inspect_Ship_info( sUserInfo['Id'] )
                        
                    sErrMsg, sInfosTxt = _format.create_User_Immunity( aNow, sUserInfo, sShipInfo )
                    break    
                
    return sErrMsg, sInfosTxt


async def _get_top_captains_For_UserInfos( aSkip: int, aTake: int) -> List[_type.EntityInfo]:
    sStart = aSkip + 1
    sRawData = await _get_top_captains_data( aSkip, aTake )

    sPreparedData = [] 
    if sRawData:
        sPreparedData = _prepare_Top_Captains_For_UserInfo( sRawData, sStart, aTake )
    else:
        print(f'An unknown error occured while retrieving the top captains. Please contact the bot\'s author!')   
        
    return sPreparedData


async def get_fleet_infos_by_name( _: Context, aFleetName: str ) -> List[_type.EntityInfo]:
    sFleetInfos = list( (await __get_fleet_data( aFleetName ) ).values())
    return sFleetInfos


async def __get_fleet_data( aFleetName: str) -> _type.EntitiesData:
    sAccessToken = await _func.get_access_key()
    sPath = await  _path.__get_search_fleets_base_path( sAccessToken, aFleetName )
    print(sPath)
    sRawData = await _func.get_data_from_path( sPath )
    print(sRawData)
    sFleet_infos = _parse.__xmltree_to_dict( sRawData, 3 )
    print(sFleet_infos)
    return sFleet_infos


async def get_User_infos_by_Fleet_ID( _: Context, aFleetID: str ) -> List[_type.EntityInfo]:
    sFleetInfos = await __get_fleet_users_data_by_ID( aFleetID )
    return sFleetInfos

async def __get_fleet_users_data_by_ID( aFleetID: str) -> _type.EntitiesData:
    print("__get_fleet_users_data_by_ID " + aFleetID )
    sAccessToken = await _func.get_access_key()
    sPath = await  _path.__get_search_fleet_users_base_path( sAccessToken, aFleetID )
    print(sPath)
    sRawData = await _func.get_data_from_path( sPath )
    print(sRawData)
    sUsers_infos = _parse.__xmltree_to_dict( sRawData, 3 )
    print(sUsers_infos)
    return sUsers_infos


async def _get_top_captains_data( aSkip: int, aTake: int) -> _type.EntitiesData:
    sAccessToken = await _func.get_access_key()
    sPath = await  _path.__get_top_captains_path( sAccessToken, aSkip + 1, aTake )

    raw_data = await _func.get_data_from_path( sPath )
    data = _parse.__xmltree_to_dict( raw_data, 3 )
    return data


def __prepare_top_captains( users_data: _type.EntitiesData, aStart: int, aTake: int ) -> List[Tuple]:
    sStart = aStart
    sEnd = ( sStart - 1 ) + aTake
    result = [
        (
            position,
            user_info['Name'],
            escape_markdown(user_info['AllianceName']),
            escape_markdown(user_info['LastHeartBeatDate']),
            # user_info['AllianceName'],
            # user_info['LastHeartBeatDate'],
            user_info['Trophy']
        )
        for position, user_info
        in enumerate(users_data.values(), start=sStart)
        if position >= sStart and position <= sEnd
    ]
    return result



def _prepare_Top_Captains_For_UserInfo( aUsersData: _type.EntitiesData, aStart: int, aTake: int ) -> List[_type.EntityInfo]:
    sStart = aStart
    sEnd = ( sStart - 1 ) + aTake
    sRank = sStart
    sUserInfoList = []
    for sUser in aUsersData.values():
        if sRank >= sStart and sRank <= sEnd:
            sInfo = { 'Rank': sRank,
                    'Id': sUser['Id'], 
                    'Name': sUser['Name'], 
                    'Trophy': sUser['Trophy'],
                    'LastLoginDate': sUser['LastLoginDate'],
                    'LastHeartBeatDate': sUser['LastHeartBeatDate'] }
            sUserInfoList.append( sInfo )
        sRank = sRank + 1
    
    return sUserInfoList

