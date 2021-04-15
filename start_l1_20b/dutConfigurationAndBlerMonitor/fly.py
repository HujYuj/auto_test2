"""
Description: Check BLER status for Master or Amber program

Author: Wei Yan, test solution squad

Comment: Please configure your **signal generator** in advance before starting

"""


import os
import sys
import time
import logging
import random
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter, StreamHandler
from library_controller import LibraryCaller
from rx_route_controller import RXRouteController


class Main:

    @staticmethod
    def init_logger():
        date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        log_file = date + '_BLER_monitor.log'
        exe_parent_path = os.path.split(sys.argv[0])[0]
        print(exe_parent_path)
        file_directory = os.path.join(exe_parent_path, 'log')
        # os.path.dirname(file_path)
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)
        file_path = os.path.join(file_directory, log_file)
        handler = RotatingFileHandler(file_path, maxBytes=50 * 1024 * 1024,
                                      backupCount=20)
        fmt = '%(asctime)s-%(pathname)s::%(funcName)s line%(lineno)d[%(levelname)s]=>%(message)s'
        # fmt = '{asctime}-{pathname}::{funcName} line{lineno}[{levelname}]=>{message}'
        formatter = logging.Formatter(fmt)  # style='{'
        handler.setFormatter(formatter)
        color_fmt = '{log_color}{asctime}-{pathname}::{funcName} ' + \
                    'line{lineno}[{levelname}]=>{message_log_color}{message}'
        color_formatter = ColoredFormatter(
            color_fmt,
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white'
            },
            secondary_log_colors={
                'message': {
                    'DEBUG': 'white',
                    'INFO': 'white',
                    'WARNING': 'white',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'}},
            style='{'
        )
        console = StreamHandler()
        console.setFormatter(color_formatter)
        # logger.addHandler(handler)
        logging.getLogger(__name__)
        # logging.basicConfig(
        #     # filename=None,
        #     # filemode=None,
        #     # format=None,
        #     # datefmt=None,
        #     # style=None,
        #     level=logging.DEBUG,
        #     # stream=None,
        #     handlers=[handler, console]
        # )
        logging.basicConfig(level=logging.DEBUG, handlers=[handler, console])
        logging.debug('Only debug')

    @staticmethod
    def run():
        LibraryCaller.activate_carriers()
        LibraryCaller.check_dut_status_ready()
        # Switch from other antenna to current antenna measured
        random_antenna = random.randint(2, 64)  # random antenna between 2 and 64, including the both
        RXRouteController().switch_route_commands(another_antenna_id=random_antenna, current_antenna_id=1)
        i = 3600000000
        while i > 0:
            LibraryCaller.get_bler()
            i -= 1
            time.sleep(1)

        # scheme two
        # while i > 0:
        #     random_antenna = random.randint(2, 64)  # random antenna between 2 and 64, including the both
        #     RXRouteController().switch_route_commands(another_antenna_id=random_antenna, current_antenna_id=1)
        #     j = 50  # get BLER 50 times
        #     while j > 0:
        #         LibraryCaller.get_bler()
        #         j -= 1
        #     i -= 1
        #     time.sleep(1)


if __name__ == "__main__":
    Main.init_logger()
    Main.run()
