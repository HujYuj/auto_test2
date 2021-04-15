import os
import sys
import logging
from time import sleep
from common.xml_helper import XMLHelper
from common.ssh_helper import SSHHelper

logger = logging.getLogger(__name__)


class RXRouteController:

    def __init__(self):
        self.one_antenna_route_commands = None
        # [
        #     '/sbin/devmem 0xf9040200 32 0',
        #     '/sbin/devmem 0xf9040204 32 6',
        #     '/sbin/devmem 0xa0002160 32 0x3F77FFF'
        # ]
        self.another_antenna_route_commands = None
        # [
        #     '/sbin/devmem 0xf9040200 32 5',
        #     '/sbin/devmem 0xf9040204 32 0',
        #     '/sbin/devmem 0xa0002160 32 0x4077FFF'
        # ]

    def get_rx_route_commands(self, antenna_id: int) -> list:
        xml_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resource', 'RouteCommandsFor5G.xml')
        xml_handler = XMLHelper()
        xml_handler.load_xml_document(xml_path)
        current_nodes = xml_handler.get_nodes(
            f'//MasterRoutes/TRX[@id={antenna_id - 1}]/Beamforming[@isOn="true"]/RouteCommand')
        commands = []
        for item in current_nodes:
            commands.append(xml_handler.get_node_text(item))
        xml_handler.release()

        return commands

    def send_route_commands(self, antenna_id: int):
        ssh = SSHHelper(host='192.168.101.1', username='toor4nsn', password='oZPS0POrRieRtu')
        ssh.create_ssh()
        self.one_antenna_route_commands = self.get_rx_route_commands(antenna_id)
        for command in self.one_antenna_route_commands:
            ssh.send(command)
        ssh.release()

    def switch_route_commands(self, another_antenna_id: int, current_antenna_id: int):
        # Switch from other antenna to current antenna measured
        self.another_antenna_route_commands = self.get_rx_route_commands(another_antenna_id)
        self.one_antenna_route_commands = self.get_rx_route_commands(current_antenna_id)
        ssh = SSHHelper(host='192.168.101.1', username='toor4nsn', password='oZPS0POrRieRtu')
        ssh.create_ssh()
        for command in self.another_antenna_route_commands:
            ssh.send(command)
        sleep(5)
        logger.info('Switch RX route from other antenna to current antenna measured to sleep 5s')
        for command in self.one_antenna_route_commands:
            ssh.send(command)
        sleep(1)
        ssh.release()


if __name__ == '__main__':
    route_controller = RXRouteController()
    current_commands = route_controller.get_rx_route_commands(16)
    print(current_commands)
