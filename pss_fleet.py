from utils import settings as _settings
from typing import Dict, List, Tuple, Optional

# ---------- Constants ----------

FLEET_DESCRIPTION_PROPERTY_NAME: str = 'AllianceName'
FLEET_KEY_NAME: str = 'AllianceId'
FLEET_SHEET_COLUMN_NAMES: Dict[str, Optional[str]] = {
    'Timestamp': _settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Fleet': None,
    'Player name': None,
    'Rank': None,
    'Last Login Date': _settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Trophies': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Max Trophies': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Stars': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Join Date': _settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Crew Donated': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Crew Borrowed': _settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Logged in ago': None,
    'Joined ago': None,
}

