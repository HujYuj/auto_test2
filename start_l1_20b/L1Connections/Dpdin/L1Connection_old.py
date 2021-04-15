# -*- coding: cp1252 -*-
########################################################################################################################
#
# PROJECT:      L1
#
# DESCRIPTION: This case configures BTS & UE with python script register writing & reading.
#
# NOTE:
#
# Copyright (c) Nokia 2017. All rights reserved.
########################################################################################################################

########################################################################################################################
# Python library declarations
#
# NOTE: add here only python libraries if need (because project specific libs will be created below)
########################################################################################################################
from time import sleep
from datetime import datetime


from nokia_5G_hwiv_configuration.libraries.common_lib.InitializeAndVerifyDut import InitializeAndVerifyDut
from nokia_5G_hwiv_configuration.libraries.common_lib.PathLib import PathLib
from tools_dev.L1Connections.Dpdin.StartupAndCellSetup import StartupAndCellSetup
from nokia_5G_hwiv_configuration.resources.test_environment.json_keyword_mapper import JsonKeywordMapper
from nokia_5G_hwiv_configuration.libraries.viavi import TmaE500_control
import os


########################################################################################################################
# DEFINE this testcase related sub-function(s) here if needed
#
# NOTE: it is RECOMMEND to create the function under Common_libs if it will be used several testcases
########################################################################################################################
class L1Connection:

    def __init__(self, logger=None, var=None, addr=None, env=None, lib=None):
        self.var = var
        self.addr = addr
        self.env = env
        self.lib = lib
        self.logger = logger
        self.path_lib = PathLib()
        self.json_keyword_mapper = JsonKeywordMapper()
        self.init = InitializeAndVerifyDut(self.path_lib, self.logger)

        # Soap message variables
        self.port_number = []
        self.antenna_line = []
        self.downlink_fixed_delay = []
        self.uplink_fixed_delay = []
        self.antenna_carrier_type = []
        self.fixed_delay = []
        self.max_variable_delay = []

    def reinit(self, logger, var, addr, env, lib):
        """
        Reinit libraries. Needed for robot framework.
        :param var:     new var instance for new test case
        :param addr:    new addr instance for new test case
        :param env:     new env instance for new test case
        :param lib:     new lib instance for new test case
        :param logger   new logger instance for new test case
        :return:
        """
        self.var = var
        self.addr = addr
        self.env = env
        self.lib = lib
        self.logger = logger

    def enable_signalization_of_fct(self):
        first_fct = 1
        for system_module in self.var.SystemModules:
            enable_pps_int_to_sync_out = True
            clocks_source = "PPS"
            if first_fct == 0:
                enable_pps_int_to_sync_out = False
                # clocks_source = "Fronthaul"
            self.lib.loner_hwiv_fct.fct_oxco_tuning(frame_clock_type=getattr(self.var, "Frame_Clock_type", 1),
                                                    system_module=system_module,
                                                    enable_pps_int_to_sync_out=enable_pps_int_to_sync_out,
                                                    clocks_source=clocks_source)
            first_fct = 0

    def initialize_l1_sw_with_conf_files(self):
        self.logger.debug("\n" + "#"*100 +
                          "\n# L1 SW enabled for the configuration\n" +
                          "#"*100)
        reset_needed = dict()
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                self.logger.info("\n----------------------------------------\n"
                                 f"FCT: Configuring host {fsp['Id']} as: {fsp.get('Mode', '')}\n"
                                 "----------------------------------------")
                config_files_to_edit = [
                    "const_customizer.conf",  # default values expected to be OK matkinnu 7Oct2019
                    "slot_type_req.conf",
                    "test_modes.conf",
                    "ss_block_send_req_insert.conf",
                    "pdcch_send_req.conf",
                    "pucch_receive_req.conf",
                    "pusch_receive_req.conf",
                    "pdsch_insert.conf",
                    # "fpga_loader.conf"
                ]
                if fsp.get("fe_release") in ["19A", "19B"]:
                    config_files_to_edit.append("pattern_config_req.conf")
                if fsp.get("fe_release") in ["19B"]:
                    config_files_to_edit.append("rd_thresholds.conf")
                if self.var.eCpri:
                    config_files_to_edit.append("ecpri.conf")
                if len(fsp.get("PrachSlots", [])) > 0:
                    config_files_to_edit.append("prach_receive_req.conf")
                reset_needed[fsp["Id"]] = self.lib.loner_hwiv_bb.configure_l1sw(
                        system_module=system_module, bb_slot=fsp["SlotIndex"], fsp=fsp,
                        config_files_to_edit=config_files_to_edit)

        for system_module in self.var.SystemModules:
            sleep_time = 50 - (15 * len(system_module["FspSettings"]))
            sleep_time = 5 if sleep_time < 5 else sleep_time

            for fsp in system_module["FspSettings"]:
                for RadioModule in self.var.RadioModules:
                    # hcwang reboot RRU firstly
                    if RadioModule["Name"] in ["AEQB", "AEQV", "AEQA", "AEQZ"]:
                        self.init.ping_host(RadioModule["Dfes"]["Dfe"][0]["Ip"], self.var.power_reset_ping_count)
                        self.lib.jaska_plus.reboot(RadioModule, dfe_name='jaska_1')
                        # sleep(10)
                        # workaround for UL bler is equal to 0
                        # self.demapper_crash_workaround()
                        break

                if reset_needed.get(fsp["Id"]):
                    self.env.reset_sequence(fsp, power_reset=True if fsp["Type"] == "ASOD" else False,
                                            ping_host=True, open_ssh=True, bb_inst=None,
                                            system_module=system_module, sleep_time=sleep_time)

                for RadioModule in self.var.RadioModules:
                    if RadioModule["Name"] in ["AAHF"]:
                        self.lib.viisgbb_hwiv_rf.jaska_plus.reboot(RadioModule, dfe_name="jaska_1")
                        # self.init.power_reset(self.var, RadioModule, state="On")
                        self.env.sleep_with_prints(180)
                        break
                    # if RadioModule["Name"] in ["AEQB"]:
                    #     self.env.sleep_with_prints(180)
                    #     break

    def extract_l1_sw_tmp_folder(self):
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                self.lib.loner_hwiv_bb.get_l1sw_logs_from_host(fsp=fsp, config_file_path=self.path_lib.ROOT_PATH)

    def check_is_fsp_ready(self):
        """Funcktion needed for robot."""
        self.lib.loner_hwiv_bb.check_is_fsp_ready()

    def startup_and_cell_setup(self, test_case_start_time):
        # Create syscom objects before using syscom messages.
        if getattr(self.env, "rf_manual_conf", False) is False:
            StartupAndCellSetup(self.var, self.env, self.lib, self.logger).startup_and_cell_setup(test_case_start_time)
        else:
            StartupAndCellSetup(self.var, self.env, self.lib, self.logger).no_rf_startup_and_cell_setup()

    # This WA is needed as long as AEQN is not able to handle the TDD timing dynamically
    # If the TDD configuration file is not defined in LibraryParameters the possibly existing file is deleted
    # If there is no tddtimer.conf in AEQN it will use the default configuration (5GC001208)
    def set_aeqn_tdd_configuration(self, rf):
        self.logger.debug("Workaround for selecting the correct tddtimer.conf file for " + rf["Name"] + "!")
        self.lib.viisgbb_hwiv_rf.sally.common_tc_init(rf)
        self.lib.viisgbb_hwiv_rf.delete_tdd_configuration_file(rf)
        if len(rf.get("TddPattern", "")) > 12:
            self.lib.viisgbb_hwiv_rf.set_tdd_configuration_file(rf, rf["TddPattern"])

    def create_test_cases(self):
        #######################
        #  Currently only two options, L1Call and L1_DL_Connection (which will also be used for L1_UL_Connection)
        ######################
        try:
            self.test_case = 'L1_Call' if "L1CALL" in os.environ.get('L1_XML').upper() else "L1_DL_Connection"
            test_results = []
            if self.test_case == 'L1_Call':
                test_results = \
                    [{'name': '5G L1 Connection', 'result': 'fail'},
                     {'name': '5G L1 HW Configuration', 'result': 'fail'}]
            elif self.test_case == 'L1_DL_Connection':
                test_results = [{'name': '5G L1 HW Configuration', 'result': 'fail'}]
        except (TypeError, AttributeError):
            self.test_case = 'L1_Call'
            test_results = [{'result': 'no run'}]
            self.logger.warn("Creation of the test cases failed(Might be due missing environment")
        return test_results

    def run_test(self):
        self.test_results = self.create_test_cases()
        test_case_start_time = datetime.now()
        self.var, self.addr, self.env, self.lib = self.init.initialize()
        if self.logger.error_flag:
            self.logger.error("\n\n" + "#"*100 + "\n# Something wrong with the setup.\n" + "#"*100 + "\n\n")
            self.init.common_end_test_case(test_case_start_time, self.env, self.logger)
            return

        # Workaround for selecting the correct tddtimer.conf file for AEQN, AZQG and AZQH
        aeqn_exists = True if any(
                True for rf in self.var.RadioModules if rf["Name"] in ["AEQN", "AZQG", "AZQH"]) else False

        if aeqn_exists:
            if getattr(self.env, "aeqn_change_tdd_conf", False) is True:
                for rf in self.var.RadioModules:
                    self.set_aeqn_tdd_configuration(rf)
                    sleep(5)
                    self.init.power_reset(self.var, rf, state="Off")
                    sleep(5)
                    self.init.power_reset(self.var, rf, state="On")
                    sleep(30)

        # ----------------------------------------------------------------------------------------------------------
        # Check if FSP is ready to start test.
        # ----------------------------------------------------------------------------------------------------------
        self.check_is_fsp_ready()
        if getattr(self.env, "l1sw_start_only", False):
            self.logger.debug("\n" + "#" * 100 + "\n# L1SW start test done\n" + "#" * 100)
            self.init.common_end_test_case(test_case_start_time, self.env, self.logger)
            return
        else:
            self.logger.debug("\n" + "#"*100 + "\n# Starting configuration functionality\n" + "#"*100)

        # ------------------------------------------------------------------------------------------------------
        # FCT: Enable signalization of FCT
        # ------------------------------------------------------------------------------------------------------
        if self.var.run_fct_ocxo_tuning:
            self.enable_signalization_of_fct()

        # ------------------------------------------------------------------------------------------------------
        # L1 SW: Initialize L1 SW and cell set up if L1 sw used
        # ------------------------------------------------------------------------------------------------------
        if getattr(self.env, "l1sw_manual_conf", False) is False:
            self.initialize_l1_sw_with_conf_files()

        # ------------------------------------------------------------------------------------------------------
        # L1 SW: Switch ON the power for RF unit if L1 sw used
        # ------------------------------------------------------------------------------------------------------
        if self.var.TestMode == "L1SW":
            for rf in self.var.RadioModules:
                self.init.power_reset(self.var, rf, state="On")
            sleep(10)
            # Ping check that all dfe:s respond after power reset.
            for rf in self.var.RadioModules:
                for i, dfe in enumerate(rf["Dfes"]["Dfe"]):
                    self.init.ping_host(dfe["Ip"], self.var.power_reset_ping_count)
            self.env.sleep_with_prints(30)

        # ------------------------------------------------------------------------------------------------------
        # 5G18A  3GPP NSA Based BTS Startup and Cell Setup
        # ------------------------------------------------------------------------------------------------------
        self.check_is_fsp_ready()

        if len(self.var.RadioModules) or getattr(self.env, "rf_manual_conf", False):
            if self.var.TestMode == "L1":
                self.startup_and_cell_setup(test_case_start_time)
            else:
                # ----------------------------------------------------------------------------------------------
                # RF configuration
                # ----------------------------------------------------------------------------------------------
                if not aeqn_exists:
                    StartupAndCellSetup(self.var, self.env, self.lib, self.logger).radio_config(test_case_start_time)

        # ------------------------------------------------------------------------------------------------------
        # L1 SW: Extract L1 SW /tmp folder
        # ------------------------------------------------------------------------------------------------------
        self.extract_l1_sw_tmp_folder()
        if getattr(self.var, "viavi_e500_test_case", False):
            print('----------STARTING E500 TEST----------')
            TmaE500_control.TmaE500Control(self.logger).main()

        for test in self.test_results:
            test['result'] = 'fail' if self.logger.error_flag else 'pass'

        ############################################################################################################
        # Common ending of the testcase
        ############################################################################################################
        if len(self.var.RadioModules) and getattr(self.env, "rf_manual_conf", False) is False:
            if self.var.RadioModules[0]["ControlType"] == "soap":
                self.lib.soap.soap_close()
        self.init.common_end_test_case(test_case_start_time, self.env, self.logger)
