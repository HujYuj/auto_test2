import os
import json
import logging
import datetime, time
import csv
from csv import DictWriter
import threading
current_path = os.path.dirname(os.path.realpath(__file__))
try:
    from tools_dev.connections.miniftp import SCP
    from tools_dev.connections.connection import _SSH_Shell
    from tools_dev.testings.Exceptions import *
    from tools_dev.testings.settings import download_runtime_log
except:
    from ..connections.miniftp import SCP
    from ..connections.connection import _SSH_Shell
    from .Exceptions import *
    from .settings import download_runtime_log


class JesdReader:

    def __init__(self, product_type, made_ips):
        self.product_type = product_type
        self.made_ips = made_ips
        self.fail_flag = False
        self.logger = logging.getLogger("main")

    def load_commands(self):
        """def self.commands"""
        self.commands = []

        if self.product_type == "AEQZ":
            command_file = "JESDCommands_AEQZ.txt"
        elif self.product_type == "AEQV" or self.product_type == "AENB" or self.product_type == "AEQY":
            command_file = "JESDCommands_AEQV.txt"
        else:
            self.logger.error("No matching JESD commands found!")
        with open(os.path.join(current_path, 'JesdTestItems', command_file), 'r') as f:
            lines = f.readlines()
        for line in lines:
            if not line.startswith('#') and line.strip() != "":
                self.commands.append(line.strip())

    def check_commands_valid(self):
        valid_commands = []
        for command in self.commands:
            if command in self.check_items.keys():
                valid_commands.append(command)
            else:
                self.logger.info(f"Invalid command: {command}")
        self.commands = valid_commands

    def load_verification(self):
        """def self.check_items : dict"""
        if self.product_type == "AEQZ":
            json_file = "AEQZ_JESD_CHECK.json"
        elif self.product_type == "AEQV" or self.product_type == "AENB" or self.product_type == "AEQY":
            json_file = "AEQV_JESD_CHECK.json"
        elif self.product_type == "AEQE":
            json_file = "AEQE_JESD_CHECK.json"
        else:
            self.logger.error("no matching JESD commands found!")

        with open(os.path.join(current_path, "JESDTestItems", json_file), "r") as f:
            self.check_items = json.load(f)

    def upload_tool(self, ip):
        scp = SCP(ip, 22)
        scp.connect_noPassword()
        local = os.path.join(current_path, 'JesdTestItems/spiafe')
        remote = '/var/tmp/spiafe'
        scp.upload(local, remote)
        scp.close()

    def read_one_cycle(self, reg_values):
        threads = []
        for ip in self.made_ips:
            reg_values[ip] = {}
            t = threading.Thread(target=self.get_reg_values, args=(reg_values[ip], ip))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self.append_dict_as_rows(reg_values)

    def get_reg_values(self, reg_values_single, ip):
        self.upload_tool(ip=ip)
        scp = SCP(ip, 22)
        scp.connect_noPassword()

        for command in self.commands:
            # command = command.strip()
            stdin, stdout, stderr = scp.write(command)
            out = stdout.readline().strip()
            # print("out:"+out)
            logging.debug("get respond => %s" % out)
            if not self.check_items[command]:
                pass
            elif self.check_items[command] == "LAST2BIT":
                logging.debug('get binary value => %s' % bin(int(out, 16)))
                reg_values_single[command] = bin(int(out, 16))
                if repr(bin(int(out, 16)))[-3:-1] == '11':
                    logging.debug('Verification result => correct')
                else:
                    logging.debug('Verification result => wrong')
                    self.fail_flag = True
            elif self.check_items[command] == "CHECKLINK":
                reg_values_single[command] = out
                if out in ['0x00002860', '0x00000060', '0x00008060']:
                    logging.debug('Verification result => correct')
                else:
                    logging.debug('Verification result => wrong')
                    self.fail_flag = True
            else:
                reg_values_single[command] = out.split()[-1]
                if out.split()[-1] == self.check_items[command]:
                    logging.debug('Verification result => correct')
                else:
                    logging.debug('Verification result => wrong')
                    self.fail_flag = True

    def append_dict_as_rows(self, reg_values):
        with open(self.filename, 'a+', newline='') as write_obj:
            dict_writer = DictWriter(write_obj, fieldnames=self.commands)
            for ip in self.made_ips:
                dict_writer.writerow(reg_values[ip])

    def filename_initiate(self, file_path):
        if file_path is None:
            file_path = os.path.join(current_path, "MainTestResults")

        time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')  # _%H%M%S')
        self.filename = os.path.join(file_path, self.product_type + '_power_' + time + '.csv')
        if not os.path.isfile(self.filename):
            with open(self.filename, 'a', newline='') as f:
                wr = csv.writer(f, quoting=csv.QUOTE_ALL)
                wr.writerow(['Time'] + self.commands)
        print("Testing result will saved to file %s" % self.filename)

    def continue_read_jesd(self):
        pass

    def read_jesd(self, repeat=3, file_path=None):
        self.load_commands()
        self.load_verification()
        self.check_commands_valid()
        self.filename_initiate(file_path=file_path)
        for i in range(repeat):
            reg_values = {}
            self.read_one_cycle(reg_values)

        pass_flag = not self.fail_flag
        return pass_flag


if __name__ == "__main__":
    made_ips = ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5']
    jesdReader = JesdReader(product_type="AEQY", made_ips=made_ips)
    jesdReader.read_jesd(repeat=3)