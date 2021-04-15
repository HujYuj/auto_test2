from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time, os, logging, sys
from selenium.webdriver.common.keys import Keys
try:
    from tools_dev.testings.Exceptions import *
except:
    root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # print('root_path: ' + root_path) # root_path = tools_dev
    sys.path.insert(0, os.path.join(root_path, ".."))
    # print('sys_path: ', sys.path) # add dut_control to system path
    from tools_dev.testings.Exceptions import *

EDGE_DRIVER_PATH = "C:\\edgedriver_win64\\msedgedriver.exe"


class Web_handler():
    def __init__(self):
        self.logger = logging.getLogger("main")
        self.driver = webdriver.Edge(executable_path=EDGE_DRIVER_PATH)

    def no_activate_carriers(self, activate_carriers_setting):
        pass

    def activate_carriers(self, activate_carriers_setting):
        try:
            self.logger.info("execute automate process to init L1 web page")

            self.driver.maximize_window()
            self.driver.get("http://localhost:8032/")
            self.driver.refresh()

            self.driver.find_element_by_id("ui-id-1").click()
            self.driver.find_element_by_id("checkEnvBtn").click()
            time.sleep(10)
            self.driver.find_element_by_id("runner").click()
            time.sleep(1)
            self.driver.find_element_by_id("abil_slot-button").send_keys(activate_carriers_setting.get_abil_slot_number(), Keys.ENTER)
            time.sleep(1)
            element = self.driver.find_element_by_id("rru-button")
            element.click()
            # for i in range(0, 8):
            #     element.send_keys(Keys.DOWN)
            # element.send_keys(Keys.RETURN)
            # time.sleep(3)
            self.driver.find_element_by_xpath("//*[@id='tdd_switch-button']").send_keys(activate_carriers_setting.get_tdd_switch(), Keys.ENTER)
            self.driver.find_element_by_id("case_type-button").send_keys(activate_carriers_setting.get_case_type(), Keys.ENTER)
            self.driver.find_element_by_id("dl_tm-button").send_keys(activate_carriers_setting.get_dl_tm(), Keys.ENTER)
            self.driver.find_element_by_xpath("//*[@id='c1_bw-button']").send_keys(activate_carriers_setting.get_bandwidth(), Keys.ENTER)

            freq_entry = self.driver.find_element_by_id("c1_freq")
            freq_entry.clear()
            freq_entry.send_keys(activate_carriers_setting.get_frequency(), Keys.ENTER)

            power_entry = self.driver.find_element_by_id("c1_power")
            power_entry.clear()
            power_entry.send_keys(activate_carriers_setting.get_power(), Keys.ENTER)

            # self.driver.find_element_by_id("l1_lib_log_capture").click()
            self.driver.find_element_by_xpath("// *[ @ id = 'executingForm'] / div[2] / table / tbody / tr / td[4] / label / span[1]").click()
            self.driver.find_element_by_id("runBtn").click()
            time.sleep(10)
            start_return_msg = self.driver.find_element_by_id("dialog").text
            print(start_return_msg)
        except Exception as e:
            self.driver.close()
            self.logger.error(msg=e)
            raise L1InitFailException

    def verify_l1_finish(self, time_out=600):
        timer = 0
        while timer < time_out:
            result_return_msg = self.driver.find_element_by_id("dialog").text
            if result_return_msg == "Done with return code 0":
                self.logger.info("L1 init finished...done with return code 0")
                # print("done with return code 0")
                self.driver.close()
                return
            time.sleep(1)
            timer += 1

        self.driver.close()
        raise L1TimeOutException

    def check_cpri_ready_in_log(self):
        timer = 0
        while timer < 600:
            log_content = self.driver.find_element_by_id("logContent").text
            if "0x00000010" in log_content:
                self.logger.info("Cpri link sync successfully!")
                return True
            time.sleep(1)
            timer += 1
            # print(timer)
        self.logger.info("Cannot found 0x00000010")
        return False


def verify_L1_results():
    current_path = os.path.dirname(os.path.realpath(__file__))
    print(current_path)
    out_put_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_path))),"nokia_5G_hwiv_configuration\\Output")
    print(out_put_dir)
    import glob

    list_of_files = glob.glob(os.path.join(out_put_dir, "autogen*[0-9].log"))
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    with open(latest_file, 'rb') as f:
        last_line = f.readlines()[-1]
    if b"passed" not in last_line:
        raise L1InitFailException




if __name__ == "__main__":
    # print(verify_L1_results())
    from tools_dev.testings.activate_carriers_setting import ActivateCarriersSetting

    activate_carriers_setting = ActivateCarriersSetting(ABIL_SLOT_NUMBER="3",
                                                        RRU="AEQB",
                                                        TDD_SWITCH="1116_3ms_a5",
                                                        CASE_TYPE="Single Carrier",
                                                        DL_TM="TM1_1",
                                                        BANDWIDTH="90",
                                                        FREQUENCY="3445",
                                                        POWER="34.49")
    web_handler = Web_handler()
    web_handler.activate_carriers(activate_carriers_setting)
    print("activate finish")
    # web_handler.check_cpri_ready_in_log()
    web_handler.verify_l1_finish()