from datetime import datetime
from time import time
import sys
import os
from utils.settings import TOURNAMENT_DATA_START_DATE
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from . import type as _type
from . import functions as _func
from . import time as _time
from . import emojis as _emojis


def create_User_Info( aUserInfo: _type.EntityInfo) -> str:
    print(aUserInfo)
    sID = aUserInfo['Id']
    sName = aUserInfo['Name']
    sCreate = aUserInfo['CreationDate']
    
    sNow = _time.get_now()  
    sLastLogin = _time.get_TimeAsTimeZone( aUserInfo['LastLoginDate'] )
    sLastHeartBeat = _time.get_TimeAsTimeZone( aUserInfo['LastHeartBeatDate'] )
    sTrophy = aUserInfo['Trophy']
    sFleet, sFleetClass = _get_FleetNClass( aUserInfo )

    sPvpAtkWin = aUserInfo['PVPAttackWins']
    sPvpAtkLose = aUserInfo['PVPAttackLosses'] 
    sPvpAtkDraw = aUserInfo['PVPAttackDraws'] 
    sPvpDfcWin = aUserInfo['PVPDefenceWins'] 
    sPvpDfcLose = aUserInfo['PVPDefenceLosses'] 
    sPvpDfcDraw = aUserInfo['PVPDefenceDraws'] 
    sInfosTxt = "ID : " + sID + "\n" + \
        "유저 : " + sName + "\n" + \
        "트로피 : " + sTrophy + "\n" + \
        "생성일 : " + sCreate + "\n" +\
        "마지막 로그인 : " + _time.get_time_diff( sLastLogin, sNow ) + "\n" + \
        "마지막 통신 : " + _time.get_time_diff( sLastHeartBeat, sNow ) + "\n" + \
        "함대 : " + sFleet + sFleetClass + "\n" + \
        "PVP 공격 승리/패배/무승부 : " + sPvpAtkWin + "/" +  sPvpAtkLose + "/" +  sPvpAtkDraw + "\n" + \
        "PVP 방어 승리/패배/무승부 : " + sPvpDfcWin + "/" +  sPvpDfcLose + "/" +  sPvpDfcDraw
        
    return sInfosTxt



def create_User_Alive( aNow: datetime, aUserInfo: _type.EntityInfo, _: _type.EntityInfo, aDetail = False  ) -> str:
    sErrMsg = None
    try:
        sID = aUserInfo['Id']
        sName = aUserInfo['Name']

        sPvpAtkWin = aUserInfo['PVPAttackWins']
        sPvpAtkLose = aUserInfo['PVPAttackLosses'] 
        sPvpAtkDraw = aUserInfo['PVPAttackDraws'] 
        sPvpDfcWin = aUserInfo['PVPDefenceWins'] 
        sPvpDfcLose = aUserInfo['PVPDefenceLosses'] 
        sPvpDfcDraw = aUserInfo['PVPDefenceDraws'] 

        sFleet, _ = _get_FleetNClass( aUserInfo )
        sTrophy = aUserInfo['Trophy']
        
        sIsStilLogin = None
        if _time.isStilLogin( aNow, aUserInfo['LastLoginDate'], aUserInfo['LastHeartBeatDate'] ) is True:
            sHeart = _emojis.pss_heartbeat
            sIsStilLogin = '접속'
        else:
            sHeart = _emojis.pss_deadHeart
            sIsStilLogin = '미접'
            

        _func.debug_log("create_User_Alive", f'{sID} / {sName}{sFleet} / {_emojis.trophy}{sTrophy} / {sHeart}{sIsStilLogin}')
    except Exception as sEx:
        sErrMsg = str(sEx)
        print( sErrMsg )
        
    sInfoTxt = ''
    if aDetail:
        sInfoTxt = f'{sID} / {sName}{sFleet} / {_emojis.trophy}{sTrophy} / {sHeart}{sIsStilLogin}' + '\n' + \
                f'공격 승 / 패 / 무승부 : {sPvpAtkWin} / {sPvpAtkLose} / {sPvpAtkDraw}' + '\n' + \
                f'방어 승 / 패 / 무승부 : {sPvpDfcWin} / {sPvpDfcLose} / {sPvpDfcDraw}'
    else:
        sInfoTxt = f'{sID} / {sName}{sFleet} / {_emojis.trophy}{sTrophy} / {sHeart}{sIsStilLogin}'

    return sErrMsg, sInfoTxt



def create_User_List( aNo: int, aUserInfo: _type.EntityInfo) -> str:
    sName = aUserInfo['Name']
    sTrophy = aUserInfo['Trophy']
    sAliance, _ = _get_FleetNClass( aUserInfo )
        
    return f'{aNo}. {sName} {sAliance} {_emojis.trophy} {sTrophy}'



def _get_LastHeartBeat( aNow:datetime, aUserInfo: _type.EntityInfo ) ->datetime:
    sLastBeat = ""
    sLastLogin = _time.get_BotTimeUTCFormat( aUserInfo['LastLoginDate'] )
    sLastHeartBeat = _time.get_BotTimeUTCFormat( aUserInfo['LastHeartBeatDate'] )
    
    if sLastLogin > sLastHeartBeat:
        sLastBeat = _time.get_time_diff( sLastLogin, aNow )
    else:
        sLastBeat = _time.get_time_diff( sLastHeartBeat, aNow )
        
    return sLastBeat



def create_User_Immunity( aNow:datetime, aUserInfo: _type.EntityInfo, aShipInfo: _type.EntityInfo, aDetail = False ) -> str:
    sName = aUserInfo['Name']
    sPvpAtkWin = aUserInfo['PVPAttackWins']
    sPvpAtkLose = aUserInfo['PVPAttackLosses'] 
    sPvpAtkDraw = aUserInfo['PVPAttackDraws'] 
    sPvpDfcWin = aUserInfo['PVPDefenceWins'] 
    sPvpDfcLose = aUserInfo['PVPDefenceLosses'] 
    sPvpDfcDraw = aUserInfo['PVPDefenceDraws'] 
    
    _func.debug_log("create_User_Immunity", f'Name : {sName}')
    
    sImmunity: datetime
    sImmunityStr: str
    sErrMsg = None
    sBold = ""
    sUnderLine = ""
    sItalic = ""
    
    if aShipInfo is None:
        print( f'{sName} create_User_Immunity ----')
        sImmunityStr = '-'
    else:
        print( f'{sName} create_User_Immunity')
        sErrMsg, sImmunity = _get_Immunity( aNow, aShipInfo )
        print( f'{sName} create_User_Immunity after _get_immu')
        if sErrMsg is not None:
            print( "create_User_Immunity Error Message : " + sErrMsg )
            return sErrMsg, None

        print( "after get immun ===========================================")
        
        if sImmunity is None:
            sImmunityStr = '없음'
            sUnderLine = "__"
            sBold = "**"
            sItalic = "*"
            print( "immun is none ===========================================")
        else:
            print( "immun is not none ===========================================")
            if sImmunity <= _time.SEARCH_IMMUNITY_SOON_TIMEOUT:
                sUnderLine = "__"
                
            if sImmunity <= _time.SEARCH_IMMUNITY_TIMEOUT:
                sBold = "**"
            
            print( "before sImmunityStr ===========================================")
            sImmunityStr = getTimeFormat( sImmunity )
            print( "create_User_Immunity sImmunityStr : " + sImmunityStr)

    sFleet, _ = _get_FleetNClass( aUserInfo )
    sTrophy = aUserInfo['Trophy']
    print( "create_User_Immunity Trophy " + str(sTrophy ) )
    
    sHeart = None
    sIsStilLogin = None
    if _time.isStilLogin( aNow, aUserInfo['LastLoginDate'], aUserInfo['LastHeartBeatDate'] ) is True:
        sHeart = _emojis.pss_heartbeat
        sIsStilLogin = '접속'
    else:
        sHeart = _emojis.pss_deadHeart
        sIsStilLogin = '미접'

    sInfosTxt = ''
    if aDetail:
        sInfosTxt = f'{sItalic}{sUnderLine}{sBold}{sName}{sFleet} / {_emojis.trophy}{sTrophy} / {sHeart}{sIsStilLogin} / {_emojis.pss_shield}{sImmunityStr}{sBold}{sUnderLine}{sItalic}' + '\n' + \
                    f'공격 승 / 패 / 무승부 : {sPvpAtkWin} / {sPvpAtkLose} / {sPvpAtkDraw}' + '\n' + \
                    f'방어 승 / 패 / 무승부 : {sPvpDfcWin} / {sPvpDfcLose} / {sPvpDfcDraw}'
    else:
        sInfosTxt = f'{sItalic}{sUnderLine}{sBold}{sName}{sFleet} / {_emojis.trophy}{sTrophy} / {sHeart}{sIsStilLogin} / {_emojis.pss_shield}{sImmunityStr}{sBold}{sUnderLine}{sItalic}'

    return sErrMsg, sInfosTxt


def _get_Immunity( aNow:datetime, aInfo: _type.EntityInfo ) ->datetime:
    sTime = ""
    sErrMsg = None
    
    _func.debug_log( "_get_Immunity", f"aInfo Immun : {aInfo['ImmunityDate']} Now : {aNow}")
    
    if 'ImmunityDate' in aInfo:
        sImmunity = _time.get_BotTimeUTCFormat( aInfo['ImmunityDate'] )

        if sImmunity > aNow:
            sTime = _time.get_time_diff( sImmunity, aNow )
        else:
            sTime = None
    else:
        sTime = None
        sErrMsg = "ImmunityDate 를 찾을 수 없습니다. 다시한번 시도해보세요."
        
    _func.debug_log( "_get_Immunity", f'Immun : {sImmunity}  Time : {sTime} Now : {aNow}')

    return sErrMsg, sTime


def getTimeFormat( aTime: datetime )->str:
    if aTime > _time.ONE_WEEK:
        sResult = f'약 {int(aTime.days / 7)}주'
    elif aTime > _time.ONE_DAY:
        sResult = f'약 {int(aTime.days)}일'
    elif aTime > _time.ONE_HOUR:
        sResult = f'{int(aTime.seconds / 3600)}시간 {int(aTime.seconds % 3600 / 60)}분'
    elif aTime > _time.ONE_MINUTE:
        sResult = f'{int(aTime.seconds / 60)}분'
    else:
        sResult = f'1분 미만'
    return sResult
    
    
def _get_FleetNClass( aUserInfo: _type.EntityInfo ):
    sAliance = ""
    sClass = ""
    if 'AllianceName' in aUserInfo:
        sAliance = "(" + aUserInfo['AllianceName'] + ")"
    else:
        sAliance = ""
    return sAliance, sClass