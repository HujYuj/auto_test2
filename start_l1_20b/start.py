import os
import sys
import time
import logging
import json
import threading
from threading import Thread

root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# print('root_path: ' + root_path) # root_path = tools_dev
sys.path.insert(0, os.path.join(root_path, ".."))
# print('sys_path: ', sys.path) # add dut_control to system path
from nokia_5G_hwiv_configuration.dev_debug import change_testmode
from nokia_5G_hwiv_configuration.libraries.common_lib.PathLib import PathLib
import nokia_5G_hwiv_configuration.libraries.testmode_gen.TestModeGen as TM_XML_Gen
from nokia_5G_hwiv_configuration.libraries.testmode_gen.TestModeGen import path_join
# from nokia_5G_hwiv_configuration.run_python import main
from auto_test_20b.tools_dev.testings.JESDVerify_AEQZ_multithread import JesdVerify
from auto_test_20b.tools_dev.L1Connections.run_python import main
from auto_test_20b.tools_dev.connections.Instrument import visaInstrument
from auto_test_20b.tools_dev.testings.CheckDutStatus import DUT_Status
from auto_test_20b.tools_dev.testings.CPRISyncCheck import CpriSync
from auto_test_20b.tools_dev.testings.DpdinCheck import DpdinStatus
from auto_test_20b.tools_dev.testings.settings import download_runtime_log
from auto_test_20b.tools_dev.testings.Exceptions import *

# if __name__ == "__main__":

logging.StreamHandler()
logger = logging.getLogger('main')
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file_handler = logging.FileHandler(
    filename=os.path.join(root_path, f'tools_dev/testings/MainTestResults/main_result.log'))
file_handler.setFormatter(formatter)
# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# logger_main.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


# print("root_path again: ", root_path)
# sys.path.insert(0, root_path + os.sep + 'L1Connections' + os.sep + 'JESD')
# sys.path.insert(0, root_path + os.sep + 'L1Connections' + os.sep + 'Dpdin')
# print(sys.path)
def get_rru_mode(mode):
    if mode in ["AEQB", "AEQE", "AEQP", "AEQI"]:
        return "AEQB"
    elif mode in ["AEQV", "AEQY", "AEQZ", "AEQQ", "AEQC", "AENB"]:
        return "AEQZ"
    else:
        return "AEQB"


def generate_xml_config(tm, ul_case, bw, rru='AEQB', abil_slot='3', force_rewrite=False, case_type="1CC", feature_id="2402"):
    """
    Generate test mode xml config based on excel template.
    :param tm: DL test mode name, such as: TM1.1, TM1.2, TM2, ...
    :param ul_case: UL test case: 'A1-5', 'A2-5'
    :param bw: bandwidth, no unit. such as: '100', '80', '60', ...
    :param rru: RRU name, such as: 'AEQB', 'AEQV', 'AEQZ'
    :param force_rewrite: if True, force generate xml and don't care if the xml has already existed.
    :return: None
    """
    bw_map = {
        '20': "20@30.72",
        '40': '40@61.44',
        '60': "60@122.88",
        '80': "80@122.88",
        '100': '100@122.88',
    }
    bandwidth = bw_map[bw]
    param_dict = {"test_mode": tm,
                  "ul_testcase": ul_case,
                  "tdd_switch": "[DL,DL,DL,DL,DL,DL,DL,SS,UL,UL]",
                  "bbu_cpri": "8",
                  "rru_cpri": "0",
                  "abil_slot": abil_slot,
                  "frequency": "3500",  # unit MHz
                  "bandwidth": bandwidth,   # unit MHz
                  "rru_name": "AEQB",
                  "rru_version": "1.0",
                  "tx_power": "34.9",
                  "fiber_length": "5",
                  "ul_rb_offset": "0"
                  }
    radio_carrier_dict = {
        "virtual_ant": "[1, 2]",
        "ant_mapping": "[antenna1a, antenna2a]",
        "tx_array_p": "[TxArrayStream1]",
        "tx_position_p": "[0]",
        "tx_array_m": "[TxArrayStream2]",
        "tx_position_m": "[960]",
        "rx_array_p": "[RxArrayStream1]",
        "rx_position_p": "[0]",
        "rx_array_m": "[RxArrayStream2]",
        "rx_position_m": "[960]"
    }
    resources_folder = path_join('..', '..', 'resources', 'bacardi', 'TDD', 'auto_generated')
    xml_file = f"autogen_{tm}_{ul_case}_{bw}MHz_{rru}_{feature_id}.xml"
    target_xml = path_join(resources_folder, xml_file)
    if not force_rewrite:
        if Path(target_xml).is_file():
            _msg = (200, "The file has existed and force_rewrite = false", xml_file[:-4])  # remove '.xml' extension
            print(_msg)
            return _msg

    result = TM_XML_Gen.main(tm=tm, ul_case=ul_case, bw=bw, unit_name=rru, abil_slot=abil_slot, case_type=case_type,
                             target_xml=target_xml, feature_id=feature_id)
    print(result)
    _msg = (200, "The file has been generated", xml_file[:-4])  # remove '.xml' extension
    print(_msg)
    return _msg


def change_testmode(setting_data):

    dl_mode = setting_data['str_dl_mode']
    ul_mode = setting_data['str_ul_mode']
    bandwidth = setting_data['str_bandwidth']
    tdd_switch = setting_data['str_tdd_switch']
    rru_mode = setting_data['str_rru_mode']
    frequency_list = setting_data['str_frequency']
    power_list = setting_data['str_power']
    cell_id_list = setting_data['str_cell_id_list'] if 'str_cell_id_list' in setting_data.keys() else []
    rnti_list = setting_data['str_rnti_list'] if 'str_rnti_list' in setting_data.keys() else ["0", "0"]
    pusch_rb_offset_list = setting_data['str_pusch_rb_offset'] if 'str_pusch_rb_offset' in setting_data.keys() else  []
    pdsch_power_backoff_list = setting_data['str_pdsch_power_backoff'] if 'str_pdsch_power_backoff' in setting_data.keys() else []
    auto_gen = setting_data['bool_auto_gen']
    test_type = setting_data['str_test_type'] if 'str_test_type' in setting_data.keys() else "TestMode"
    case_type = setting_data['str_case_type']
    abil_slot = "3"
    force_rewrite = True
    feature_id = setting_data['str_feature_id']

    # rru_mode = get_rru_mode(rru_mode)
    if test_type in ["BFCal"]:
        l1_tc_xml = f"LibraryParametersExample_2x2_MIMO_{bandwidth}MHz_{rru_mode}_BFCal"
    else:
        if auto_gen:
            _, _, l1_tc_xml = generate_xml_config(dl_mode, ul_mode, bandwidth, rru_mode, abil_slot, force_rewrite=force_rewrite,
                                                  case_type=case_type, feature_id=feature_id)
        else:
            if ul_mode == "A1-2":
                dl_mode = "TM1_1"
                print("Only the DL TM1_1 case includes UL A1-2, so change to it.")
            elif ul_mode == "A2-5":
                dl_mode = "TM3_1A"
                print("Only the DL TM3_1A case includes UL A2-5, so change to it.")
            l1_tc_xml = f"LibraryParametersExample_{dl_mode}_{ul_mode}_{bandwidth}MHz_{rru_mode}"

    param_dict = {
        "frequency": list(str(int(float(frequency) * 10**6)) for frequency in frequency_list),
        "power": power_list,
        "cellId": cell_id_list,
        "rnti": rnti_list,
        "puschStartPrb": pusch_rb_offset_list,
        "pdschPowerBackoff": pdsch_power_backoff_list,
        "feature_id": feature_id
    }

    if tdd_switch != "1116_3ms" and tdd_switch != "":
        from nokia_5G_hwiv_configuration.libraries.testmode_gen.TestModeGen import path_join
        from nokia_5G_hwiv_configuration.libraries.common_lib.config_util import load_cfg, convert_value_type_to_list
        file = path_join('..', '..', 'Input', 'tddtiming_mapping.json')
        pattern_cfg = load_cfg(file)
        pattern_mapping = pattern_cfg.get(tdd_switch, None)
        if pattern_mapping is not None:
            convert_value_type_to_list(pattern_mapping)
            param_dict = {**param_dict, **pattern_mapping}
    elif tdd_switch == "":
        param_dict.update({"tddPattern": ['']})

    xml_handler = PathLib(tc_l1_xml=l1_tc_xml)
    l1_tc_xml_modified = xml_handler.modify_parameters(param_dict)
    return l1_tc_xml_modified

# main(l1_xml)
# time.sleep(10)

###################################################################################################################

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



    def pre_test(self, l1_xml, setting_data, test_options):
        DpdinFlag = test_options['DpdinFlag']
        JesdFlag = test_options['JesdFlag']
        CpriFlag = test_options['CpriFlag']
        CpriRepeatTimes = test_options['CpriRepeatTimes']
        JesdRepeatTimes = test_options['JesdRepeatTimes']
        DpdinRepeatTimes = test_options['DpdinRepeatTimes']

        if setting_data['made_num'] == 4:
            made_ips = ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5']
        else:
            made_ips = ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5',
                        '192.168.101.6', '192.168.101.7', '192.168.101.8', '192.168.101.9']
        beamer_ip = '192.168.101.1'
        str_rru_mode = setting_data['str_rru_mode']

        DutStatusHandler = DUT_Status(made_ips, beamer_ip, product_type=str_rru_mode)
        if not DutStatusHandler.check_dut_status():
            raise DUTNotReadyException("DUT status not ready!")
        self.check_if_pause()
            # if True:
            # raise DUTNotReadyError("this is a dummy error!")
        # L1_STATUS = 'PASS'

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
        # self.check_if_pause()
        time.sleep(40)
        # disable_auto_reboot(beamer_ip)

        if CpriFlag:
            CpriSyncHandler = CpriSync()
            if not CpriSyncHandler.Cpri_test(REPEAT=CpriRepeatTimes):
                raise CpriSyncFailException("Cpri link sync failed..unit will reboot")
            # self.check_if_pause()
        if JesdFlag:
            time.sleep(260)
            JesdVerifyHandler = JesdVerify(made_ips=made_ips, product_type=str_rru_mode)
            self.jesd_test_pass = JesdVerifyHandler.JesdTest(JesdRepeatTimes)
            # self.check_if_pause()
        if DpdinFlag: # or UdpcpFlag or SoapFlag
            DpdinCheckHandler = DpdinStatus(made_ips)
            self.dpdin_test_pass = DpdinCheckHandler.DPDIN_test(repeat=DpdinRepeatTimes)
            if not self.dpdin_test_pass:
                self.set_pause_flag()
            self.check_if_pause()


    def start(self, setting_data, test_options):
        root_path = os.path.dirname(os.path.realpath(__file__))
        PSU = visaInstrument()
        PSU_Controller = PSU.PowerSuppy_Init("GPIB", "11")
        l1_xml = change_testmode(setting_data)
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
            PSU.PowerSuppy_ON(PSU_Controller)
            # SerialLog = getattr(__import__("serial_log"), 'SerialLog')
            # serialLog = SerialLog()
            # t_serial = Thread(target=serialLog.run)
            # t_serial.start()
            # start reading temperature thread
            # from tools_dev.connections.RecordTemperature import RecordTemperature
            # record_temp = RecordTemperature()
            # t_record_temp = Thread(target=record_temp.run, args=(setting_data['made_num']*8, 18, "AENB"))
            # t_record_temp.start()
            try:
                self.pre_test(l1_xml, setting_data, test_options)
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
            except:
                e = sys.exc_info()[0]
                logger.error(f"unexpected error during test: {e}")
                self.check_if_pause()
            finally:
                # serialLog.catch_log()
                print("wait for thread finish..")
                # serialLog.terminate()
                # t_serial.join()
                # record_temp.terminate()
                # t_record_temp.join()

                PSU.PowerSuppy_OFF(PSU_Controller)
                time.sleep(5)
                main_result['total test'] += 1
            root_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(root_path, 'testings/MainTestResults/main_result.json'), 'w') as f:
                json.dump(main_result, f)


if __name__ == '__main__':
    setting_data = {
        'made_num': 4,
        'str_dl_mode': "TM1_1",  # refer to comments above
        'str_bandwidth': "40",  # Mhz
        'str_frequency': ["2350"],  # MHz
        'str_power': ["38.75"],  # dBm
        # 'str_pusch_rb_offset': '0',
        'str_ul_mode': "A1-5",  # A1-5, A2-5
        # 'str_pdsch_power_backoff': "0",  # dB
        'str_rru_mode': "AENB",  # "AEQB", "AEQZ"
        # 'str_test_type': "TestMode",  # "TestMode", "BFCal"
        'bool_auto_gen': True,
        'str_tdd_switch': "1116_3ms",
        'str_case_type': "1CC",
        'str_feature_id': "2402"
    }
    test_options = {
                    'CycleTimes': 300,
                    'CpriFlag': True,
                    'CpriRepeatTimes': 1,
                    'JesdFlag': True,
                    'JesdRepeatTimes': 3,
                    'UdpcpFlag': False,
                    'SoapFlag': False,
                    'DpdinFlag': True,
                    'DpdinRepeatTimes': 1}
    cv = threading.Condition()
    preVerification = PreVerification(cv)
    preVerification.start(setting_data, test_options)
