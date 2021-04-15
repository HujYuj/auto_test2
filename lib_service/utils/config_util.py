# -*- coding: utf-8 -*-
"""
    :author: Wang, Fuqiang Q. (NSB - CN/Hangzhou) <fuqiang.q.wang@nokia-sbell.com>
"""
import os
import json
import ast

lib_root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
file = os.path.join(lib_root_path, 'Output', '.env_cfg')
web_params_file = os.path.join(lib_root_path, 'Output', '.web_params')

def store_web_params(json_data):
    print(web_params_file)
    store_cfg(json_data, web_params_file)

def load_web_params():
    return load_cfg(web_params_file)

def store_cfg(json_data, file_path=None):
    if file_path is None:
        file_path = file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    stored_cfg = load_cfg(file_path)
    if stored_cfg is not None:
        json_data = {**stored_cfg, **json_data}

    with open(file_path, 'w+', encoding='utf-8') as outfile:
        convert_value_type_to_str(json_data)
        json.dump(json_data, outfile)

def load_cfg(file_path=None):
    raw_data = load_raw_cfg(file_path)
    json_data = None
    if raw_data is not None:
        json_data = json.loads(raw_data)
        convert_value_type_to_list(json_data)
    return json_data


def load_raw_cfg(file_path=None):
    if file_path is None:
        file_path = file
    data = None
    if os.path.isfile(file_path) and os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as file_o:
            data = file_o.read()
    return data

def convert_value_type_to_list(dict_obj: dict):
    if dict_obj is not None and len(dict_obj) > 0:
        for k, v in dict_obj.items():
            if isinstance(v, str) and v.startswith("[") and v.endswith("]"):
                v = ast.literal_eval(v)
                dict_obj.update({k: v})

def convert_value_type_to_str(dict_obj: dict):
    if dict_obj is not None and len(dict_obj) > 0:
        for k, v in dict_obj.items():
            if isinstance(v, list):
                v = str(v)
                dict_obj.update({k: v})

def get_abil_slot() -> str:
    filePath_abilSlot = os.path.join(lib_root_path, "abil_slot.txt")
    str_Temp = load_raw_cfg(filePath_abilSlot)
    str_abil_slot = str_Temp if str_Temp is not None and int(str_Temp) < 9 and int(str_Temp) > 0 else str_abil_slot
    return "3" if str_abil_slot is None else str_abil_slot

if __name__ == "__main__":
    # file = path_join('..', '..', 'Input', 'tddtiming_mapping.json')
    # pattern_cfg = load_cfg(file)
    # pattern_mapping = pattern_cfg.get("1116_0ms", None)
    # if pattern_mapping is not None:
    #     convert_value_type_to_list(pattern_mapping)
    #
    # print(str(pattern_mapping))

    # mac_re_str = "<re.Match object; span=(98559, 98586), match=', dst mac 02:40:43:80:12:31'>"
    # data = {"mac_re_str": str(mac_re_str)}
    # store_cfg(data)

    # from nokia_5G_hwiv_configuration.utils.config_util import load_cfg
    # import re
    #
    # cfg = load_cfg()
    # fsp_mac_re_str = cfg.get("fsp_mac_re_str", None)
    # fsp_mac_re_str = re.search("MAC address to ([0-9a-fA-F-:]+)", fsp_mac_re_str)
    print(f"fsp_mac_re_str: <{get_abil_slot()}>")



