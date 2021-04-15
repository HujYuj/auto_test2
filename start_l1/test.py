EDGE_DRIVER_PATH = "C:\\edgedriver_win64\\msedgedriver.exe"

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time, os, logging, sys
from selenium.webdriver.common.keys import Keys

driver = webdriver.Edge(executable_path=EDGE_DRIVER_PATH)
driver.maximize_window()
driver.get("http://localhost:8032/")
driver.refresh()

driver.find_element_by_id("ui-id-1").click()
driver.find_element_by_id("checkEnvBtn").click()
time.sleep(10)
driver.find_element_by_id("runner").click()
time.sleep(1)
abil = driver.find_element_by_id("abil_slot-button")
abil.send_keys(1, Keys.ENTER)
time.sleep(1)
# el = driver.find_element_by_id("rru-menu")
# for option in el.find_elements_by_tag_name("option"):
#     if option.text == "AEQE":
#         option.select()
#         break
element = driver.find_element_by_id("rru-button")
element.click()
for i in range(0, 14):
    element.send_keys(Keys.UP)
    time.sleep(0.1)
for i in range(0,1):
    element.send_keys(Keys.DOWN)
    time.sleep(0.1)
element.send_keys(Keys.RETURN)
time.sleep(5)
driver.close()