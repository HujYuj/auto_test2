
import os, sys
import json

def get_root_folder():
    current_foler = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.dirname(os.path.dirname(current_foler))
    # return root_folder as auto_test_20b
    return root_folder

    # sys.path.insert(0, root_folder)
    # from tools_dev.start import start_stability_test
    # from nokia_5G_hwiv_configuration.libraries.common_lib.log_handler.socketio_client import SyncSocketIOClient
    # print(root_folder)

def get_config_data():
    root_file_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    config_file = os.path.join(root_file_path, "configuration", "config_data.json")
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    return config_data


def get_specific_config_data(key: str):
    config_data = get_config_data()
    try:
        info = config_data[key]
    except AttributeError:
        raise RuntimeError("No related config available, please run case firstly.")
    return info

def get_default_config():
    return {
        "abil_slot": "",
        "abil_opt_port": "",
        "tdd_switch": "",
        "scs": "",
        "rru": "",
        "rru_opt_port": "",
        "num_of_carrier": "",
        "c1_freq": "",
        "c1_rboffset": "",
        "c1_bw": "",
        "c1_power": "",
        "c1_dltm": "",
        "c1_ultm": "",
        "c2_freq": "",
        "c2_rboffset": "",
        "c2_bw": "",
        "c2_power": "",
        "c2_dltm": "",
        "c2_ultm": "",
        "file_name": ""
    }
if __name__ == "__main__":
    # rru_list = get_specific_config_data("rru_list")
    # print(rru_list)

    print(get_root_folder())