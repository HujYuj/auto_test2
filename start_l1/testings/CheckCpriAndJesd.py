import logging, time
try:
    from tools_dev.testings.CPRISyncCheck import CpriSync
    from tools_dev.testings.JESDVerify_AEQZ_multithread import JesdVerify
    from tools_dev.testings.activate_carriers_setting import ActivateCarriersSetting
    from tools_dev.testings.Exceptions import *
except:
    from CPRISyncCheck import CpriSync
    from JESDVerify_AEQZ_multithread import JesdVerify
    from activate_carriers_setting import ActivateCarriersSetting
    from Exceptions import *

def checkCpriAndJesd(activate_carriers_setting,CpriRepeatTimes,JesdRepeatTimes):
    # CPRISync_handler = CpriSync()
    # if not CPRISync_handler.Cpri_test(REPEAT=CpriRepeatTimes):
    #     raise CpriSyncFailException("Cpri link sync failed..unit will reboot")
    # time.sleep(300)

    handler = JesdVerify(made_ips=activate_carriers_setting.get_mades(),
                        product_type=activate_carriers_setting.get_rru())
    handler.JesdTest(REPEAT=JesdRepeatTimes)

if __name__ == "__main__":
    logger = logging.getLogger('main')
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    # file_handler = logging.FileHandler(
    #     filename=os.path.join(root_path, f'testings/MainTestResults/main_result.log'))
    # file_handler.setFormatter(formatter)
    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    # logger_main.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)
    activate_carriers_setting = ActivateCarriersSetting(ABIL_SLOT_NUMBER="3",
                                                        RRU="AEQY",
                                                        TDD_SWITCH="1116_3ms_a5",
                                                        CASE_TYPE="Single Carrier",
                                                        DL_TM="TM1_1",
                                                        BANDWIDTH="100",
                                                        FREQUENCY="3650",
                                                        POWER="36")
    checkCpriAndJesd(activate_carriers_setting, 200, 10)



