import pytz
from typing import Any, Dict, List, Optional, Union

from utils import settings as _settings

# ---------- Time ----------
KST = pytz.timezone( 'Asia/Seoul' )

# ---------- Formatting / Parsing ----------
API_DATETIME_FORMAT_ISO: str = '%Y-%m-%dT%H:%M:%S'
API_DATETIME_FORMAT_ISO_DETAILED: str = '%Y-%m-%dT%H:%M:%S.%f'
API_DATETIME_FORMAT_CUSTOM: str = '%d.%m.%y %H:%M'

EntityInfo = Dict[str, 'EntityInfo']
EntitiesData = Dict[str, EntityInfo]
_EntityDict = Union[List['_EntityDict'], Dict[str, '_EntityDict']]

USER_DESCRIPTION_PROPERTY_NAME = 'Name'
USER_KEY_NAME = 'Id'

FLEET_DESCRIPTION_PROPERTY_NAME: str = 'AllianceName'
FLEET_KEY_NAME: str = 'AllianceId'
FLEET_SHEET_COLUMN_NAMES: Dict[str, Optional[str]] = {
    'Timestamp': _settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Fleet': None,
    'Player name': None,
    'Rank': None,
    'Last Login Date': _settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Last HeartBeat Date': _settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Trophies': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Max Trophies': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Stars': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Join Date': _settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Crew Donated': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Crew Borrowed': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Logged in ago': None,
    'Joined ago': None,
}
