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
from auto_test.start_l1.testings.activate_carriers_setting import ActivateCarriersSetting
# from nokia_5G_hwiv_configuration.run_python import main

# print('sys_path: ', sys.path) # add dut_control to system path
from nokia_5G_hwiv_configuration.dev_debug import change_testmode
from nokia_5G_hwiv_configuration.libraries.common_lib.PathLib import PathLib
import nokia_5G_hwiv_configuration.libraries.testmode_gen.TestModeGen as TM_XML_Gen
from nokia_5G_hwiv_configuration.libraries.testmode_gen.TestModeGen import path_join
# from nokia_5G_hwiv_configuration.run_python import main
from auto_test.start_l1.testings.JESDVerify_AEQZ_multithread import JesdVerify
from auto_test.start_l1.L1Connections.run_python import main
from auto_test.start_l1.connections.Instrument import visaInstrument
from auto_test.start_l1.testings.CheckDutStatus import DUT_Status
from auto_test.start_l1.testings.CPRISyncCheck import CpriSync
from auto_test.start_l1.testings.DpdinCheck import DpdinStatus
from auto_test.start_l1.testings.settings import download_runtime_log
from auto_test.start_l1.testings.Exceptions import *
from lib_service.log_handler.socketio_handler import SocketIOHandler
# if __name__ == "__main__":

logging.StreamHandler()
logger = logging.getLogger('main')
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file_handler = logging.FileHandler(
    filename=os.path.join(root_path, f'start_l1/testings/MainTestResults/main_result.log'))
file_handler.setFormatter(formatter)
# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# logger_main.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)
# server_url = "http://localhost:8032"
# event = "runner_message_event"
# socket_io_handler = SocketIOHandler(server_url, event)
# socket_io_handler.setLevel(logging.DEBUG)
# logger.addHandler(socket_io_handler)

# print("root_path again: ", root_path)
# sys.path.insert(0, root_path + os.sep + 'L1Connections' + os.sep + 'JESD')
# sys.path.insert(0, root_path + os.sep + 'L1Connections' + os.sep + 'Dpdin')
# print(sys.path)

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
                    'CycleTimes': int(runner_params['cycle_times']),
                    'CpriFlag': runner_params['cpri_flag'] == "True",
                    'CpriRepeatTimes': int(runner_params['cpri_repeat_times']) if runner_params['cpri_repeat_times'].strip() else 0,
                    'JesdFlag': runner_params['jesd_flag'] == "True",
                    'JesdRepeatTimes': int(runner_params['jesd_repeat_times']) if runner_params['jesd_repeat_times'].strip() else 0,
                    'UdpcpFlag': False,
                    'SoapFlag': False,
                    'DpdinFlag': runner_params['dpdin_flag'] == "True",
                    'DpdinRepeatTimes': int(runner_params['dpdin_repeat_times']) if runner_params['dpdin_repeat_times'].strip() else 0}

    return activate_carriers_setting, test_options


class PreVerification(object):

    def __init__(self, cv):
        self.jesd_test_pass = False
        self.dpdin_test_pass = False
        self._pause_flag = False
        self.cv = cv

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

    def pre_test(self, activate_carriers_setting, test_options):
        DpdinFlag = test_options['DpdinFlag']
        JesdFlag = test_options['JesdFlag']
        CpriFlag = test_options['CpriFlag']
        CpriRepeatTimes = test_options['CpriRepeatTimes']
        JesdRepeatTimes = test_options['JesdRepeatTimes']
        DpdinRepeatTimes = test_options['DpdinRepeatTimes']

        made_ips = activate_carriers_setting.get_mades()
        beamer_ip = '192.168.101.1'

        # DutStatusHandler = DUT_Status(made_ips, beamer_ip, product_type=activate_carriers_setting.get_rru())
        # if not DutStatusHandler.check_dut_status():
        #     raise DUTNotReadyException("DUT status not ready!")
        self.check_if_pause()
        """
        activate_carriers_setting = ActivateCarriersSetting(ABIL_SLOT_NUMBER=runner_params['abil_slot'],
                                                        RRU=runner_params['rru'],
                                                        TDD_SWITCH=runner_params['tdd_switch'],
                                                        CASE_TYPE=runner_params['case_type'],
                                                        DL_TM=runner_params['dl_tm'],
                                                        BANDWIDTH=['bw'],
                                                        FREQUENCY=runner_params['freq_list'],
                                                        POWER=runner_params['power_list'])"""
        l1_xml = change_testmode(dl_mode=activate_carriers_setting.get_dl_tm(),  # TM1_1, TM1_2, TM2, TM2A, TM3_1, TM3_1A, TM3_2, TM3_3
                                 ul_mode=activate_carriers_setting.get_ul_tm(),  # A1-2, A1-5, A2-5
                                 bandwidth=activate_carriers_setting.get_bandwidth(),  # MHz, 100, 80, 60, 40, 20
                                 rru_mode=activate_carriers_setting.get_rru(),  #
                                 frequency_list=activate_carriers_setting.get_frequency(),  # MHz
                                 power_list=activate_carriers_setting.get_power(),  # dBm
                                 # cell_id_list=["1", "1"],
                                 # pusch_rb_offset_list=[85, 122],      # RB offset for PUSCH
                                 # pdsch_power_backoff_list=[20, 30],   # dB
                                 case_type=activate_carriers_setting.get_case_type(),  # "1CC", "2CC", "Split", set it if auto_gen=True
                                 auto_gen=True,  # xml generation switch, True or False
                                 feature_id="2402",  # "1037" for 3GPP 15-1, "2402" for 3GPP 15-2
                                 )
        if DpdinFlag:
            logger.info("initial with L1 Scripts...")
            L1_STATUS = main(l1_xml, L1Connection_file='L1Connection', timeout=1200)
        elif JesdFlag or CpriFlag:
            logger.info("initial with L1 Scripts...")
            L1_STATUS = main(l1_xml, L1Connection_file='L1Connection_Jesd', timeout=1200)
        else:
            L1_STATUS = "NO INIT"


        if L1_STATUS == 'TIME OUT':
            raise L1TimeOutException("L1 init didn't finish in 1200 seconds.. unit will reboot")
        elif L1_STATUS == 'FAIL':
            raise L1InitFailException("L1 init failed.. unit will reboot")
        logger.info("initial finished...")
        time.sleep(40)



        if CpriFlag:
            CpriSyncHandler = CpriSync()
            if not CpriSyncHandler.Cpri_test(REPEAT=CpriRepeatTimes):
                raise CpriSyncFailException("Cpri link sync failed..unit will reboot")
            self.check_if_pause()

        if JesdFlag:
            JesdVerifyHandler = JesdVerify(made_ips=made_ips, product_type=activate_carriers_setting.get_rru())
            self.jesd_test_pass = JesdVerifyHandler.JesdTest(JesdRepeatTimes)
                # self.set_pause_flag()
            self.check_if_pause()
        time.sleep(300)
        if DpdinFlag:  # or UdpcpFlag or SoapFlag
            DpdinCheckHandler = DpdinStatus(made_ips)
            self.dpdin_test_pass = DpdinCheckHandler.DPDIN_test(repeat=DpdinRepeatTimes)
            self.check_if_pause()

    def start(self, activate_carriers_setting, test_options):
        root_path = os.path.dirname(os.path.realpath(__file__))
        PSU = visaInstrument()
        PSU_Controller = PSU.PowerSuppy_Init("GPIB", "11")
        CycleTimes = test_options['CycleTimes']
        JesdFlag = test_options['JesdFlag']
        DpdinFlag = test_options['DpdinFlag']
        for i in range(CycleTimes):
            try:
                with open(os.path.join(root_path, f'testings/MainTestResults/main_result.json'), 'r') as f:
                    main_result = json.load(f)
            except FileNotFoundError:
                main_result = {'total test': 0, 'pass': 0, 'fail on DUT not ready': 0, 'fail on L1 TIME OUT': 0,
                               'fail on L1 failure': 0, 'CPRI sync fail': 0, 'JESD reg fail': 0, 'DPD power fail': 0,
                               'fail both on JESD reg and DPD power': 0}

            logger.info(f"Cycle time {i + 1}")
            PSU.PowerSuppy_ON_DELTA(PSU_Controller)
            SerialLog = getattr(__import__("serial_log"), 'SerialLog')
            serialLog = SerialLog(port="COM7")
            t_serial = Thread(target=serialLog.run)
            t_serial.start()
            # start reading temperature thread
            # from tools_dev.connections.RecordTemperature import RecordTemperature
            # record_temp = RecordTemperature()
            # t_record_temp = Thread(target=record_temp.run, args=(setting_data['made_num']*8, 18, "AENB"))
            # t_record_temp.start()
            try:
                self.pre_test(activate_carriers_setting, test_options)
                if JesdFlag and DpdinFlag and not self.jesd_test_pass and not self.dpdin_test_pass:
                    main_result['fail both on JESD reg and DPD power'] += 1
                elif JesdFlag and not self.jesd_test_pass:
                    main_result['JESD reg fail'] += 1
                elif DpdinFlag and not self.dpdin_test_pass:
                    main_result['DPD power fail'] += 1
                else:
                    main_result['pass'] += 1
                print("still running..")
            except DUTNotReadyException:
                print("DUT status not ready..")
                logger.error("DUT status not ready")
                main_result['fail on DUT not ready'] += 1
                # serialLog.catch_log()
                self.check_if_pause()
            except L1InitFailException:
                print("L1 didn't init successfully!")
                logger.error("L1 didn't init successfully!")
                main_result['fail on L1 failure'] += 1
                root_path = os.path.dirname(os.path.realpath(__file__))
                download_runtime_log(path=os.path.join(root_path, 'testings/MainTestResults/runtimeLog/'),
                                     log_name='L1_Fail')
                self.check_if_pause()
            except L1TimeOutException:
                print("L1 didn't init within 1200s!")
                logger.error("L1 didn't init within 1200s!")
                main_result['fail on L1 TIME OUT'] += 1
                root_path = os.path.dirname(os.path.realpath(__file__))
                download_runtime_log(path=os.path.join(root_path, 'testings/MainTestResults/runtimeLog/'),
                                     log_name='L1_Timeout')
                self.check_if_pause()
            except CpriSyncFailException:
                print("Cpri link failed!")
                logger.error("Cpri link failed!")
                main_result['CPRI sync fail'] += 1
                root_path = os.path.dirname(os.path.realpath(__file__))
                download_runtime_log(path=os.path.join(root_path, 'testings/MainTestResults/runtimeLog/'),
                                     log_name='Cpri_sync_fail')
                self.check_if_pause()
            # except:
            #     e = sys.exc_info()[0]
            #     logger.error(f"unexpected error during test: {e}")
            #     self.check_if_pause()
            finally:
                serialLog.catch_log()
                print("wait for thread finish..")
                serialLog.terminate()
                t_serial.join()
                # record_temp.terminate()
                # t_record_temp.join()

                PSU.PowerSuppy_OFF_DELTA(PSU_Controller)
                time.sleep(5)
                main_result['total test'] += 1
            root_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(root_path, 'testings/MainTestResults/main_result.json'), 'w') as f:
                json.dump(main_result, f)

if __name__ == '__main__':
    runner_params = {'abil_slot': '3', 'bw': ['40'], 'dl_tm': 'TM1_1', 'ul_tm': 'A1-5', 'tdd_switch': '1116_3ms_a5',
                     'rru': 'AENB',
                     'case_type': '1CC', 'freq_list': ['2320'], 'power_list': ['38.75'], 'cell_id_list': [],
                     'rnti_list': [], 'rboffset_list': [],
                     'power_backoff_list': [], 'jesd_flag': 'True', 'cpri_flag': 'True', 'dpdin_flag': 'True',
                     'cycle_times': '100', 'cpri_repeat_times': '3',
                     'jesd_repeat_times': '3', 'dpdin_repeat_times': '1',
                     'socket_io_server_url': {'url': 'http://localhost:8032', 'event': 'runner_message_event'}}
    activate_carriers_setting, test_options = parse_parameters(runner_params)
    cv = threading.Condition()
    preVerification = PreVerification(cv)
    preVerification.start(activate_carriers_setting, test_options)

