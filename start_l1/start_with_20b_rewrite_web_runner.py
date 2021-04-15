import os
import sys
import time
import logging
import json
import threading
from threading import Thread

root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print('root_path: ' + root_path)  # root_path = auto_test
sys.path.insert(0, os.path.join(root_path, ".."))
from auto_test.start_l1.utils.activate_carriers_setting import ActivateCarriersSetting
from auto_test.start_l1.utils.activate_carriers import verify_L1_results
# print('sys_path: ', sys.path) # add dut_control to system path
from auto_test.start_l1.utils.cpriSyncCheck import cpri_check
from auto_test.start_l1.utils.jesdReader import JesdReader
from auto_test.start_l1.utils.DpdinCheck import DpdinStatus
from auto_test.start_l1.utils.settings import download_runtime_log
from auto_test.start_l1.utils.Exceptions import *
from auto_test.lib_service.log_handler.socketio_handler import SocketIOHandler
from auto_test.start_l1.connections.PowerControl import PowerControl, TCPIPVisaRawSocketControlMode, TCPIPVisaControlMode, GPIBControlMode
from auto_test.start_l1.utils.checkDut import check_dut_status
from auto_test.start_l1.utils.L1Init import select_L1_init_mode, L1Init
from auto_test.lib_service.utils.config_util import load_web_params

logging.StreamHandler()
logger = logging.getLogger('main')
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file_handler = logging.FileHandler(
    filename=os.path.join(root_path, f'start_l1/testings/MainTestResults/main_result.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
server_url = "http://localhost:5000"
event = "runner_message_event"
socket_io_handler = SocketIOHandler(server_url, event)
socket_io_handler.setLevel(logging.DEBUG)
logger.addHandler(socket_io_handler)

def parse_parameters(runner_params: dict):
    # runner_params = {'abil_slot': '3', 'bw': ['40'], 'dl_tm': 'TM1_1', 'ul_tm': 'A1-5', 'tdd_switch': '1116_3ms_a5',
    #                  'rru': 'AEQB',
    #                  'case_type': '1CC', 'freq_list': ['2320'], 'power_list': ['38.75'], 'cell_id_list': [],
    #                  'rnti_list': [], 'rboffset_list': [],
    #                  'power_backoff_list': [], 'jesd_flag': 'True', 'cpri_flag': 'True', 'dpdin_flag': 'True',
    #                  'cycle_times': '100', 'cpri_repeat_times': '3',
    #                  'jesd_repeat_times': '3', 'dpdin_repeat_times': '1',
    #                  'socket_io_server_url': {'url': 'http://localhost:8032', 'event': 'runner_message_event'}}
    activate_carriers_setting = ActivateCarriersSetting(ABIL_SLOT_NUMBER=runner_params['abil_slot'],
                                                        RRU=runner_params['rru'],
                                                        TDD_SWITCH=runner_params['tdd_switch'],
                                                        CASE_TYPE=runner_params['case_type'],
                                                        DL_TM=runner_params['dl_tm'],
                                                        BANDWIDTH=runner_params['bw'],
                                                        FREQUENCY=runner_params['freq_list'],
                                                        POWER=runner_params['power_list'],
                                                        UL_TM=runner_params['ul_tm'])
    test_options = {
                    'cycle_times': int(runner_params['cycle_times']),
                    'cpri_flag': runner_params['cpri_flag'] == "True",
                    'cpri_repeat_times': int(runner_params['cpri_repeat_times']) if runner_params['cpri_repeat_times'].strip() else 0,
                    'jesd_flag': runner_params['jesd_flag'] == "True",
                    'jesd_repeat_times': int(runner_params['jesd_repeat_times']) if runner_params['jesd_repeat_times'].strip() else 0,
                    'udhcp_flag': False,
                    'soap_flag': False,
                    'dpdin_flag': runner_params['dpdin_flag'] == "True",
                    'dpdin_repeat_times': int(runner_params['dpdin_repeat_times']) if runner_params['dpdin_repeat_times'].strip() else 0,
                    'pause_on_cpri_fail': runner_params['pause_on_cpri_fail'] == "True",
                    'pause_on_jesd_fail': runner_params['pause_on_jesd_fail'] == "True",
                    'pause_on_power_fail': runner_params['pause_on_power_fail'] == "True",
                    'power_supply_model': runner_params['power_supply_model'], 'power_supply_address': runner_params['power_supply_address'],
                    'serial_port': runner_params['serial_port'], 'l1_version': runner_params['l1_version']}

    return activate_carriers_setting, test_options

class StabilityTest(object):

    def __init__(self, activate_carriers_setting, test_options):
        self.activate_carriers_setting = activate_carriers_setting
        self.test_options = test_options
        self.jesd_test_pass = False
        self.dpdin_test_pass = False
        self._pause_flag = False
        self.cv = threading.Condition()

    def set_pause_flag(self):
        self._pause_flag = True
        print("set pause flag to True")

    def set_resume_flag(self):
        self._pause_flag = False
        print("set pause flag to False")

    def check_if_pause(self):
        while self._pause_flag:
            with self.cv:
                print("put thread to sleep...")
                self.cv.wait()

    def check_dut(self):
        check_dut_status(self.activate_carriers_setting)

    def init_l1(self):
        l1_init_mode = select_L1_init_mode(test_options=self.test_options)
        l1_init_handler = L1Init(l1_init_mode)
        l1_init_handler.run(activate_carriers_setting=self.activate_carriers_setting)
        verify_L1_results()

    def check_cpri(self):
        if self.test_options["cpri_flag"]:
            cpri_check(time_out=30)
        else:
            pass

    def read_jesd(self):
        if self.test_options['jesd_flag']:
            jesdReader = JesdReader(product_type=self.activate_carriers_setting.get_rru(),
                                    made_ips=self.activate_carriers_setting.get_mades())
            self.jesd_test_pass = jesdReader.read_jesd(repeat=self.test_options["jesd_repeat_times"])
            if not self.jesd_test_pass and self.test_options['pause_on_jesd_fail']:
                self.set_pause_flag()
            self.check_if_pause()
        else:
            pass

    def one_cycle(self):
        self.power_on()
        self.check_dut()
        self.init_l1()
        self.check_cpri()
        self.read_jesd()
        self.power_read()

    def power_read(self):
        if test_options["dpdin_flag"]:
            DpdinCheckHandler = DpdinStatus(self.activate_carriers_setting.get_mades())
            self.dpdin_test_pass = DpdinCheckHandler.DPDIN_test(repeat=self.test_options["dpdin_repeat_times"])
            if not self.dpdin_test_pass and self.test_options["pause_on_power_fail"]:
                self.set_pause_flag()
                self.check_if_pause()
        else:
            pass

    def init_result_file(self):
        try:
            with open(os.path.join(root_path, f'testings/MainTestResults/main_result.json'), 'r') as f:
                main_result = json.load(f)
        except FileNotFoundError:
            main_result = {'total test': 0, 'pass': 0, 'fail on DUT not ready': 0, 'fail on L1 TIME OUT': 0,
                           'fail on L1 failure': 0, 'CPRI sync fail': 0, 'JESD reg fail': 0, 'DPD power fail': 0,
                           'fail both on JESD reg and DPD power': 0}
        self.result = main_result

    def set_power_control(self):
        if self.test_options["power_supply_model"] == "TOE":
            power_control = PowerControl(GPIBControlMode())
        elif self.test_options["power_supply_model"] == "Delta":
            power_control = PowerControl(TCPIPVisaRawSocketControlMode())
        else:
            power_control = None
            logger.error("No supported power supply model!")
        self.power_control = power_control

    def power_init(self):
        self.set_power_control()
        self.power_control.power_init(address=self.test_options["power_supply_address"])

    def power_on(self):
        self.power_control.power_on()

    def power_off(self):
        self.power_control.power_off()

    def start_serial_log(self):
        SerialLog = getattr(__import__("serial_log"), 'SerialLog')
        serialLog = SerialLog(port=self.test_options["serial_port"])
        t_serial = Thread(target=serialLog.run)
        t_serial.start()
        self.serialLog = serialLog
        self.t_serial = t_serial

    def catch_serial_log(self):
        self.serialLog.catch_log()
        self.t_serial.join()

    def terminate_serial_log(self):
        self.serialLog.terminate()
        self.t_serial.join()

    def parse_result(self):
        if self.test_options["jesd_flag"] and self.test_options["dpdin_flag"] and not self.jesd_test_pass and not self.dpdin_test_pass:
            self.result['fail both on JESD reg and DPD power'] += 1
        elif self.test_options["jesd_flag"] and not self.jesd_test_pass:
            self.result['JESD reg fail'] += 1
        elif self.test_options["dpdin_flag"] and not self.dpdin_test_pass:
            self.result['DPD power fail'] += 1
        else:
            self.result['pass'] += 1

    def start(self):
        self.power_init()
        cycle_times = self.test_options['cycle_times']
        root_path = os.path.dirname(os.path.realpath(__file__))
        for i in range(cycle_times):
            logger.info(f"Cycle time {i + 1}")
            self.init_result_file()
            self.power_control.power_on()
            self.start_serial_log()
            try:
                self.one_cycle()
                self.parse_result()
                print("still running..")
            except DUTNotReadyException:
                print("DUT status not ready..")
                logger.error("DUT status not ready")
                self.result['fail on DUT not ready'] += 1
            except L1InitFailException:
                print("L1 didn't init successfully!")
                logger.error("L1 didn't init successfully!")
                self.result['fail on L1 failure'] += 1

                download_runtime_log(path=os.path.join(root_path, 'testings/MainTestResults/runtimeLog/'),
                                     log_name='L1_Fail')
            except L1TimeOutException:
                print("L1 didn't init within 1200s!")
                logger.error("L1 didn't init within 1200s!")
                self.result['fail on L1 TIME OUT'] += 1
                download_runtime_log(path=os.path.join(root_path, 'testings/MainTestResults/runtimeLog/'),
                                     log_name='L1_Timeout')
            except CpriSyncFailException:
                print("Cpri link failed!")
                logger.error("Cpri link failed!")
                self.result['CPRI sync fail'] += 1
                download_runtime_log(path=os.path.join(root_path, 'testings/MainTestResults/runtimeLog/'),
                                     log_name='Cpri_sync_fail')
                if self.test_options['pause_on_cpri_fail']:
                    self.set_pause_flag()
                self.check_if_pause()
            # except:
            #     e = sys.exc_info()[0]
            #     logger.error(f"unexpected error during test: {e}")
            #     self.check_if_pause()
            finally:
                self.catch_serial_log()
                self.power_off()
                time.sleep(5)
                self.result['total test'] += 1
            with open(os.path.join(root_path, 'testings/MainTestResults/main_result.json'), 'w') as f:
                json.dump(self.result, f)

if __name__ == '__main__':
    web_params = load_web_params()
    runner_params = web_params["runner"]
    print(runner_params)
    # runner_params = {'abil_slot': '3', 'bw': ['40'], 'dl_tm': 'TM1_1', 'ul_tm': 'A1-5', 'tdd_switch': '1116_3ms_a5',
    #                  'rru': 'AEQC',
    #                  'case_type': '1CC', 'freq_list': ['3450'], 'power_list': ['37.95'], 'cell_id_list': [],
    #                  'rnti_list': [], 'rboffset_list': [],
    #                  'power_backoff_list': [], 'jesd_flag': 'True', 'cpri_flag': 'True', 'dpdin_flag': 'True',
    #                  'cycle_times': '100', 'cpri_repeat_times': '3',
    #                  'jesd_repeat_times': '3', 'dpdin_repeat_times': '1',
    #                  'socket_io_server_url': {'url': 'http://localhost:8032', 'event': 'runner_message_event'},
    #                  'power_supply_model': 'Delta', 'power_supply_address': '192.168.254.11', 'serial_port': 'COM8',
    #                  'l1_version': '20B'}
    activate_carriers_setting, test_options = parse_parameters(runner_params)
    stability_test_handler = StabilityTest(activate_carriers_setting, test_options)
    stability_test_handler.start()
