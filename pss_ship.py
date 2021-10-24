from utils import path as _path
from utils import functions as _func
from utils import parse as _parse

async def get_Inspect_Ship_info( aID ):
    _func.debug_log("get_Inspect_Ship_info", f'ID : {aID}')
    sKey = await _func.get_access_key()
    sPath = await _path.__get_inspect_ship_base_path( sKey, aID )
    raw_data = await _func.get_data_from_path( sPath )
    sShipInfo = _parse.__xmltree_to_dict( raw_data, 2 )
    
    return sShipInfo.get('Ship', None)