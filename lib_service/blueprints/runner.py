from flask import render_template, Blueprint, current_app, request, send_from_directory, jsonify
from lib_service.utils.command_executer import AsynCommandExecuter
from lib_service.utils.common import get_specific_config_data, get_default_config
from lib_service.forms import ExecutingForm
from lib_service.utils.config_util import store_web_params
from start_l1.utils.activate_carriers_setting import ActivateCarriersSetting
from lib_service.log_handler.socketio_client import SyncSocketIOClient
from lib_service.config import root_path, PORT
import logging, time
import threading
import os
import json

runner_bp = Blueprint('runner', __name__)

@runner_bp.route('/', methods=('GET', 'POST'))
def index():
    form = get_default_config()
    rru_list = get_specific_config_data('rru_list')
    bandwidth_list = get_specific_config_data('bandwidth_list')
    return render_template('index.html', form=form, rru_list=rru_list, bandwidth_list=bandwidth_list, tm_list=[])

socketio_server_base_url = "http://localhost:{}".format(PORT)
runner_sio_client = SyncSocketIOClient(socketio_server_base_url, "runner_message_event")
cmd_runner = "C:\RF_L1_Launcher_20B-21.01.R01-windows\env\python.exe {}{}start_l1{}start_with_20b_rewrite_web_runner.py".format(root_path, os.sep, os.sep)
as_cmd_executer = AsynCommandExecuter(cmd_runner)

def parse_raw_request(form:dict) -> dict:
    _setting = dict()
    pay_load = dict()
    # runner_type = form['runner_type']
    # _setting.update({"runner_type": runner_type})
    # pay_load.update({"runner_type": runner_type})
    power_supply_model = form['power_supply_model']
    power_supply_address = form['power_supply_address']
    serial_port = form['serial_port']
    l1_version = form['l1_version']
    pay_load.update({'power_supply_model': power_supply_model})
    pay_load.update({'power_supply_address': power_supply_address})
    pay_load.update({'serial_port': serial_port})
    pay_load.update({'l1_version': l1_version})

    abil_slot = form['abil_slot']
    _setting.update({"abil_slot": abil_slot})
    pay_load.update({"abil_slot": abil_slot})
    # auto_generate = form['auto_generate']
    # _setting.update({"auto_generate": auto_generate})
    # pay_load.update({"auto_generate": auto_generate})
    # l1_call_list = form['l1_call_list']
    # _setting.update({"l1_call_list": l1_call_list})
    # pay_load.update({"l1_call_list": l1_call_list})
    # bf_cal_list = form['bf_cal_list']
    # _setting.update({"bf_cal_list": bf_cal_list})
    # pay_load.update({"bf_cal_list": bf_cal_list})
    # if "prach_list" in form:
    #     prach_list = form['prach_list']
    #     _setting.update({"prach_list": prach_list})
    #     pay_load.update({"prach_list": prach_list})
    # setup_type = form['setup_type']
    # _setting.update({"setup_type": setup_type})
    # pay_load.update({"setup_type": setup_type})
    # beamer_log_capture = form.get('beamer_log_capture', None)
    # if beamer_log_capture is not None and beamer_log_capture == "on":
    #     _setting.update({"beamer_log_capture": beamer_log_capture})
    #     pay_load.update({"beamer_log_capture": "True"})
    #     pay_load.update({"log_dir": log_dir})
    # else:
    #     _setting.update({"beamer_log_capture": ""})
    #     pay_load.update({"beamer_log_capture": "False"})
    # l1sw_manual_conf = form.get('l1sw_manual_conf', None)
    # if l1sw_manual_conf is not None and l1sw_manual_conf == "on":
    #     _setting.update({"l1sw_manual_conf": l1sw_manual_conf})
    #     pay_load.update({"l1sw_manual_conf": "True"})
    # else:
    #     _setting.update({"l1sw_manual_conf": ""})
    #     pay_load.update({"l1sw_manual_conf": "False"})
    # loner_log_capture = form.get('loner_log_capture', None)
    # if loner_log_capture is not None and loner_log_capture == "on":
    #     _setting.update({"loner_log_capture": loner_log_capture})
    #     pay_load.update({"loner_log_capture": "True"})
    #     pay_load.update({"log_dir": log_dir})
    # else:
    #     _setting.update({"loner_log_capture": ""})
    #     pay_load.update({"loner_log_capture": "False"})
    # l1_lib_log_capture = form.get('l1_lib_log_capture', None)
    # if l1_lib_log_capture is not None and l1_lib_log_capture == "on":
    #     _setting.update({"l1_lib_log_capture": l1_lib_log_capture})
    #     pay_load.update({"l1_lib_log_capture": "True"})
    #     pay_load.update({"log_dir": log_dir})
    # else:
    #     _setting.update({"l1_lib_log_capture": ""})
    #     pay_load.update({"l1_lib_log_capture": "False"})
    # loner_dl_data_capture = form.get('loner_dl_data_capture', None)
    # if loner_dl_data_capture is not None and loner_dl_data_capture == "on":
    #     _setting.update({"loner_dl_data_capture": loner_dl_data_capture})
    #     pay_load.update({"loner_dl_data_capture": "True"})
    # else:
    #     _setting.update({"loner_dl_data_capture": ""})
    #     pay_load.update({"loner_dl_data_capture": "False"})
    # loner_ul_data_capture = form.get('loner_ul_data_capture', None)
    # if loner_ul_data_capture is not None and loner_ul_data_capture == "on":
    #     _setting.update({"loner_ul_data_capture": loner_ul_data_capture})
    #     pay_load.update({"loner_ul_data_capture": "True"})
    # else:
    #     _setting.update({"loner_ul_data_capture": ""})
    #     pay_load.update({"loner_ul_data_capture": "False"})

    dl_tm = form['dl_tm']
    ul_tm = form['ul_tm']
    tdd_switch = form['tdd_switch']
    rru = form['rru']
    case_type = form['case_type']
    c1_bw = form['c1_bw']
    c1_freq = form['c1_freq']
    c1_power = form['c1_power']
    c1_cell_id = form['c1_cell_id']
    c1_rnti = form['c1_rnti']
    c1_rboffset = form['c1_rboffset']
    c1_power_backoff = form['c1_power_backoff']

    _setting.update({
        "dl_tm": dl_tm,
        "ul_tm": ul_tm,
        "tdd_switch": tdd_switch,
        "rru": rru,
        "case_type": case_type,
        "c1_bw": c1_bw,
        "c1_freq": c1_freq,
        "c1_power": c1_power,
        "c1_cell_id": c1_cell_id,
        "c1_rnti": c1_rnti,
        "c1_rboffset": c1_rboffset,
        "c1_power_backoff": c1_power_backoff
    })

    bw_list = list()
    if len(c1_bw) > 0:
        bw_list.append(c1_bw)
    freq_list = list()
    if len(c1_freq) > 0:
        freq_list.append(c1_freq)
    power_list = list()
    if len(c1_power) > 0:
        power_list.append(c1_power)
    cell_id_list = list()
    if len(c1_cell_id) > 0:
        cell_id_list.append(c1_cell_id)
    rnti_list = list()
    if len(c1_rnti) > 0:
        rnti_list.append(c1_rnti)
    rboffset_list = list()
    if len(c1_rboffset) > 0:
        rboffset_list.append(c1_rboffset)
    power_backoff_list = list()
    if len(c1_power_backoff) > 0:
        power_backoff_list.append(c1_power_backoff)

    if case_type != "1CC":
        c2_bw = form['c2_bw']
        if len(c2_bw) > 0:
            bw_list.append(c2_bw)
        c2_freq = form['c2_freq']
        if len(c2_freq) > 0:
            freq_list.append(c2_freq)
        c2_power = form['c2_power']
        if len(c2_power) > 0:
            power_list.append(c2_power)
        c2_cell_id = form['c2_cell_id']
        if len(c2_cell_id) > 0:
            cell_id_list.append(c2_cell_id)
        c2_rnti = form['c2_rnti']
        if len(c2_rnti) > 0:
            rnti_list.append(c2_rnti)
        c2_rboffset = form['c2_rboffset']
        if len(c2_rboffset) > 0:
            rboffset_list.append(c2_rboffset)
        c2_power_backoff = form['c2_power_backoff']
        if len(c2_power_backoff) > 0:
            power_backoff_list.append(c2_power_backoff)

        _setting.update({
            "c2_bw": c2_bw,
            "c2_freq": c2_freq,
            "c2_power": c2_power,
            "c2_cell_id": c2_cell_id,
            "c2_rnti": c2_rnti,
            "c2_rboffset": c2_rboffset,
            "c2_power_backoff": c2_power_backoff
        })

    pay_load.update({
        "bw": bw_list,
        "dl_tm": dl_tm,
        "ul_tm": ul_tm,
        "tdd_switch": tdd_switch,
        "rru": rru,
        "case_type": case_type,
        "freq_list": freq_list,
        "power_list": power_list,
        "cell_id_list": cell_id_list,
        "rnti_list": rnti_list,
        "rboffset_list": rboffset_list,
        "power_backoff_list": power_backoff_list
    })
    cycle_times = form['cycle_times']

    jesd_flag = form.get('jesd_flag', None)
    if jesd_flag is not None and jesd_flag == "on":
        pay_load.update({"jesd_flag": "True"})
    else:
        pay_load.update({"jesd_flag": "False"})

    pause_on_jesd_fail = form.get('pause_on_jesd_fail', None)
    if pause_on_jesd_fail is not None and pause_on_jesd_fail == 'on':
        pay_load.update({'pause_on_jesd_fail': "True"})
    else:
        pay_load.update({'pause_on_jesd_fail': "False"})

    cpri_flag = form.get('cpri_flag', None)
    if cpri_flag is not None and cpri_flag == "on":
        pay_load.update({"cpri_flag": "True"})
    else:
        pay_load.update({"cpri_flag": "False"})

    pause_on_cpri_fail = form.get('pause_on_cpri_fail', None)
    if pause_on_cpri_fail is not None and pause_on_cpri_fail == 'on':
        pay_load.update({'pause_on_cpri_fail': "True"})
    else:
        pay_load.update({'pause_on_cpri_fail': "False"})

    dpdin_flag = form.get('dpdin_flag', None)
    if dpdin_flag is not None and dpdin_flag == "on":
        pay_load.update({"dpdin_flag": "True"})
    else:
        pay_load.update({"dpdin_flag": "False"})

    pause_on_power_fail = form.get('pause_on_power_fail', None)
    if pause_on_power_fail is not None and pause_on_power_fail == 'on':
        pay_load.update({'pause_on_power_fail': "True"})
    else:
        pay_load.update({'pause_on_power_fail': "False"})

    cpri_repeat_times = form['cpri_repeat_times']
    jesd_repeat_times = form['jesd_repeat_times']
    dpdin_repeat_times = form['dpdin_repeat_times']

    pay_load.update({
        'cycle_times':cycle_times,
        'cpri_repeat_times': cpri_repeat_times,
        'jesd_repeat_times': jesd_repeat_times,
        'dpdin_repeat_times': dpdin_repeat_times
    })

    return _setting, pay_load




def send_message(socketio_client: SyncSocketIOClient, message: str):
    socketio_client.send(message)

def runner_callback(message: str):
    send_message(runner_sio_client, message)

@runner_bp.route('/executing', methods=['POST'])
def execute():
    form = ExecutingForm(request.form)
    # activate_carriers_setting = ActivateCarriersSetting(ABIL_SLOT_NUMBER=form.abil_slot,
    #                                                     RRU=form.rru,
    #                                                     TDD_SWITCH=form.tdd_switch,
    #                                                     CASE_TYPE=form.case_type,
    #                                                     DL_TM=form.dl_tm,
    #                                                     BANDWIDTH=form.c1_bw,
    #                                                     FREQUENCY=form.c1_freq,
    #                                                     POWER=form.c1_power)
    # test_options = {
    #     'CycleTimes': form.cycle_times,
    #     'CpriFlag': form.cpri_flag,
    #     'CpriRepeatTimes': form.cpri_repeat_times,
    #     'JesdFlag': form.jesd_flag,
    #     'JesdRepeatTimes': form.jesd_repeat_times,
    #     'UdpcpFlag': False,
    #     'SoapFlag': False,
    #     'DpdinFlag': form.dpdin_flag,
    #     'DpdinRepeatTimes': form.dpdin_repeat_times}
    try:
        _setting, payload = parse_raw_request(request.form)

        payload.update({"socket_io_server_url": current_app.config.get("socket_io_server_url", None)})

        global current_executing
        current_executing = _setting
        runner = {
            "runner": payload
        }

        store_web_params(runner)
        as_cmd_executer.setCallback(runner_callback)
        as_cmd_executer.start()
        return {'type': 'success', 'message': 'Started successfully.'}
    except RuntimeError as exp:
        current_app.logger.error(exp)
        return {'type': 'error', 'message': str(exp)}

@runner_bp.route('/stop', methods=['POST', 'GET'])
def stop():
    as_cmd_executer.stop()
    return {'type': 'success', 'message': "Stopped successfully."}