import pytz
from typing import Any, Dict, List, Optional, Union

from utils import settings as _settings

# ---------- Time ----------
KST = pytz.timezone( 'Asia/Seoul' )

# ---------- Formatting / Parsing ----------
API_DATETIME_FORMAT_ISO: str = '%Y-%m-%d %H:%M:%S'
API_DATETIME_FORMAT_ISO_DETAILED: str = '%Y-%m-%d %H:%M:%S.%f'
API_DATETIME_FORMAT_CUSTOM: str = '%d.%m.%y %H:%M'

INT_TYPE:int = 0
STR_TYPE:int = 1
DATE_TYPE:int = 2

ZERO_WIDTH_SPACE: str = '\u200b'

EntityInfo = Dict[str, 'EntityInfo']
EntitiesData = Dict[str, EntityInfo]
_EntityDict = Union[List['_EntityDict'], Dict[str, '_EntityDict']]
