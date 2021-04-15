from __future__ import annotations

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger("main")


class L1Init:

    def __init__(self, L1_init_mode: L1InitMode):
        self.L1_init_mode = L1_init_mode

    def run(self, activate_carriers_setting):
        self.L1_init_mode.run(activate_carriers_setting)


class L1InitMode(ABC):

    @abstractmethod
    def run(self, activate_carriers_setting):
        pass


class L1InitModeActivateCarriers20B(L1InitMode):

    def run(self, activate_carriers_setting):
        web_handler = Web_handler()
        web_handler.activate_carriers(activate_carriers_setting)
        print("activate finish")
        # web_handler.check_cpri_ready_in_log()
        web_handler.verify_l1_finish()


class L1InitModeNoActivateCarriers20B(L1InitMode):

    def run(self, activate_carriers_setting):
        web_handler = Web_handler()
        web_handler.no_activate_carriers(activate_carriers_setting)
        # web_handler.check_cpri_ready_in_log()
        web_handler.verify_l1_finish()


class L1InitModeActivateCarriers20A(L1InitMode):

    def run(self, activate_carriers_setting):
        main(l1_xml, L1Connection_file='L1Connection', timeout=1200)


class L1InitModeNoActivateCarriers20A(L1InitMode):

    def run(self, activate_carriers_setting):
        main(l1_xml, L1Connection_file='L1Connection_jesd', timeout=1200)


def L1InitModeNone(L1InitMode):

    def run(self, activate_carriers_setting):
        pass


def select_L1_init_mode(product_settings):

    if product_settings.L1_mode() == "20A":
        if product_settings.power_flag():
            return L1InitModeActivateCarriers20A()
        elif product_settings.jesd_flag() or product_settings.cpri_flag():
            return L1InitModeNoActivateCarriers20A()
    elif product_settings.L1_mode == "20B":
        if product_settings.power_flag():
            return L1InitModeActivateCarriers20B()
        elif product_settings.jesd_flag() or product_settings.cpri_flag():
            return L1InitModeNoActivateCarriers20B()

    else:
        logger.error("not supported L1 init mode")
        return L1InitModeNone()