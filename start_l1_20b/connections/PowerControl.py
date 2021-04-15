from __future__ import annotations
from abc import ABC, abstractmethod
import pyvisa


class PowerControl:

    def __init__(self, control_mode: ControlMode) -> None:
        self._control_mode = control_mode

    @property
    def control_mode(self):
        return self._control_mode

    @control_mode.setter
    def control_mode(self, control_mode: ControlMode):
        self._control_mode = control_mode

    def init_power(self, address: str):
        self._control_mode.power_init(address)

    def power_on(self):
        self._control_mode.power_on()

    def power_off(self):
        self._control_mode.power_off()


class ControlMode(ABC):

    def __init__(self):
        self.visaDLL = 'c:/windows/system32/visa64.dll'
        self.resourceManager = pyvisa.ResourceManager(self.visaDLL)

    @abstractmethod
    def power_init(self, address: str):
        pass

    @abstractmethod
    def power_on(self):
        pass

    @abstractmethod
    def power_off(self):
        pass


class GPIBControlMode(ControlMode):

    def power_init(self, address: str):
        self.PS_handler = self.resourceManager.open_resource("GPIB1::%s::INSTR" % (address))

    def power_on(self):
        self.PS_handler.write("OUTPUT:STAT ON")

    def power_off(self):
        self.PS_handler.write("OUTPUT:STAT OFF")


class TCPIPVisaControlMode(ControlMode):

    def power_init(self, address: str):
        self.PS_handler = self.resourceManager.open_bare_resource("TCPIP0::%s::INSTR"%(address))

    def power_on(self):
        self.PS_handler.write("OUTPUT:STAT ON")

    def power_off(self):
        self.PS_handler.write("OUTPUT:STAT OFF")


class TCPIPVisaRawSocketControlMode(ControlMode):

    def power_init(self, address: str):
        self.PS_handler = self.resourceManager.open_bare_resource("TCPIP0::%s::8462::SOCKET"%address)

    def power_on(self):
        self.PS_handler.write("OUTPUT 1\n")

    def power_off(self):
        self.PS_handler.write("OUTPUT 1\n")


if __name__ == "__main__":

    power_control = PowerControl(GPIBControlMode())
    power_control.init_power(address="11")
    power_control.power_off()
