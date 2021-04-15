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
from auto_test.start_l1.testings.JESDVerify_AEQZ_multithread import JesdVerify
from auto_test.start_l1.connections.Instrument import visaInstrument
from auto_test.start_l1.testings.CheckDutStatus import DUT_Status
from auto_test.start_l1.testings.CPRISyncCheck import CpriSync
from auto_test.start_l1.testings.DpdinCheck import DpdinStatus
from auto_test.start_l1.testings.settings import download_runtime_log
from auto_test.start_l1.testings.Exceptions import *
from auto_test.start_l1.testings.activate_carriers import Web_handler, verify_L1_results
from lib_service.log_handler.socketio_handler import SocketIOHandler

# if __name__ == "__main__":

logging.StreamHandler()
logger = logging.getLogger('main')
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file_handler = logging.FileHandler(
    filename=os.path.join(root_path, f'start_l1/testings/MainTestResults/main_result.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


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

        DutStatusHandler = DUT_Status(made_ips, beamer_ip, product_type=activate_carriers_setting.get_rru())
        if not DutStatusHandler.check_dut_status():
            raise DUTNotReadyException("DUT status not ready!")
        self.check_if_pause()

        if DpdinFlag or JesdFlag or CpriFlag:
            logger.info("initial with L1 Scripts...")
            web_handler = Web_handler()
            web_handler.activate_carriers(activate_carriers_setting)
            web_handler.verify_l1_finish()
            verify_L1_results()

            logger.info("L1 init successfully...")
        # time.sleep(40)
        # disable_auto_reboot(beamer_ip)

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
        time.sleep(10)
        if DpdinFlag:  # or UdpcpFlag or SoapFlag
            DpdinCheckHandler = DpdinStatus(made_ips)
            self.dpdin_test_pass = DpdinCheckHandler.DPDIN_test(repeat=DpdinRepeatTimes)
            if not self.dpdin_test_pass:
                self.set_pause_flag()
                self.check_if_pause()

    def start(self, activate_carriers_setting, test_options):
        root_path = os.path.dirname(os.path.realpath(__file__))
        PSU = visaInstrument()
        PSU_Controller = PSU.PowerSuppy_Init("TCPIP_VISA_RAWSOCKET", "192.168.254.11")
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
            serialLog = SerialLog(port="COM8")
            t_serial = Thread(target=serialLog.run)
            t_serial.start()
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
                PSU.PowerSuppy_OFF_DELTA(PSU_Controller)
                time.sleep(5)
                main_result['total test'] += 1
            root_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(root_path, 'testings/MainTestResults/main_result.json'), 'w') as f:
                json.dump(main_result, f)


def start_stability_test(activate_carriers_setting, test_options):
    cv = threading.Condition()
    preVerification = PreVerification(cv)
    preVerification.start(activate_carriers_setting, test_options)


if __name__ == '__main__':
    activate_carriers_setting = ActivateCarriersSetting(ABIL_SLOT_NUMBER="3",
                                                        RRU="AEQC",
                                                        TDD_SWITCH="1116_3ms_a5",
                                                        CASE_TYPE="1CC",
                                                        DL_TM="TM1_1",
                                                        UL_TM="A1-5",
                                                        BANDWIDTH=["40", "40"],
                                                        FREQUENCY=["3450", "3450"],
                                                        POWER=["37.95", "37.95"])
    test_options = {
        'CycleTimes': 500,
        'CpriFlag': True,
        'CpriRepeatTimes': 100,
        'JesdFlag': True,
        'JesdRepeatTimes': 3,
        'UdpcpFlag': False,
        'SoapFlag': False,
        'DpdinFlag': True,
        'DpdinRepeatTimes': 1}
    cv = threading.Condition()
    preVerification = PreVerification(cv)
    preVerification.start(activate_carriers_setting, test_options)
