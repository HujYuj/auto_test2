import os, sys
import threading
import datetime, time
import csv
from csv import DictWriter
import logging

current_path = os.path.dirname(os.path.realpath(__file__))
try:
    from auto_test.start_l1.connections.connection import _SSH_Shell
    from auto_test.start_l1.utils.settings import download_runtime_log
except:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(current_path))))
    from auto_test.start_l1.connections.connection import _SSH_Shell
    from auto_test.start_l1.utils.settings import download_runtime_log


class PowerReader:

    def __init__(self, made_ips, product_type):
        self.made_ips = made_ips
        self.product_type = product_type
        self.lock = threading.Lock()
        self.logger = logging.getLogger("main")
        self.fail_flag = False

    def file_name_initiate(self, file_path):
        if file_path is None:
            file_path = os.path.join(os.path.dirname(current_path), "testings/MainTestResults")

        time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')  # _%H%M%S')
        self.get_pipe_names()
        self.filename = os.path.join(file_path, self.product_type + '_power_' + time + '.csv')
        if not os.path.isfile(self.filename):
            with open(self.filename, 'a', newline='') as f:
                wr = csv.writer(f, quoting=csv.QUOTE_ALL)
                wr.writerow(['Time'] + self.pipe_names_list)
        print("Testing result will saved to file %s" % self.filename)

    def get_pipe_names(self):
        """initiate pipe names"""
        self.pipe_names_list = []
        self.pipe_names_list.append("MADE")
        self.pipe_names_list.append("time")
        for pipe_num in range(8):
            self.pipe_names_list.append("DPDIN_" + str(pipe_num))
            self.pipe_names_list.append("DPDOUT_" + str(pipe_num))
            self.pipe_names_list.append("FB_" + str(pipe_num))

    def get_made_power(self, power, made_ip):
        """power = {**power, **power_line}"""
        power_line = {}
        now = datetime.datetime.now()
        power_line['time'] = now
        power_line['MADE'] = made_ip

        port = 22
        username = "root"
        command = "dapd -sq"
        ssh = _SSH_Shell()
        ssh.open(hostname=made_ip, port=port, username=username, password=None)
        stdout, stderr = ssh.command(command)
        self.logger.info(f"send command to {made_ip}=> {command}")
        for line in stdout.split('\n'):
            self.logger.info(line)
            if line.strip().startswith('DPD IN:'):
                dpdin_values = [float(value) for value in line.split() if value != 'DPD' and value != 'IN:'
                                and '(' not in value and ')' not in value]
            if line.strip().startswith('DPD OUT:'):
                dpdout_values = [float(value) for value in line.split() if value != 'DPD' and value != 'OUT:'
                                 and '(' not in value and ')' not in value]
            if line.strip().startswith('FB:'):
                fb_values = [float(value) for value in line.split() if value != 'FB:'
                             and '(' not in value and ')' not in value]
        for pipe_num in range(len(dpdin_values)):
            power_line['DPDIN_' + str(pipe_num)] = dpdin_values[pipe_num]
            if not (-11.3 - self.limit['dpdin'] <= dpdin_values[pipe_num] <= -11.3 + self.limit['dpdin']):
                self.logger.error("dpdin value out of limit")
                self.fail_flag = True
        for pipe_num in range(len(dpdout_values)):
            power_line['DPDOUT_' + str[pipe_num]] = dpdout_values[pipe_num]
            if not (-11.3 - self.limit['dpdout'] <= dpdout_values[pipe_num] <= -11.3 + self.limit['dpdout']):
                self.logger.error("dpdout value out of limit")
                self.fail_flag = True
        for pipe_num in range(len(fb_values)):
            power_line['FB_' + str[pipe_num]] = fb_values[pipe_num]
            if not (-11.3 - self.limit['fb'] <= dpdout_values[pipe_num] <= -11.3 + self.limit['fb']):
                self.logger.error("fbt value out of limit")
                self.fail_flag = True

        self.lock.aquire()
        power = {**power, **power_line}
        self.lock.release()

    def read_one_cycle(self, power):
        threads = []
        for ip in self.made_ips:
            power[ip] = {}
            t = threading.Thread(target=self.get_made_power, args=(power[ip], ip))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self.append_dict_as_rows(power)

    def append_dict_as_rows(self, power):
        with open(self.filename, 'a+', newline='') as write_obj:
            dict_writer = DictWriter(write_obj, fieldnames=self.pipe_names_list)
            for ip in self.made_ips:
                dict_writer.writerow(power[ip])

    def read_power(self, repeat=3, file_path=None, limit=None):
        self.file_name_initiate(file_path=file_path)
        if limit is None:
            self.limit = {'dpdin': 0.5, 'fb': 0.5, 'dpdout': 0.5}

        for i in range(repeat):
            power = {}
            self.read_one_cycle(power)

        pass_flag = not self.fail_flag
        return pass_flag

    def continue_read_power(self, file_path=None, interval=30):
        self.file_name_initiate(file_path=file_path)
        print("........Begin........")
        N = 1
        start_time = time.time()
        while True:
            power = {}
            next_time = start_time + interval * N
            N += 1
            self.read_one_cycle(power)
            end = time.time()
            print(f'______One scanning done, wait next______')
            wait_time = next_time - end
            time.sleep(wait_time)


if __name__ == "__main__":
    made_ips = ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5']
    powerReader = PowerReader(made_ips=made_ips, product_type="AEQY")
    powerReader.continue_read_power()
