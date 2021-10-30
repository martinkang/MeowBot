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
# 스케줄 종류에는 여러가지가 있는데 대표적으로 BlockingScheduler, BackgroundScheduler 입니다
# BlockingScheduler 는 단일수행에, BackgroundScheduler은 다수 수행에 사용됩니다.
# 여기서는 BackgroundScheduler 를 사용하겠습니다.
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
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
# Temporary User List
#==============================================================================================
sRussian = []
sRussian.append( { 'Id' : '5195724', 'Name' : 'SPACE ENEMY' } )
sRussian.append( { 'Id' : '3433365', 'Name' : 'atomic samurai' } ) 
sRussian.append( { 'Id' : '2135741', 'Name' : 'tezzar' } )
sRussian.append( { 'Id' : '6606727', 'Name' : 'xBiGx' } )
sRussian.append( { 'Id' : '3608200', 'Name' : 'volax' } )
sRussian.append( { 'Id' : '2819541', 'Name' : 'Cpt. Laser Beard' } ) 
sRussian.append( { 'Id' : '4703085', 'Name' : 'Zlоdey' } )
sRussian.append( { 'Id' : '1228935', 'Name' : 'Taska' } )
sRussian.append( { 'Id' : '6420614', 'Name' : 'AlfaR1' } )
sRussian.append( { 'Id' : '3145262', 'Name' : 'Giallar' } )
    
#==============================================================================================
# Bot Commands Sub Functions
#==============================================================================================
async def getUserInfoByFunction( aCtx:context, aTitle:str, aIsNeedShipInfo:bool, aSelectFunc, aFormatFunc ):
    sExactName = str(_discord.get_exact_args(aCtx)).strip()
    sOutputEmbed = None
    async with aCtx.typing():
        sUserInfos = await _user.get_users_infos_by_name( aCtx, sExactName )

    if sUserInfos:
        sNow = _time.get_utc_now()
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


async def getTopUserInfosByFunction( aCtx:context, aTitle:str, aIsNeedShipInfo:bool, aFormatFunc, 
                                    aStart:int = 1, aEnd:int = _settings.SEARCH_TOP_RANK ):
    sOutputEmbed = None
    sStart = aStart
    sEnd = aEnd
    
    async with aCtx.typing():
        sTopUserInfos = await _user._get_top_captains_For_UserInfos( sStart - 1, sEnd ) 
        
    if sTopUserInfos:
        sOutputList = ''
        sRank = sStart
        sNow = _time.get_utc_now()
        
        for sUser in sTopUserInfos:
            sInfosTxt = None
            sIsLogin = False
            sUserInfos = await _user.get_users_infos_by_name( aCtx, sUser['Name'] )  
            try:
                for sUserInfo in sUserInfos:
                    if sUser['Id'] == sUserInfo['Id']:
                        sShipInfo = None
                        if aIsNeedShipInfo is True:
                            sIsLogin = _time.isStilLogin( sNow, sUserInfo['LastLoginDate'], sUserInfo['LastHeartBeatDate'] )
                            if  sIsLogin is not True:
                                sShipInfo = await _ship.get_Inspect_Ship_info( sUserInfo['Id'] )
                                _, sImmunity = _format._get_Immunity( sNow, sShipInfo )
                                if sImmunity is None or sImmunity <= _time.SEARCH_IMMUNITY_PRINT_TIMEOUT:
                                    _, sInfosTxt = aFormatFunc( sNow, sUserInfo, sShipInfo )
                        else:
                            _, sInfosTxt = aFormatFunc( sNow, sUserInfo, None )
                            
                        break    
            except Exception as sEx:
                print( f'getTopUserInfosByFunction Exception {sEx}' )
            
            if sInfosTxt is not None:
                sOutputList = sOutputList + f'{sRank}. {sInfosTxt}' + '\n'
            else:
                if sIsLogin == True:
                    print( f'{sUser["Name"]} 는 로그인 중입니다')
                else:
                    print( f'{sUser["Name"]} 를 찾지 못했습니다')

            sRank = sRank + 1
            if sRank % 10 == 0:
                time.sleep(2)

        sOutputEmbed = discord.Embed(title=aTitle, description=sOutputList, color=0x00aaaa)
    else:
        sInfosTxt = f'Top {_settings.SEARCH_TOP_RANK} 서치가 안됩니다.'
        sOutputEmbed = discord.Embed(title=f'검색 에러', description=sInfosTxt, color=0x00aaaa)
        
    return sOutputEmbed


async def getListUserInfosByFunction( aCtx:context, aUserList, aTitle:str, aIsNeedShipInfo:bool, aFormatFunc ):
    sOutputEmbed = None
    
    async with aCtx.typing():
        sOutputList = ''
        sNow = _time.get_utc_now()
        
        for sUser in aUserList:
            sInfosTxt = None
            sIsLogin = False
            sUserInfos = await _user.get_users_infos_by_name( aCtx, sUser['Name'] )  
            try:
                for sUserInfo in sUserInfos:
                    if sUser['Id'] == sUserInfo['Id']:
                        sShipInfo = None
                        if aIsNeedShipInfo is True:
                            sShipInfo = await _ship.get_Inspect_Ship_info( sUserInfo['Id'] )
                            _, sInfosTxt = aFormatFunc( sNow, sUserInfo, sShipInfo, True )
                        else:
                            _, sInfosTxt = aFormatFunc( sNow, sUserInfo, None, True )
                            
                        break    
            except Exception as sEx:
                print( f'getTopUserInfosByFunction Exception {sEx}' )
            
            if sInfosTxt is not None:
                sOutputList = sOutputList + f'{sInfosTxt}' + '\n'
            else:
                if sIsLogin == True:
                    print( f'{sUser["Name"]} 는 로그인 중입니다')
                else:
                    print( f'{sUser["Name"]} 를 찾지 못했습니다')

        sOutputEmbed = discord.Embed(title=aTitle, description=sOutputList, color=0x00aaaa)
        
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
        sNow = _time.get_utc_now()
        
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


@gBot.event
async def getLastDayStars():# aCtx: context, aDivision:str = None ):
    """
    설명쓰기
    """   

    sChannel = gBot.get_channel(int(os.environ.get( 'RANKING_CANNEL_ID' )))

    sOutputEmbed = None
    sNow = _time.get_utc_now()
    if _time.isTourneyStart():
        sDivisionStars = await pss_tournament.getOnlineDivisionStarsData()
        sFleetDatas = pss_tournament.getOnlineFleetIDs( sDivisionStars )

        sKey = await _func.get_access_key()
        for sFleetData in sFleetDatas:
            if sFleetData[0] == 1:
                sFleetName, sOutputEmbed = await pss_tournament.getStarsEachFleet( sKey, sFleetData[1], sNow )
                sEmb = discord.Embed(title=f'{sFleetName} Stars Score', description=sOutputEmbed, color=0x00aaaa)   
                await sChannel.send(embed=sEmb)
            else:
                break
            #await _discord.reply_with_output( aCtx, sOutputEmbed )

        return
        

            # if aDivision is None:
            #     #전체 리그의 별 갯수
            #     sOutputEmbed = pss_tournament.getOnlineTotalDivisionStars( sDivisionStars )
            # elif pss_tournament.isDivisionLetter(aDivision):
            #     # 리그별 함대의 별 갯수
            #     sOutputEmbed = pss_tournament.getOnlineDivisionStars( aDivision, sDivisionStars )
            # else:
            #     # 함대별 별 갯수
            #     pss_tournament.getOnlineFeetIDs( sDivisionStars )
            #     pss_tournament.getStarsEachFleet( sDivisionStars )
            #     sOutputEmbed = None
    #     else:
    #         sOutputEmbed = None
    #         return
        
    # if sOutputEmbed is not None:
    #     await _discord.reply_with_output( sChannel, sOutputEmbed )
    # else:
    #     sOutputEmbed = discord.Embed(title=f'에러 발생', description="결과를 찾을 수 없습니다", color=0x00aaaa)   
    #     await sChannel.send(embed=sOutputEmbed)
        
    # return
   
@gBot.command(name='토너', aliases=['stars', '별'], brief=['토너 별'] )
async def getLastDayStarsUser( aCtx: context, aDivision:str = None ):
    """
    설명쓰기
    """   
    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )), True )
    if sisAuthorized is not True:
        await aCtx.send("관리자만 이용 가능합니다.")
        return

    async with aCtx.typing():
        sOutputEmbed = None
        sNow = _time.get_utc_now()
        if _time.isTourneyStart():
            sDivisionStars = await pss_tournament.getOnlineDivisionStarsData()
            sFleetDatas = pss_tournament.getOnlineFleetIDs( sDivisionStars )
            
            if aDivision is None:
                sDivision = 1
            else:
                if aDivision.upper() == 'A':
                    sDivision = 1
                elif aDivision.upper() == 'B':
                    sDivision = 2
                elif aDivision.upper() == 'C':
                    sDivision = 3
                elif aDivision.upper() == 'D':
                    sDivision = 4
                else:
                    sDivision = 1

            sKey = await _func.get_access_key()
            for sFleetData in sFleetDatas:
                if sFleetData[0] == sDivision:
                    sFleetName, sOutputEmbed = await pss_tournament.getStarsEachFleet( sKey, sFleetData[1], sNow )
                    sEmb = discord.Embed(title=f'{sFleetName} Stars Score', description=sOutputEmbed, color=0x00aaaa)   
                    await aCtx.send(embed=sEmb)
                else:
                    break

            
        return
    
    
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
async def getUserInfo_top( aCtx: context, aTop = None ):
    """
    설명쓰기
    """   

    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )), False )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널 또는 관리자만 이용 가능합니다.")
        return

    if aTop is None:
        sTop = 30
    else:   
        if aTop.isdigit() == False:
            await aCtx.send("검색하고 싶은 순위를 최대 50까지 입력하세요.")
            return
        else:
            sTop = int(aTop)
            if sTop > _settings.SEARCH_TOP_RANK:
                await aCtx.send( f'랭킹값이 {_settings.SEARCH_TOP_RANK } 보다 크면 {_settings.SEARCH_TOP_RANK } 으로 대체됩니다.')
                sTop = _settings.SEARCH_TOP_RANK

    start = time.time()
    async with aCtx.typing():
        try:
            sOutputEmbed = await getTopUserInfosByFunction( aCtx, 
                                                            f'랭킹. 유저(함대) / 트로피 / 접속 / 보호막',
                                                            NEED_SHIP_INFO, 
                                                            _format.create_User_Immunity,
                                                            aEnd = sTop )  
            sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다. / 보호막이 3시간 이하로 남은 유저만 표기됩니다.")
        except Exception as sERR:
            sErrTxt = f'에러발생 : {sERR}'
            sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
            
        await aCtx.send(embed=sOutputEmbed)
    print( f'Sync Time : {time.time() - start}')
        

@getUserInfo.group(name='러시안', aliases=['russian'], brief=['러시안 플레이어 보호막 정보'], invoke_without_command=True)
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
            sOutputEmbed = await getListUserInfosByFunction( aCtx, 
                                                            sRussian,
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
async def getUserAliveInfo_top( aCtx: context, aTop = None):
    """
    설명쓰기
    """      
    sisAuthorized = isAuthorized( aCtx, str(os.environ.get( 'MEOW_CHANNEL_ID' )), False )
    if sisAuthorized is not True:
        await aCtx.send("현재는 냥냥봇 채널 또는 관리자만 이용 가능합니다.")
        return
    
    if aTop is None:
        sTop = 30
    else:   
        if aTop.isdigit() == False:
            await aCtx.send("검색하고 싶은 순위를 최대 50까지 입력하세요.")
            return
        else:
            sTop = int(aTop)
            if sTop > _settings.SEARCH_TOP_RANK:
                await aCtx.send( f'랭킹값이 {_settings.SEARCH_TOP_RANK } 보다 크면 {_settings.SEARCH_TOP_RANK } 으로 대체됩니다.')
                sTop = _settings.SEARCH_TOP_RANK

    async with aCtx.typing():
        try:
            sOutputEmbed = await getTopUserInfosByFunction( aCtx, 
                                                            f'랭킹. 유저(함대) / 트로피 / 접속',
                                                            DO_NOT_NEED_SHIP_INFO, 
                                                            _format.create_User_Alive,
                                                            aEnd = sTop )  
            sOutputEmbed.set_footer(text="약 3분 정도 오차가 존재할 수 있습니다.")
        except Exception as sERR:
            sErrTxt = f'에러발생 : {sERR}'
            sOutputEmbed = discord.Embed(title=f'에러 발생', description=sErrTxt, color=0x00aaaa)   
        
        await aCtx.send(embed=sOutputEmbed)

  
#==============================================================================================
# Initialize Bot
#==============================================================================================
@gBot.event
async def on_ready():
    print( 'Logged in as' )
    print( 'User Name : ' + gBot.user.name )
    print( 'Bot ID    : ' + str(gBot.user.id) )
    print( '--------------' )
    
    #sched = AsyncIOScheduler(timezone='UTC')
    #sched = BackgroundScheduler(timezone='UTC')
    #sched.start()
    #sched.add_job( getLastDayStars, 'cron', hour='23', minute='55', id="touney_save" )
    print( 'Tourney Schedule Start' )
    

@tasks.loop(seconds=10)
async def pingDatatbase():
    await db.pingConnectDB()


async def initBot(): 
    print( 'init Bot' )
    try:
        _time.init()
        print( 'Time Function initilaize Success' )
        _func.init()
        print( 'Internal Function initilaize Success' )
        await db._init()
        print( 'Database initilaize Success' )            
        #await pss_tournament.initTourneyDB()
        #print( 'Tournament Data initilaize Success' )
        print( 'init Bot Success' )
    except Exception as sEx:
        print( 'init Bot Failure : ' + str(sEx) )
        sys.exit()

    sKey = await _func.get_access_key()
    print( "initBot AccessKey : ", sKey )
   
if sys.platform == 'win32':
    # Set the policy to prevent "Event loop is closed" error on Windows - https://github.com/encode/httpx/issues/914
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
if __name__ == "__main__":  
    asyncio.run( initBot() )
     
#asyncio.create_task(pingDatatbase())
gBot.run( os.environ.get('MEOW_BOT_TOKEN') )

