import os
import sys
import time
import logging
root_path = os.path.dirname(os.path.realpath(__file__))
# print('root_path: ' + root_path) # root_path = tools_dev
sys.path.insert(0, os.path.join(root_path, ".."))
# print('sys_path: ', sys.path) # add dut_control to system path
from nokia_5G_hwiv_configuration.dev_debug import get_rru_mode, generate_xml_config, change_testmode
# from nokia_5G_hwiv_configuration.run_python import main
from tools_dev.testings.JESDVerify_AEQZ_multithread import JesdVerify
from tools_dev.L1Connections.run_python import main
from tools_dev.connections.Instrument import visaInstrument
from tools_dev.testings.CheckDutStatus import DUT_Status
from tools_dev.testings.CPRISyncCheck import CpriSync
from tools_dev.testings.DpdinCheck import DpdinStatus
from tools_dev.testings.Exceptions import *
# from tools_dev.testings.settings import disable_auto_reboot


###################### case of reboot stress test ##########################
# power control


########################case of run JESD verifications #####################

# from tools_dev.testings.JESDVerify import JesdVerify
# JesdVerifyHandler = JesdVerify()
# JesdVerifyHandler.JesdTest()

########################cese of run CPRI sync test  ########################

# from tools_dev.testings.CPRISyncCheck import CPRISync
# # init_L1(l1_xml) # finish cpri sync
# CPRIsyncHandler = CPRISync()
# CPRISync.CPRI_test()

########################case of run Dpdin stress test ######################
# def runDpdinStressTest():
#     from tools_dev.testings.DpdinCheck import DpdinStatus
#     # init_L1(l1_xml) # finish activate carriers
#     DpdinStatusHandler = DpdinStatus()
#     DpdinStatusHandler.DPDIN_test()

###################### case of UDPCP stress test ###########################

# repeat of UDPCP L1 init


############################################################################
if __name__ == "__main__":
    root_path = os.path.dirname(os.path.realpath(__file__))
    logging.basicConfig(level=logging.INFO, filename=os.path.join(root_path, 'testings\JesdLogAndResults\JesdVerify.log'), format="%(asctime)s:%(levelname)s:%(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    stream_handler.setFormatter(formatter)
    logging.getLogger().addHandler(stream_handler)
    # print("root_path again: ", root_path)

    # sys.path.insert(0, root_path + os.sep + 'L1Connections' + os.sep + 'JESD')
    # sys.path.insert(0, root_path + os.sep + 'L1Connections' + os.sep + 'Dpdin')
    # print(sys.path)
    import getopt
    def usage():
        print(
            """
            Usage:sys.args[0] [option]
            -h or --help
            -d or --dl_mode
            -b or --bandwidth
            -f or --frequency
            -p or --power
            -o or --pusch_rb_offset
            -u or --ul_mode
            -k or --pdsch_power_backoff
            -m or --rru_mode
            -t or --test_type
            -g or --auto_gen
            """
        )


    str_dl_mode = "TM3_1A"  # refer to comments above
    str_bandwidth = "20"  # MHz
    str_frequency = "3500"  # MHz
    str_power = "10.9"  # dBm
    str_pusch_rb_offset = "0"
    str_ul_mode = "A1-5"  # A1-5, A2-5
    str_pdsch_power_backoff = "0"  # dB
    str_rru_mode = "AEQZ"  # "AEQB", "AEQZ"
    str_test_type = "TestMode"  # "TestMode", "BFCal"
    bool_auto_gen = False
    opts = ()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hd:b:f:p:o:u:k:m:t:g:',
                                   ["help", "dl_mode=", "bandwidth=", "frequency=", "power=", "pusch_rb_offset=",
                                    "ul_mode=", "pdsch_power_backoff=", "rru_mode=", "test_type=", "auto_gen="])
    except getopt.GetoptError:
        print("Err: There are some unexpected parameter!")

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-d', '--dl_mode'):
            str_dl_mode = arg
        elif opt in ('-b', '--bandwidth'):
            str_bandwidth = arg
        elif opt in ('-f', '--frequency'):
            str_frequency = arg
        elif opt in ('-p', '--power'):
            str_power = arg
        elif opt in ('-o', '--pusch_rb_offset'):
            str_pusch_rb_offset = arg
        elif opt in ('-u', '--ul_mode'):
            str_ul_mode = arg
        elif opt in ('-k', '--pdsch_power_backoff'):
            str_pdsch_power_backoff = arg
        elif opt in ('-m', '--rru_mode'):
            str_rru_mode = arg
        elif opt in ('-t', '--test_type'):
            str_test_type = arg
        elif opt in ('-g', '--auto_gen'):
            bool_auto_gen = True if arg == "True" or arg == "true" or arg == True else False
    l1_xml = change_testmode(dl_mode=str_dl_mode,
                             bandwidth=str_bandwidth,
                             frequency=str_frequency,
                             power=str_power,
                             pusch_rb_offset=str_pusch_rb_offset,
                             ul_mode=str_ul_mode,
                             pdsch_power_backoff=str_pdsch_power_backoff,
                             rru_mode=str_rru_mode,
                             test_type=str_test_type,
                             auto_gen=bool_auto_gen)
    # main(l1_xml)
    # time.sleep(10)
    def PSU_stress_test(PSU, PSU_Controller):
        for i in range(100):
            PSU.PowerSuppy_ON(PSU_Controller)
            time.sleep(0.5)
            PSU.PowerSuppy_OFF(PSU_Controller)
            time.sleep(0.5)
    CycleTimes = 1000
    PSUStress = False
    JesdFlag = True
    JesdRepeatTimes = 5
    made_ips = ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5']
    beamer_ip = '192.168.101.1'
    CpriFlag = False
    CpriRepeatTimes = 3
    UdpcpFlag = False
    SoapFlag = False
    DpdinFlag = False
    DpdinRepeatTimes = 1

    PSU = visaInstrument()
    PSU_Controller = PSU.PowerSuppy_Init('GPIB', '15')
    for i in range(CycleTimes):
        # power on
        if PSUStress:
            PSU_stress_test(PSU, PSU_Controller)
        PSU.PowerSuppy_ON(PSU_Controller)
        time.sleep(15)
        try:
            DutStatusHandler = DUT_Status(made_ips, beamer_ip, product_type=str_rru_mode)
            if DutStatusHandler.check_dut_status():
            # if True:
                if DpdinFlag or UdpcpFlag or SoapFlag:
                    main(l1_xml, L1Connection_file='L1Connection')
                elif JesdFlag or CpriFlag:
                    main(l1_xml, L1Connection_file='L1Connection_Jesd')
                time.sleep(40)
                # disable_auto_reboot(beamer_ip)
                if JesdFlag:
                    JesdVerifyHandler = JesdVerify(made_ips=made_ips, product_type=str_rru_mode)
                    JesdVerifyHandler.JesdTest(JesdRepeatTimes)
                if CpriFlag:
                    CpriSyncHandler = CpriSync()
                    CpriSyncHandler.Cpri_test(REPEAT=CpriRepeatTimes)
                    time.sleep(2)
                if DpdinFlag or UdpcpFlag or SoapFlag:
                    DpdinCheckHandler = DpdinStatus(made_ips, limit=2, repeat=3)
                    DpdinCheckHandler.DPDIN_test()
            else:
                # logging.error("DUT status not ready!!")
                raise DUTNotReadyError
        except Exception as e:
            logging.error(msg=e)
        PSU.PowerSuppy_OFF(PSU_Controller)
        time.sleep(2)













