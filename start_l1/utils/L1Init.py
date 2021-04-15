from __future__ import annotations

from abc import ABC, abstractmethod
import logging, os, sys

logger = logging.getLogger("main")

try:
    from auto_test.start_l1.L1Connections.run_python import main
    from auto_test.start_l1.utils.activate_carriers import Web_handler
except:
    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(current_path))))
    from auto_test.start_l1.L1Connections.run_python import main
    from auto_test.start_l1.utils.activate_carriers import Web_handler

class L1Init:

    def __init__(self, L1_init_mode: L1InitMode):
        self.L1_init_mode = L1_init_mode

    def run(self, activate_carriers_setting):
        self.L1_init_mode.run(activate_carriers_setting)


class L1InitMode(ABC):

    @abstractmethod
    def run(self, activate_carriers_setting):
        pass

class L1InitModeActivateCarriers21A(L1InitMode):

    def run(self, activate_carriers_setting):
        web_handler = Web_handler()
        web_handler.activate_carriers(activate_carriers_setting)
        print("activate finish")
        # web_handler.check_cpri_ready_in_log()
        web_handler.verify_l1_finish()


class L1InitModeNoActivateCarriers21A(L1InitMode):

    def run(self, activate_carriers_setting):
        web_handler = Web_handler()
        web_handler.no_activate_carriers(activate_carriers_setting)
        # web_handler.check_cpri_ready_in_log()
        web_handler.verify_l1_finish()

class L1InitModeActivateCarriers20B(L1InitMode):

    def run(self, activate_carriers_setting):
        web_handler = Web_handler()
        web_handler.activate_carriers(activate_carriers_setting)
        print("activate finish")
        web_handler.verify_l1_finish()


class L1InitModeNoActivateCarriers20B(L1InitMode):

    def run(self, activate_carriers_setting):
        web_handler = Web_handler()
        web_handler.no_activate_carriers(activate_carriers_setting)
        web_handler.verify_l1_finish()


class L1InitModeActivateCarriers20A(L1InitMode):

    def run(self, activate_carriers_setting):
        from nokia_5G_hwiv_configuration.dev_debug import change_testmode
        l1_xml = change_testmode(dl_mode=activate_carriers_setting.get_dl_tm(),
                                 # TM1_1, TM1_2, TM2, TM2A, TM3_1, TM3_1A, TM3_2, TM3_3
                                 ul_mode=activate_carriers_setting.get_ul_tm(),  # A1-2, A1-5, A2-5
                                 bandwidth=activate_carriers_setting.get_bandwidth(),  # MHz, 100, 80, 60, 40, 20
                                 rru_mode=activate_carriers_setting.get_rru(),  #
                                 frequency_list=activate_carriers_setting.get_frequency(),  # MHz
                                 power_list=activate_carriers_setting.get_power(),  # dBm
                                 # cell_id_list=["1", "1"],
                                 # pusch_rb_offset_list=[85, 122],      # RB offset for PUSCH
                                 # pdsch_power_backoff_list=[20, 30],   # dB
                                 case_type=activate_carriers_setting.get_case_type(),
                                 # "1CC", "2CC", "Split", set it if auto_gen=True
                                 auto_gen=True,  # xml generation switch, True or False
                                 feature_id="2402",  # "1037" for 3GPP 15-1, "2402" for 3GPP 15-2
                                 )
        main(l1_xml, L1Connection_file='L1Connection', timeout=1200)


class L1InitModeNoActivateCarriers20A(L1InitMode):

    def run(self, activate_carriers_setting):
        main(l1_xml, L1Connection_file='L1Connection_jesd', timeout=1200)


def L1InitModeNone(L1InitMode):

    def run(self, activate_carriers_setting):
        pass


def select_L1_init_mode(test_options):

    if test_options["l1_version"] == "20A":
        if test_options["dpdin_flag"]:
            return L1InitModeActivateCarriers20A()
        elif test_options["jesd_flag"] or test_options["cpri_flag"]:
            return L1InitModeNoActivateCarriers20A()
    elif test_options["l1_version"] == "20B":
        if test_options["dpdin_flag"]:
            return L1InitModeActivateCarriers20B()
        elif test_options["jesd_flag"] or test_options["cpri_flag"]:
            return L1InitModeNoActivateCarriers20B()
    elif test_options["l1_version"] == "21A":
        if test_options["dpdin_flag"]:
            return L1InitModeActivateCarriers21A()
        elif test_options["jesd_flag"] or test_options["cpri_flag"]:
            return L1InitModeNoActivateCarriers21A()
    else:
        logger.error("not supported L1 init mode")
        return L1InitModeNone()

if __name__ == "__main__":
    from auto_test.start_l1.utils.activate_carriers_setting import ActivateCarriersSetting
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
        'l1_version': "20B",
        'CycleTimes': 500,
        'CpriFlag': True,
        'CpriRepeatTimes': 100,
        'JesdFlag': True,
        'JesdRepeatTimes': 3,
        'UdpcpFlag': False,
        'SoapFlag': False,
        'DpdinFlag': True,
        'DpdinRepeatTimes': 1}
    l1_init_mode = select_L1_init_mode(test_options=test_options)
    l1_init_handler = L1Init(l1_init_mode)
    l1_init_handler.run(activate_carriers_setting=activate_carriers_setting)