import sys
from asyncio.tasks import sleep
import datetime 
from typing import Dict, List, Tuple


# --------------- Utils ---------------
from utils import functions as _func
from utils import database as db
from utils import path as _path
from utils import discord as _discord
from utils import format as _format

# --------------- Schedule --------------- 

import time

# --------------- User Module ---------------
import pss_user as _user
import pss_ship as _ship
from utils import settings as _settings

from utils import type as _type

# --------------- Discord -------------------
import discord, os
import asyncio
from discord import ChannelType, Message, Reaction, User
from discord.ext import commands, tasks
from discord.ext.commands import Context, context
from utils import time as _time



import pss_tournament


#==============================================================================================
# Constant
#==============================================================================================
NEED_SHIP_INFO: bool = True
DO_NOT_NEED_SHIP_INFO: bool = False

#==============================================================================================
# Global Variables
#==============================================================================================
gBot = commands.Bot(command_prefix='-', status=discord.Status.online, activity=discord.Game("-냥냥냥") )



#==============================================================================================
# Bot Commands Sub Functions
#==============================================================================================
async def getUserInfoByFunction( aCtx:context, aTitle:str, aIsNeedShipInfo:bool, aSelectFunc, aFormatFunc ):
    sExactName = str(_discord.get_exact_args(aCtx)).strip()
    sOutputEmbed = None
    async with aCtx.typing():
        sUserInfos = await _user.get_users_infos_by_name( aCtx, sExactName )

    if sUserInfos:
        sNow = _time.get_now()
        sErrMsg, sOutput = await _user._getUserInfoByFunction( aCtx,
                                                            sExactName,
                                                            sNow,
                                                            sUserInfos,
                                                            aIsNeedShipInfo,
                                                            aSelectFunc,
                                                            aFormatFunc )
        
        if sErrMsg is None and sOutput is not None:
            sOutputEmbed = discord.Embed(title=aTitle, description=sOutput, color=0x00aaaa)
        else:
            sOutputEmbed = discord.Embed(title=f'선택 에러', description=sErrMsg, color=0x00aaaa) 
    else:
        sInfosTxt = f'유저 {sExactName} 가 존재하지 않습니다.'
        sOutputEmbed = discord.Embed(title=f'검색 에러', description=sInfosTxt, color=0x00aaaa)
        
    return sOutputEmbed


async def getTopUserInfosByFunction( aCtx:context, aTitle:str, aIsNeedShipInfo:bool, aFormatFunc ):
    sOutputEmbed = None
    sStart = 1
    sEnd = _settings.SEARCH_TOP_RANK
    
    async with aCtx.typing():
        sTopUserInfos = await _user._get_top_captains_For_UserInfos( sStart - 1, sEnd ) 
        
    if sTopUserInfos:
        sOutputList = ''
        sRank = sStart
        sNow = _time.get_now()
        
        for sUser in sTopUserInfos:
            sInfosTxt = None
            sUserInfos = await _user.get_users_infos_by_name( aCtx, sUser['Name'] )  
            try:
                for sUserInfo in sUserInfos:
                    if sUser['Id'] == sUserInfo['Id']:
                        sShipInfo = None
                        if aIsNeedShipInfo is True:
                            if _time.isStilLogin( sNow, sUserInfo['LastLoginDate'], sUserInfo['LastHeartBeatDate'] ) is not True:
                                sShipInfo = await _ship.get_Inspect_Ship_info( sUserInfo['Id'] )
                                # _, sInfosTxt = aFormatFunc( sNow, sUserInfo, sShipInfo )
                                _, sImmunity = _format._get_Immunity( sNow, sShipInfo )
                                if sImmunity is None or sImmunity <= _time.SEARCH_IMMUNITY_PRINT_TIMEOUT:
                                    _, sInfosTxt = aFormatFunc( sNow, sUserInfo, sShipInfo )
                            else:
                                sInfosTxt = None
                                # _, sInfosTxt = aFormatFunc( sNow, sUserInfo, None )
                        else:
                            _, sInfosTxt = aFormatFunc( sNow, sUserInfo, None )
                            
                        break    
            except Exception as sEx:
                sInfosTxt = None
                print( f'getTopUserInfosByFunction Exception {sEx}' )
            
            if sInfosTxt is not None:
                sOutputList = sOutputList + f'{sRank}. {sInfosTxt}' + '\n'
            sRank = sRank + 1

        sOutputEmbed = discord.Embed(title=aTitle, description=sOutputList, color=0x00aaaa)
    else:
        sInfosTxt = f'Top {_settings.SEARCH_TOP_RANK} 서치가 안됩니다.'
        sOutputEmbed = discord.Embed(title=f'검색 에러', description=sInfosTxt, color=0x00aaaa)
        
    return sOutputEmbed


async def getAsyncTopUserInfosByFunction( aCtx:context, aTitle:str, aIsNeedShipInfo:bool, aFormatFunc ):
    sOutputEmbed = None
    sStart = 1
    sEnd = _settings.SEARCH_TOP_RANK
    
    async with aCtx.typing():
        sTopUserInfos = await _user._get_top_captains_For_UserInfos( sStart - 1, sEnd ) 
        
    if sTopUserInfos:
        sOutputList = ''
        sRank = sStart
        sNow = _time.get_now()
        
        sUserInfos = []
        sUserList = []
        for sTopUser in sTopUserInfos:
            sUserList.append( await _user.get_users_infos_by_name( aCtx, sTopUser['Name'] ) )
        
        sIdx = 0
        for sTopUser in sTopUserInfos:
            for sUserInfo in sUserList[sIdx]:
                if sTopUser['Id'] == sUserInfo['Id']: 
                    _func.debug_log( "getAsyncTopUserInfosByFunction UserList append", sUserInfo['Name'] )
                    sUserInfos.append( sUserInfo )
                    break
            sIdx = sIdx + 1

        for sUser in sUserInfos:
            _func.debug_log( "getAsyncTopUserInfosByFunction UserInfos", sUser['Name'] )
            sInfosTxt = None 
            sShipInfo = None
            
            try:
                if aIsNeedShipInfo is True:
                    if _time.isStilLogin( sNow, sUser['LastLoginDate'], sUser['LastHeartBeatDate'] ) is not True:
                        sShipInfo = await _ship.get_Inspect_Ship_info( sUser['Id'] )
                        _, sImmunity = _format._get_Immunity( sNow, sShipInfo )
                        if sImmunity is None or sImmunity <= _time.SEARCH_IMMUNITY_SOON_TIMEOUT:
                            _, sInfosTxt = aFormatFunc( sNow, sUser, sShipInfo )
                    else:
                        sInfosTxt = None
                else:
                    _, sInfosTxt = aFormatFunc( sNow, sUser, None )

            except Exception as sEx:
                sInfosTxt = None
                print( f'getAsyncTopUserInfosByFunction Exception {sEx}' )
            
            if sInfosTxt is not None:
                sOutputList = sOutputList + f'{sRank}. {sInfosTxt}' + '\n'
            sRank = sRank + 1

        sOutputEmbed = discord.Embed(title=aTitle, description=sOutputList, color=0x00aaaa)
    else:
        sInfosTxt = f'Top {_settings.SEARCH_TOP_RANK} 서치가 안됩니다.'
        sOutputEmbed = discord.Embed(title=f'검색 에러', description=sInfosTxt, color=0x00aaaa)
        
    return sOutputEmbed



def isAuthorized( aCtx:context, aChannelID:str, aIsOnlyAdmin:bool = False) -> bool:
    sIsAuthor = False
    
    if str(aCtx.author.id) == str(os.environ.get('ADMIN_ID')):
        sIsAuthor = True
        
    if aIsOnlyAdmin is not True:  
        if str(aCtx.channel.id) == aChannelID:
            sIsAuthor = True
        
    return sIsAuthor

#==============================================================================================
# Bot Commands
#==============================================================================================
@gBot.command(name='저장', aliases=['save', 'u'], brief=['플레이어 리스트 저장'] )
async def saveUserList( aCtx: Context ):   
    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )) )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널에서만 이용 가능합니다.")
    return


@gBot.command(name='리스트', aliases=['목록', 'list'], brief=['저장된 플레이어 리스트'] )
async def getUserList( aCtx: Context ):   
    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )) )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널에서만 이용 가능합니다.")
        
    return


@gBot.command(name='테스트', aliases=['test'], brief=['테스트'] )
async def getU( aCtx: context ):
    """
    설명쓰기
    """   

    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )), False )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널 또는 관리자만 이용 가능합니다.")
        return
    
    start = time.time()  
    async with aCtx.typing():
        try:
            sOutputEmbed = await _user.get_User_infos_by_Fleet_ID( aCtx, '43692')
            sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다. / 접속중이면 보호막은 - 로 표기됩니다")
        except Exception as sERR:
            sErrTxt = f'에러발생 : {sERR}'
            sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
            
        await aCtx.send(embed=sOutputEmbed)
    print( f'ASync Time : {time.time() - start}')


@gBot.command(name='토너', aliases=['stars', '별'], brief=['토너 별'] )
async def getU( aCtx: context ):
    """
    설명쓰기
    """   

    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )), False )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널 또는 관리자만 이용 가능합니다.")
        return
    
    # if _time.get_current_tourney_start():
    #     async with aCtx.typing():
    #          if not pss_tournament.is_valid_division_letter(division):
    #         try:
    #             sOutputEmbed = await _user.get_User_infos_by_Fleet_ID( aCtx, '43692')
    #             sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다. / 접속중이면 보호막은 - 로 표기됩니다")
    #         except Exception as sERR:
    #             sErrTxt = f'에러발생 : {sERR}'
    #             sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
                
    #         await aCtx.send(embed=sOutputEmbed)
    # else:
    #     sErrTxt = '지금은 토너먼트 기간이 아닙니다'
    #     sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
    #     return
   
    
@gBot.group(name='보호막', aliases=['이뮨', 'immunity', '방어'], brief=['플레이어 보호막 정보'], invoke_without_command=True )
async def getUserInfo( aCtx: Context ):         
    """
    설명쓰기
    """
    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )) )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널에서만 이용 가능합니다.")
        return
    
    sOutputEmbed = await getUserInfoByFunction( aCtx, 
                                                f'유저(함대) / 트로피 / 접속 / 보호막',  
                                                NEED_SHIP_INFO,
                                                _user.get_Selected_User_N_Ship_Info,
                                                _format.create_User_Immunity )  
    sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다. / 접속중이면 보호막은 - 로 표기됩니다")
    
    await aCtx.send(embed=sOutputEmbed)
    return


@getUserInfo.group(name='탑', aliases=['랭킹', '랭커', 'top', 'rank'], brief=['탑 플레이어 보호막 정보'], invoke_without_command=True)
async def getUserInfo_top( aCtx: context ):
    """
    설명쓰기
    """   

    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )), False )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널 또는 관리자만 이용 가능합니다.")
        return

    start = time.time()
    async with aCtx.typing():
        try:
            sOutputEmbed = await getTopUserInfosByFunction( aCtx, 
                                                            f'랭킹. 유저(함대) / 트로피 / 접속 / 보호막',
                                                            NEED_SHIP_INFO, 
                                                            _format.create_User_Immunity )  
            sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다. / 보호막이 3시간 이하로 남은 유저만 표기됩니다.")
        except Exception as sERR:
            sErrTxt = f'에러발생 : {sERR}'
            sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
            
        await aCtx.send(embed=sOutputEmbed)
    print( f'Sync Time : {time.time() - start}')
        


@gBot.group(name='접속', aliases=['생존', 'alive', 'heartbeat'], brief=['플레이어 접속 정보'], invoke_without_command=True )
async def getUserAliveInfo( aCtx: Context ):   
    """
    설명쓰기
    """      
    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )) )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널에서만 이용 가능합니다.")
        return
    
    sOutputEmbed = await getUserInfoByFunction( aCtx, 
                                                f'ID / 유저(함대) / 트로피 / 접속',
                                                DO_NOT_NEED_SHIP_INFO, 
                                                _user.get_Selected_User_Alive_Info, 
                                                _format.create_User_Alive )  
    sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다.")
    
    await aCtx.send(embed=sOutputEmbed)

    return

@getUserAliveInfo.group(name='탑', aliases=['랭킹', '랭커', 'top', 'rank'], brief=['탑 플레이어 보호막 정보'], invoke_without_command=True)
async def getUserAliveInfo_top( aCtx: context ):
    """
    설명쓰기
    """      
    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )), False )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널 또는 관리자만 이용 가능합니다.")
        return
    
    async with aCtx.typing():
        try:
            sOutputEmbed = await getTopUserInfosByFunction( aCtx, 
                                                            f'랭킹. 유저(함대) / 트로피 / 접속',
                                                            DO_NOT_NEED_SHIP_INFO, 
                                                            _format.create_User_Alive )  
            sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다.")
        except Exception as sERR:
            sErrTxt = f'에러발생 : {sERR}'
            sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
        
        await aCtx.send(embed=sOutputEmbed)


#==============================================================================================
# Schedule
#==============================================================================================
@tasks.loop(minute=5)
def saveLastDayTourneyStars():
    
    # if _time.get_current_tourney_start:
    #     sNow = _time.get_utc_now()
    #     if sNow.hour == 23 and sNow.minute > 55:

        
    # else:
    #     return

#==============================================================================================
# Initialize Bot
#==============================================================================================
@gBot.event
async def on_ready():
    print( 'Logged in as' )
    print( 'User Name : ' + gBot.user.name )
    print( 'Bot ID    : ' + str(gBot.user.id) )
    print( '--------------' )


async def initBot():
    print( 'init Bot' )
    try:
        _time.init()
        print( 'Time Function initilaize Success' )
        _func.init()
        print( 'Internal Function initilaize Success' )
        await db._init()
        print( 'Database initilaize Success' )
        await pss_tournament.initTourneyDB()
        print( 'Tournament Data initilaize Success' )

        print( 'init Bot Success' )
    except Exception as sEx:
        print( 'init Bot Failure : ' + str(sEx) )
        sys.exit()

    sKey = await _func.get_access_key()
    print( "initBot AccessKey : ", sKey )
   

if __name__ == "__main__":
    asyncio.run( initBot() )
    
gBot.run( os.environ.get('MEOW_BOT_TOKEN') )

