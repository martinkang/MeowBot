# ---------- Constants ----------

FLEET_DESCRIPTION_PROPERTY_NAME: str = 'AllianceName'
FLEET_KEY_NAME: str = 'AllianceId'
FLEET_SHEET_COLUMN_NAMES: Dict[str, Optional[str]] = {
    'Timestamp': settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Fleet': None,
    'Player name': None,
    'Rank': None,
    'Last Login Date': settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Trophies': settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Max Trophies': settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Stars': settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Join Date': settings.EXCEL_COLUMN_FORMAT_DATETIME,
    'Crew Donated': settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Crew Borrowed': settings.EXCEL_COLUMN_FORMAT_NUMBER,
    'Logged in ago': None,
    'Joined ago': None,
}

