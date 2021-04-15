# -*- coding: cp1252 -*-
from time import sleep
from nokia_5G_hwiv_configuration.libraries.common_lib.TimingConfiguring import TimingConfiguring
from nokia_5G_hwiv_configuration.libraries.common_lib.CpriConfiguring import CpriConfiguring
from nokia_5G_hwiv_configuration.libraries.rf_lib.RadioCarrierConfig import RadioCarrierConfig, FixedDelayException
from nokia_5G_hwiv_configuration.libraries.rf_lib.BeamerSetup import AfterRun, BeforeRun
import copy
import re

debug_flag = False


class StartupAndCellSetup:
    def __init__(self, var, env, lib, logger):
        self.var = var
        self.env = env
        self.lib = lib
        self.logger = logger
        self.cpri_configuring = CpriConfiguring(var, lib, logger)
        self.timing_config = TimingConfiguring(var, lib, logger, self.cpri_configuring)
        self.radio_carrier_config = RadioCarrierConfig(var, lib, logger, self.timing_config)

    def startup_and_cell_setup(self, test_case_start_time):
        if self.var.fdd_conf:
            self.fdd_startup_and_cell_setup(test_case_start_time)
            return

        # Create syscom objects before using syscom messages.
        soap_init_done = False
        ethernet_over_cpri_configured = False
        self.lib.loner_hwiv_bb.create_syscom_objects_for_hosts()
        second_fsp = False
        discovery_ind_with_syscom = False
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                # ------------------------------------------------------------------------------------------------------
                # Configure ethernet over cpri
                # Set ASIK and ABIL routing and start the DHCP server if Ethernet over cpri is used
                # ------------------------------------------------------------------------------------------------------
                if getattr(self.env, "ethernet_over_cpri",
                           False) and ethernet_over_cpri_configured is False and second_fsp is False:
                    bb_client = self.lib.loner_hwiv_bb.declear_ssh_client_in_use_for_host(fsp["Id"])
                    if not self.lib.loner_hwiv_fct.configure_ethernet_over_cpri(system_module, bb_client):
                        self.logger.debug("Could not start the DHCP server!")  # test should end here
                        raise Exception("Could not start the DHCP server!")
                    else:
                        second_fsp = True
                # ------------------------------------------------------------------------------------------------------
                # CPRI link setup with Syscom messages
                # 1. CPRI setup for each CPRI link is made.
                # ------------------------------------------------------------------------------------------------------
                self.cpri_configuring.cpri_link_setup(fsp)

            for fsp in system_module["FspSettings"]:
                self.cpri_configuring.cpri_link_enable(fsp)
                if fsp["Cells"][0]["Scs"] < 120 and fsp.get("fe_release") in ["20A"]:
                    self.cpri_configuring.cpri_configure_axc_info(fsp)

            if getattr(self.env, "ethernet_over_cpri", False) and ethernet_over_cpri_configured is False:
                self.lib.loner_hwiv_bb.add_dhcp_address_to_fsp(fsp, debug=True)

        # ------------> AEUA/AEWF WA for PR416711 <------------
        # ----------------------------------------------------------------------------------------------------------
        for radio in self.var.RadioModules:
            soap_init_done = False
            self.var.soap_rm_id = radio["Id"]
            self.var.soap_rm_name = radio["Name"]
            fsps = list(self.get_fsps_connected_to_radio(radio))
            system_modules = list(self.get_system_modules_connected_to_radio(radio))

            for fsp in fsps:
                self.timing_config.add_fsp_timing(fsp["Id"])
            self.timing_config.add_radio_timing(radio["Id"])

            # ------------------------------------------------------------------------------------------------------
            # ------------> AAHF WA <------------
            # ------------------------------------------------------------------------------------------------------
            if radio.get("Board", "") == "jaska_plus" and radio.get("Name", "") == "AAHF":
                self.lib.viisgbb_hwiv_rf.jaska_plus.aahf_init(radio)
            # do nothing if RF is different than "AEUA", "AEWF", "AEUD", "AEUB"
            self.switch_radio_power_on(radio, fsps)

            # Added by L1 INT3
            # hcwang config relay on abil and asik
            radio_list = ["AEQB", "AEQV", "AEQZ"]
            if radio.get("Name", "") in radio_list:
                beamer_setup_b = BeforeRun(logger=self.logger)
                beamer_setup_a = AfterRun(logger=self.logger)
                self.logger.info(f"Workaround for {radio.get('Name', '')}, do dhcp relay on ABIL and ASIK")
                self.lib.loner_hwiv_bb.config_dhcp_relay_service(fsp, fsp['SlotIndex'])
                self.lib.loner_hwiv_fct.enable_dhcp_relay(system_module)
                beamer_setup_b.run_env_cfg(beamer_setup_a)

            if getattr(self.env, "rf_manual_conf", False) is False:
                # ----------------------------------------------------------------------------------------------
                # ------------> WA for radios with no soap functionality <------------
                # ----------------------------------------------------------------------------------------------
                if radio["ControlType"] in ["cli", "frmon"]:
                    self.radio_config(test_case_start_time)
                elif soap_init_done is False and radio["ControlType"] not in ["cli", "frmon"]:
                    if getattr(self.env, "ethernet_over_cpri", False) and discovery_ind_with_syscom is False:
                        for fsp in fsps:
                            self.lib.loner_hwiv_bb.cpri_link_discovery_ind_with_syscom_msg(fsp)
                    self.env.sleep_with_prints(10)

                    # If Ethernet over CPRI functionality is used.
                    # The IP address of radio is read from the DHCP server lease file at ASIK
                    if getattr(self.env, "ethernet_over_cpri", False) and ethernet_over_cpri_configured is False:
                        if getattr(self.env, "router_over_cpri", False) is False:
                            for i, dfe in enumerate(radio["Dfes"]["Dfe"]):
                                self.env.int_dut.ping_host(dfe["Ip"], self.var.power_reset_ping_count)
                        if discovery_ind_with_syscom is False:
                            self.lib.loner_hwiv_fct.wait_for_ip_from_lease_file(system_modules[0],
                                                                                len(self.var.RadioModules),
                                                                                wait_loops=16)
                            discovery_ind_with_syscom = True
                        rf = getattr(self.lib.viisgbb_hwiv_rf, radio["Board"])
                        beamforming_used = True if fsps[0]["Cells"][0].get("actBeamforming", 0) == 1 else False
                        for ru in self.var.RadioModules:
                            fsps = list(self.get_fsps_connected_to_radio(ru))
                            rf.add_router_to_radio(fsps[0], ru)
                            if ru.get("Name", "") in ["AZQO"] and beamforming_used is True:
                                rf.add_router_to_radio(fsps[0], ru, cmd="bfcali -stop")

                        ethernet_over_cpri_configured = True

                    # Added by L1 INT3
                    if radio.get("Name", "") in radio_list:
                        beamer_setup_a.setup_route_for_dhcp(fsp['SlotIndex'])

                    if getattr(self.env, "ethernet_over_cpri", False) is False:
                        self.lib.soap.soap_init()
                    else:
                        self.lib.soap.soap_init(radio.get("Ip"))
                    rf_mac = self.lib.soap.mri_params.get("nodeLabel", "0200c0a8040a0000")
                    radio["ruMacAddress"] = list(int(f"0x{rf_mac[s:s + 2]}", 16) for s in range(0, 12, 2))

            # --------------------------------------------------------------------------------------------------
            # Radio module initialization
            # --------------------------------------------------------------------------------------------------
            if radio.get("ControlType", "") == "soap":
                sleep(1)  # for AZQG
                self.radio_carrier_config.radio_module_initialization(radio, fsps[0])

            # --------------------------------------------------------------------------------------------------
            # CPRI timing exchange
            # --------------------------------------------------------------------------------------------------
            for fsp in fsps:
                # separated self.cpri_timing_exchance(fsp, radio)
                self.timing_config.get_fsp_cpri_loop_delays(fsp)

            # asked from Radio
            self.timing_config.radio_timing_capability(radio)
            self.timing_config.get_radio_looping_delays(radio)

            for fsp in fsps:
                self.timing_config.get_fsp_fiber_delays(fsp, radio)

            for fsp in fsps:
                self.timing_config.get_total_delay(fsp, radio)

            for fsp in fsps:
                self.timing_config.set_fsp_delay_config(fsp, radio, 16000)

            # ----------------------------------------------------------------------------------------------------------
            # Syscom Get CPRI link parameter (ndl)
            # ----------------------------------------------------------------------------------------------------------
            for fsp in fsps:
                self.timing_config.get_fsp_dlul_offsets(fsp)

            # ----------------------------------------------------------------------------------------------------------
            # Cpri air frame timing
            # ----------------------------------------------------------------------------------------------------------
            cpri_air_frame_timing_par_dict = self.timing_config.get_cpri_air_frame_parameters(fsps, radio)

            if radio["ControlType"] == "soap":
                self.radio_carrier_config.radio_cpri_air_frame_time(radio, cpri_air_frame_timing_par_dict)

            # ------------------------------------------------------------------------------------------------------
            #   End of Cpri timing exchance
            # ------------------------------------------------------------------------------------------------------

            # ----------------------------------------------------------------------------------------------------------
            # tdd switching timing
            # ----------------------------------------------------------------------------------------------------------
            # tdd_switching_timing_par_dict = self.timing_config.get_tdd_switching_parameters(fsps, radio)
            #
            # if radio["ControlType"] == "soap" and self.var.eCpri is False and self.var.fdd_conf is False:
            #     self.radio_carrier_config.radio_tdd_switching_time(radio, tdd_switching_timing_par_dict)
            # Changed by L1 INT3
            tdd_pattern = radio.get("TddPattern", "")
            if "tddtiming.txt" in tdd_pattern:
                self.radio_carrier_config.send_tdd_switching_configuration(radio, tdd_pattern)

            # Added by L1 INT3
            # hcwang  for short term
            self.timing_config.calculate_variable_delay_dl(fsps, radio)
            self.timing_config.calculate_variable_delay_ul(fsps, radio)
            self.radio_carrier_config.radio_carrier_configuration(fsps, radio)

            # self.logger.debug("Start to close the soap!!!")
            # self.lib.soap.soap_close()
            # ------------------------------------------------------------------------------------------------------
            # Syscom cell setup
            # ------------------------------------------------------------------------------------------------------
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                self.lib.loner_hwiv_bb.cell_setup_with_syscom_msg(fsp)

            # ----------------------------------------------------------------------------------------------------------
            # Syscom cell setup
            # ----------------------------------------------------------------------------------------------------------
        for radio in self.var.RadioModules:
            self.var.soap_rm_id = radio["Id"]
            self.var.soap_rm_name = radio["Name"]
            # if getattr(self.env, "ethernet_over_cpri", False) is False:
            #     self.lib.soap.soap_init(detect_mri=False)
            # else:
            #     self.lib.soap.soap_init(radio.get("Ip"), detect_mri=False)
            if (radio.get("ControlType", "") != "cli" and radio.get("ControlType", "") != "frmon" and
                    getattr(self.env, "rf_manual_conf", False) is False):
                # self.logger.warning("xxx need to be verified by L1 INT3")
                # if "tddtiming.txt" in radio.get("TddPattern", ""):
                #     self.radio_carrier_config.send_tdd_switching_configuration(radio, radio["TddPattern"])

                # try:
                #     self.radio_carrier_config.activate_carriers(radio)
                # except:
                #     # WA For both FDD/TDD, still under investigation !!!!!!!!!!!!!!!!!!!
                #     self.logger.warning("\n\nWas not able to activate carriers after cell setup\n\n.")
                #     sleep_time = 5
                #     for i in range(0, 125, sleep_time):
                #         self.logger.warning(f"WAITING {i}/120s")
                #         sleep(sleep_time)
                #         self.logger.warning(f"Trying to activate carriers again.")
                #         try:
                #             self.radio_carrier_config.activate_carriers(radio)
                #             break
                #         except:
                #             pass
                self.radio_carrier_config.activate_carriers(radio)
                # Syscom CPRI Delay Configuration (nUl)
                # nUl exchange is done after carrier activation, ref. CPRI on ABIL 5G19B
                self.radio_carrier_config.set_nul_value(fsps, radio)
            self.lib.soap.soap_close()

    def fdd_startup_and_cell_setup(self, start_time):
        ethernet_over_cpri_configured = False
        self.lib.loner_hwiv_bb.create_syscom_objects_for_hosts()
        second_fsp = False
        for radio in self.var.RadioModules:
            radio['Ip'] = ""
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                # ------------------------------------------------------------------------------------------------------
                # Configure ethernet over cpri
                # Set ASIK and ABIL routing and start the DHCP server if Ethernet over cpri is used
                # ------------------------------------------------------------------------------------------------------
                if getattr(self.env, "ethernet_over_cpri",
                           False) and ethernet_over_cpri_configured is False and second_fsp is False:
                    bb_client = self.lib.loner_hwiv_bb.declear_ssh_client_in_use_for_host(fsp["Id"])
                    if not self.lib.loner_hwiv_fct.configure_ethernet_over_cpri(system_module, bb_client):
                        self.logger.debug("Could not start the DHCP server!")  # test should end here
                        raise Exception("Could not start the DHCP server!")
                    else:
                        second_fsp = True
                # ------------------------------------------------------------------------------------------------------
                # CPRI link setup with Syscom messages
                # 1. CPRI setup for each CPRI link is made.
                # ------------------------------------------------------------------------------------------------------
                self.cpri_configuring.cpri_link_setup(fsp)

            for fsp in system_module["FspSettings"]:
                self.cpri_configuring.cpri_link_enable(fsp)
                self.cpri_configuring.cpri_configure_axc_info(fsp)

                if getattr(self.env, "ethernet_over_cpri", False) and ethernet_over_cpri_configured is False:
                    self.lib.loner_hwiv_bb.add_dhcp_address_to_fsp(fsp, debug=True)

        # -- FDD multi cell setup
        self.fhs_setup(self.var)
        self.var.soap_rm_ip_address = ""
        for radio in self.var.RadioModules:
            self.var.soap_rm_ip_address = ""
            if not radio['Name'] in ["MDEA"]:
                self.var.soap_rm_id = radio["Id"]
                self.var.soap_rm_name = radio["Name"]
                fsps = list(self.get_fsps_connected_to_radio(radio))
                system_modules = list(self.get_system_modules_connected_to_radio(radio))
                if radio.get("Ip", "") == "":
                    self.env.int_dut.power_reset(self.var, radio, state="On")
                    self.env.sleep_with_prints(60, 30)
                    for fsp in fsps:
                        carrier_cprilink_dic, cell_cprilink_dic = \
                            self.cpri_configuring.get_carrier_cprilink_from_radio_fsp(fsp, radio)
                        for cprilink in carrier_cprilink_dic:
                            self.cpri_configuring.cpri_vsb_configure(fsp, cprilink)

                if getattr(self.env, "rf_manual_conf", False) is False:
                    # ----------------------------------------------------------------------------------------------
                    # ------------> WA for radios with no soap functionality <------------
                    # ----------------------------------------------------------------------------------------------
                    if radio["ControlType"] == "cli" or radio["ControlType"] == "frmon":
                        self.radio_config(start_time)
                    else:
                        if self.lib.loner_hwiv_fct.\
                                wait_for_ip_from_lease_file_no_discovery_ind(system_modules[0], wait_loops=16):
                            radio['Ip'] = self.var.soap_rm_ip_address
                            for fsp in fsps:
                                self.lib.loner_hwiv_bb.wa_route_for_fdd(fsp, radio.get("Ip"))
                            if self.lib.int_dut.ping_host(ip_to_ping=radio.get("Ip"), ping_time=1, ping_count=3) \
                                    is False:
                                self.logger.debug("Error, Could not access radio, cases will be fail!")
                        else:
                            self.logger.debug("Error, Could not access radio, cases will be fail!")
                        self.lib.soap.soap_init(rru_ip=radio.get("Ip"))
                        rf_mac = self.lib.soap.mri_params.get("nodeLabel", "0200c0a8040a0000")
                        radio["ruMacAddress"] = list(int(f"0x{rf_mac[s:s + 2]}", 16) for s in range(0, 12, 2))

                self.env.sleep_with_prints(10)
                for fsp in fsps:
                    carrier_cprilink_dic, cell_cprilink_dic = \
                        self.cpri_configuring.get_carrier_cprilink_from_radio_fsp(fsp, radio)
                    for cprilink in carrier_cprilink_dic:
                        for carrier in carrier_cprilink_dic[cprilink]:
                            self.radio_carrier_config.Fdd_radio_carrier_configuration(fsp, radio, carrier, cprilink)
                        for cell in cell_cprilink_dic[cprilink]:
                            self.timing_config.fdd_timing_exchance(fsp, radio, cprilink, cell)
                # ------------------------------------------------------------------------------------------------------
                # Syscom cell setup
                # ------------------------------------------------------------------------------------------------------
                for fsp in fsps:
                    clear_fsp = self.get_fsp_only_cells_of_radio(fsp, radio)
                    self.lib.loner_hwiv_bb.cell_setup_with_syscom_msg(clear_fsp)

                # ----------------------------------------------------------------------------------------------------------
                # Syscom cell setup
                # ----------------------------------------------------------------------------------------------------------
                if (radio.get("ControlType", "") != "cli" and radio.get("ControlType", "") != "frmon" and
                        getattr(self.env, "rf_manual_conf", False) is False):
                    try:
                        self.radio_carrier_config.activate_carriers(radio)
                    except Exception as e1:
                        # WA For both FDD/TDD, still under investigation !!!!!!!!!!!!!!!!!!!
                        self.logger.warning("\n\nWas not able to activate carriers after cell setup\n\n.")
                        print(str(e1))
                        sleep_time = 5
                        for i in range(0, 125, sleep_time):
                            self.logger.warning(f"WAITING {i}/120s")
                            sleep(sleep_time)
                            self.logger.warning(f"Trying to activate carriers again.")
                            try:
                                self.radio_carrier_config.activate_carriers(radio)
                                break
                            except Exception as e2:
                                print(str(e2))
                                pass
                self.lib.soap.soap_close()
        return

    def no_rf_startup_and_cell_setup(self):
        # Create syscom objects before using syscom messages.
        self.lib.loner_hwiv_bb.create_syscom_objects_for_hosts()
        ethernet_over_cpri_configured = False
        # ------------------------------------------------------------------------------------------------------
        # Configure ethernet over cpri
        # Set ASIK and ABIL routing and start the DHCP server if Ethernet over cpri is used
        # ------------------------------------------------------------------------------------------------------
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                # ------------------------------------------------------------------------------------------------------
                # Configure ethernet over cpri
                # Set ASIK and ABIL routing and start the DHCP server if Ethernet over cpri is used
                # ------------------------------------------------------------------------------------------------------
                if getattr(self.env, "ethernet_over_cpri", False) and ethernet_over_cpri_configured is False:
                    bb_client = self.lib.loner_hwiv_bb.declear_ssh_client_in_use_for_host(fsp["Id"])
                    if not self.lib.loner_hwiv_fct.configure_ethernet_over_cpri(system_module, bb_client):
                        self.logger.debug("Could not start the DHCP server!")  # test should end here
                        raise Exception("Could not start the DHCP server!")

                # ------------------------------------------------------------------------------------------------------
                # CPRI link setup with Syscom messages
                # 1. CPRI setup for each CPRI link is made.
                # ------------------------------------------------------------------------------------------------------
                self.cpri_configuring.cpri_link_setup(fsp)
                self.cpri_configuring.cpri_link_enable(fsp)
                if getattr(self.env, "ethernet_over_cpri", False) and ethernet_over_cpri_configured is False:
                    self.lib.loner_hwiv_bb.add_dhcp_address_to_fsp(fsp, debug=True)
                    ethernet_over_cpri_configured = True

                # ------------------------------------------------------------------------------------------------------
                # Syscom cell setup
                # ------------------------------------------------------------------------------------------------------
                self.lib.loner_hwiv_bb.cell_setup_with_syscom_msg(fsp)

    def get_fsps_connected_to_radio(self, radio):
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                if radio["Id"] in list(rf["RadioId"] for cell in fsp["Cells"] for rf in cell["Rfs"]):
                    yield fsp

    def get_system_modules_connected_to_radio(self, radio):
        for system_module in self.var.SystemModules:
            for fsp in system_module["FspSettings"]:
                if radio["Id"] in list(rf["RadioId"] for cell in fsp["Cells"] for rf in cell["Rfs"]):
                    yield system_module

    def switch_radio_power_on(self, radio, fsps):
        radio_list = ["AEUA", "AEWF", "AEUD", "AEUB", "AZQO"]
        if radio.get("Name", "") in radio_list:
            self.logger.info("WA for PR416711: "
                             f"Power restart for {', '.join(radio_list)} if both fibres are connected!")
            self.env.int_dut.power_reset(self.var, radio, state="On")
            if radio.get("power") is not None:
                sleep_time = 15 if len(fsps) >= 2 else 30
                self.logger.info("WA for PR416711: "
                                 f"Sleeping {sleep_time} seconds after {', '.join(radio_list)} power on.")
                self.env.sleep_with_prints(sleep_time)
        if self.var.fdd_conf and self.var.power_reset:
            self.logger.info("FDD RRH power on for get ip address of radio(id):" + str(radio["Id"]) + ".")
            self.env.int_dut.power_reset(self.var, radio, state="On")

    def get_fsp_only_cells_of_radio(self, fsp, radio):
        def fsp_copy_without_cell():
            output_fsp = {}
            for fsp_key in fsp:
                if fsp_key != 'Cells':
                    output_fsp[fsp_key] = fsp[fsp_key]
                else:
                    output_fsp['Cells'] = []
            return output_fsp

        _, cell_cprilink_dic = self.cpri_configuring.get_carrier_cprilink_from_radio_fsp(
            fsp, radio)
        fsp_return = fsp_copy_without_cell()
        for dic_key in cell_cprilink_dic:
            for internal_cell in cell_cprilink_dic[dic_key]:
                cell_info = copy.deepcopy(internal_cell)
                fsp_return['Cells'].append(cell_info)
        return fsp_return

        # --------------------------------------------------------------------------------------------------------------
        #   End of Cpri timing exchance
        # --------------------------------------------------------------------------------------------------------------

    def radio_config(self, test_case_start_time):
        for rf in self.var.RadioModules:
            if rf["ControlType"] == "cli" or rf["ControlType"] == "frmon":
                self.logger.debug("Note: cli in use!")
                if rf["Board"] == "jaska_pp":
                    self.lib.viisgbb_hwiv_rf.jaska_pp.common_tc_init(rf)
                elif rf["Board"] == "jaska_plus":
                    if rf["Name"] == "AAHF":
                        self.lib.viisgbb_hwiv_rf.jaska_plus.aahf_init()
                    else:
                        self.lib.viisgbb_hwiv_rf.jaska_plus.common_tc_init(rf)
                elif rf["Board"] == "sally":
                    self.lib.viisgbb_hwiv_rf.sally.common_tc_init(rf)
                self.lib.viisgbb_hwiv_rf.dfe_configuration(rf, test_case_start_time=test_case_start_time)

                if rf["Board"] == "jaska_pp":
                    if rf["Name"] in ["AEUD", "AEUB"]:
                        self.lib.viisgbb_hwiv_rf.malli_configuration(rf)
                        self.lib.viisgbb_hwiv_rf.ptp_sync_check()
                    if rf["Name"] == "AEUA":
                        self.lib.viisgbb_hwiv_rf.dfe_cpri_router_axc_antenna_mapping(
                            dfe_name="jaska_1", pattern="Default",
                            custom_list_rx=[i for i in range(16)],
                            custom_list_tx=[i for i in range(16)])

            else:
                self.logger.debug("Note: RP1/SOAP in use!")

    def fhs_setup(self, var):
        def power_on_related_radio(input_radios, input_fsps, radios):
            for one_radio in radios:
                for power_on_radio in input_radios:
                    if one_radio['Id'] == power_on_radio:
                        self.switch_radio_power_on(one_radio, input_fsps)

        def get_fsps_connected_to_fhs(radio_input):
            for system_module in self.var.SystemModules:
                for fsp in system_module["FspSettings"]:
                    if radio_input["Fhs_index"] in list(rf["FhsId"] for cell in fsp["Cells"] for rf in cell["Rfs"]):
                        return fsp

        def get_radios_connected_to_fhs(radio_input):
            related_radios_id_list = list()
            for system_module in self.var.SystemModules:
                for fsp in system_module["FspSettings"]:
                    for cell in fsp["Cells"]:
                        for Rf in cell["Rfs"]:
                            if radio_input["Fhs_index"] == Rf["FhsId"]:
                                related_radios_id_list.append(Rf["RadioId"])
            return related_radios_id_list

        def fhs_soap_configure(input_rf):
            def ret_s_value(bw):
                if bw == 5000000:
                    s = 2
                elif bw == 10000000:
                    s = 4
                elif bw == 15000000:
                    s = 6
                else:
                    s = 8
                return s
            input_par_dict = {"newState": "enabled"}
            self.lib.soap.send_msg_to_radio(message='Fhs_ModuleStateChange', rf=input_rf, par_dict=input_par_dict)
            for channel in input_rf["CarrierSettings"]['Carrier']:
                parameters = {"Tx_channel_distName": str(channel['TxContainer'][0]['DistName'][0]),
                              "Tx_source": str(channel['TxContainer'][0]['TxSource']),
                              "Tx_target": str(channel['TxContainer'][0]['TxTarget']),
                              "Tx_position": str(channel['TxContainer'][0]['Position'][0]),
                              "Tx_S": str(ret_s_value(channel['TxBandwidth'])),
                              "Rx_S": str(ret_s_value(channel['RxBandwidth'])),
                              "Rx_channel_distName": str(channel['RxContainer'][0]['DistName'][0]),
                              "Rx_source": str(channel['RxContainer'][0]['RxSource']),
                              "Rx_target": str(channel['RxContainer'][0]['RxTarget']),
                              "Rx_position": str(channel['RxContainer'][0]['Position'][0]),
                              "distName": "cpriPort" + str(channel['TxContainer'][0]['TxTarget'])
                              }
                fhs_soap_configure_one_channel(input_rf, parameters)
                for rrh in self.var.RadioModules:
                    if rrh['Id'] == channel['RadioId']:
                        self.lib.loner_hwiv_fct.wait_for_ip_from_lease_file(var.SystemModules[0], wait_loops=16)
                        rrh['ipaddress'] = radio['ipaddress'] = self.var.soap_rm_ip_address

        def fhs_soap_configure_one_channel(rf, parameter):
            input_par_dict = {"distName": parameter['distName'], "portMode": "MASTER",
                              "maxEthernetBitRate": "184312", "allowedBitrates": "9830"}
            self.lib.soap.send_msg_to_radio(
                message='Fhs_Cpriport', rf=rf,
                par_dict=input_par_dict)
            while True:
                input_par_dict = {"distName": parameter['distName']}
                rsp_dict, rsp_xml = self.lib.soap.send_msg_to_radio(message='Fhs_CpriportRetrieve',
                                                                    rf=rf, par_dict=input_par_dict)
                status = rsp_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['retrieveParameterRsp']['managedObject']
                status = status['parameter'][9]['newValue']
                self.logger.debug("CPRI status:" + status)
                if status == 'NOT_OPERATIONAL':
                    self.env.sleep_with_prints(60, 30)
                    continue
                else:
                    break

            input_par_dict = {"distName": parameter['Tx_channel_distName'], "S": parameter["Tx_S"],
                              "position": parameter['Tx_position'],
                              "source_port": parameter["Tx_source"], "target_port": parameter['Tx_target']}
            self.lib.soap.send_msg_to_radio(message='Fhs_CpriForwardingDownLink', rf=rf, par_dict=input_par_dict)
            input_par_dict = {"distName": "cpriForwardingOffsets"}
            self.lib.soap.send_msg_to_radio(message='Fhs_CpriForwardingOffsets', rf=rf, par_dict=input_par_dict)
            input_par_dict = {"distName": parameter['Rx_channel_distName'], "S": parameter["Rx_S"],
                              "position": parameter['Rx_position'],
                              "source_port": parameter["Rx_source"], "target_port": parameter['Rx_target']}
            self.lib.soap.send_msg_to_radio(message='Fhs_CpriForwardingUpLink', rf=rf, par_dict=input_par_dict)

        for radio in var.RadioModules:
            if radio['Name'] in ["MDEA"]:
                self.var.soap_rm_id = radio["Id"]
                self.var.soap_rm_name = radio["Name"]
                related_fsps = get_fsps_connected_to_fhs(radio)
                related_radios = get_radios_connected_to_fhs(radio)
                power_on_related_radio(related_radios, related_fsps, self.var.RadioModules)
                self.lib.loner_hwiv_bb.route_add_radio_fhs(related_fsps, radio.get('Ip'))
                self.lib.soap.soap_init()
                fhs_soap_configure(radio)
                self.lib.soap.soap_close()
