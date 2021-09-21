from urllib.parse import quote as _quote
from xml.etree import ElementTree as _ElementTree
from typing import Dict, List

import pss_data as _pas_data
from utils import type as _type
from utils import time as _time

def raw_xml_to_dict(raw_xml: str, include_root: bool = True, fix_attributes: bool = True, preserve_lists: bool = False) -> _type._EntityDict:
    root = _ElementTree.fromstring(raw_xml)
    result = __convert_xml_to_dict(root, include_root=include_root, fix_attributes=fix_attributes, preserve_lists=preserve_lists)
    return result


def __xmltree_to_dict(raw_text: str, depth: int) -> _type.EntitiesData:
    result = raw_xml_to_dict(raw_text)
    while depth > 0:
        found_new_root = False
        for value in result.values():
            if isinstance(value, dict):
                result = value
                depth -= 1
                found_new_root = True
                break
        if not found_new_root:
            return {}
    return result


def __fix_attribute(attribute: Dict[str, str]) -> Dict[str, str]:
    if not attribute:
        return None

    result = {}

    for key, value in attribute.items():
        if key.endswith('Xml') and value:
            raw_xml = value
            fixed_value = raw_xml_to_dict(raw_xml)
            result[key[:-3]] = fixed_value

        result[key] = value

    return result
    
def __convert_xml_to_dict(root: _ElementTree.Element, include_root: bool = True, fix_attributes: bool = True, preserve_lists: bool = False) -> _type._EntityDict:
    if root is None:
        return None

    result = {}
    if root.attrib:
        if include_root:
            if fix_attributes:
                result[root.tag] = __fix_attribute(root.attrib)
            else:
                result[root.tag] = root.attrib
        else:
            if fix_attributes:
                result = __fix_attribute(root.attrib)
            else:
                result = root.attrib
    elif include_root:
        result[root.tag] = {}

    # Retrieve all distinct names of sub tags
    tag_count_map = __get_child_tag_count(root)
    children_dict = {}

    for child in root:
        tag = child.tag
        key = None
        if tag_count_map[tag] > 1:
            id_attr_names = _pas_data.ID_NAMES_INFO.get(tag)
            if id_attr_names:
                id_attr_values = [child.attrib[id_attr_name] for id_attr_name in id_attr_names]
                key = '.'.join(sorted(id_attr_values))
        if not key:
            key = tag

        child_dict = __convert_xml_to_dict(child, include_root=False, fix_attributes=fix_attributes, preserve_lists=preserve_lists)
        if key not in children_dict.keys():
            children_dict[key] = child_dict

    if children_dict:
        if preserve_lists:
            if len(children_dict) > 1:
                children_list = list(children_dict.values())
                if include_root:
                    result[root.tag] = children_list
                else:
                    if result:
                        result['Collection'] = children_list
                    else:
                        result = children_list
            else:
                result.setdefault(root.tag, {}).update(children_dict)
        else:
            if include_root:
                # keys get overwritten here
                result[root.tag] = children_dict
            else:
                result.update(children_dict)

    return result

def __get_child_tag_count(root: _ElementTree.Element) -> Dict[str, int]:
    if root is None:
        return None

    child_tags = list(set([child_node.tag for child_node in root]))
    result = {}
    for child_tag in child_tags:
        result[child_tag] = sum(1 for child_node in root if child_node.tag == child_tag)

    return result

def formatted_datetime(date_time: str, include_time: bool = True, include_tz: bool = True, include_tz_brackets: bool = True) -> _time.datetime:
    format_string = '%Y-%m-%d'
    if include_time:
        format_string += ' %H:%M:%S'
    if include_tz:
        if include_tz_brackets:
            format_string += ' (%Z)'
        else:
            format_string += ' %Z'
    result = _time.datetime.strptime(date_time, format_string)
    if result.tzinfo is None:
        result = result.replace(tzinfo=_time._timezone.utc)
    return result

def pss_datetime(pss_datetime: str) -> _time.datetime:
    result = None
    if pss_datetime:
        try:
            result = _time.datetime.strptime(pss_datetime, _type.API_DATETIME_FORMAT_ISO)
        except ValueError:
            result = _time.datetime.strptime(pss_datetime, _type.API_DATETIME_FORMAT_ISO_DETAILED)
        result = _time._pytz.utc.localize(result)
    return result
