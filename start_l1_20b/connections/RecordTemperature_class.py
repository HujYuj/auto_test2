"""
This script is used to reading and save 32 pipe or 64 pipe products temperature sensors values.
Set the PROJECT_NAME, PIPE_NUMBER and READ_INTERVAL.
Author: colin.yang@nokia-sbell.com
Rev: 0.1
Date: 2020/7/30
"""

import paramiko
import time, datetime
import re
import threading
from csv import DictWriter
import csv
import os
from threading import Thread

PROJECT_NAME = 'TEST'  # Project name, the log file name will begin with project name.
PIPE_NUMBER = 32  # Pipe numbers, support 32 and 64 pipe Master, Amber projects, other projects not tested.
READ_INTERVAL = 5  # Read time internal, unit second.

SENSOR_NAME_LIST = []
lock = threading.Lock()


def get_sensor_name_list(pips):
    global MADE_NUM, SENSOR_NAME_LIST, PIPE_SENSOR_NUM
    if pips == 32:
        MADE_NUM = 4
        PIPE_SENSOR_NUM = 18
        for i in range(4):
            pre = f'M{i + 1}_'
            SENSOR_NAME_LIST.append(pre + 'external')
            for k in range(7):
                SENSOR_NAME_LIST.append(pre + 'internal' + str(k + 1))
            SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 1}_{i * 8 + 4}')
            SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 5}_{i * 8 + 8}')
            for m in range(8):
                SENSOR_NAME_LIST.append(f'{pre}pa{i * 8 + m + 1}')
        SENSOR_NAME_LIST.append('BM_core')
        SENSOR_NAME_LIST.append('BM_serdes')
    elif pips == 64:
        MADE_NUM = 8
        PIPE_SENSOR_NUM = 14
        for i in range(8):
            pre = f'M{i + 1}_'
            SENSOR_NAME_LIST.append(pre + 'external')
            for k in range(7):
                SENSOR_NAME_LIST.append(pre + 'internal' + str(k + 1))
            SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 1}_{i * 8 + 4}')
            SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 5}_{i * 8 + 8}')
            for m in range(4):
                SENSOR_NAME_LIST.append(f'{pre}pa{i * 4 + m * 2 + 1}_{i * 4 + m * 2 + 2}')
        SENSOR_NAME_LIST.append('BM_core')
        SENSOR_NAME_LIST.append('BM_serdes')
    else:
        print("please provide the right PIPE NUMBER, it should be 32 or 64.")
        pass


def get_device_info(rc, device_name, ic_type):
    if ic_type == 'BEAMER':
        dt = 1
    else:
        dt = 0.2
    try:
        rc.recv(20000)
        rc.send(f'/ action create ThermometerDevice /ThermometerDevice/temp/{device_name} /temp/{device_name}\n')
        time.sleep(dt)
        # if ic_type == 'BEAMER':
        #     rc.send(f'/ThermometerDevice/temp/{device_name} get device_path')
        #     time.sleep(dt)
        rc.send(f'/ThermometerDevice/temp/{device_name} get temperature\n')
        time.sleep(dt)
        output = rc.recv(65535).decode('utf-8')
        temp = re.findall(r"-?\d+\.\d\d\d", output)[0]
        rc.send('/ action terminate\n')
        time.sleep(dt)
    except:
        print("not able to get %s" % device_name)
        rc.send('/ action terminate\n')
        time.sleep(dt)
        temp = ''
    return temp


def ssh2a(ip):
    transport = paramiko.Transport(ip)
    transport.connect(username='root', password=None)
    transport.auth_none('root')

    client = paramiko.SSHClient()
    client._transport = transport
    shell = client.invoke_shell()
    rc = shell
    return client, rc


def get_made_temperature(made_id, sensors):
    print('reading MADE %s' % made_id)
    temperature_line = {}
    ip = f'192.168.100.{made_id + 1}'
    client, shell = ssh2a(ip)
    shell.send('telnet 127.0.0.1 2000\n')
    ic_type = 'MADE'
    for sensor in sensors:
        s = sensor.split('_', 1)[1]
        if s.startswith(('e', 'i')):
            device_name = f'made{made_id}/{s}'
        elif s.startswith(('pa', 'trx')):
            device_name = s
        elif s.startswith(('core', 'serdes')):
            device_name = f'bmFpga1/{s}'
        temp = get_device_info(shell, device_name, ic_type)
        temperature_line[f'M{made_id}_{s}'] = temp
    client.close()
    global temperature, lock
    lock.acquire()
    temperature = {**temperature, **temperature_line}
    lock.release()
    # return temperature_line


def get_beamer_temperature(sensors):
    print('reading BEAMER')
    temperature_line = {}
    ip = f'192.168.100.1'
    client, shell = ssh2a(ip)
    shell.send('telnet 127.0.0.1 2000\n')
    ic_type = "BEAMER"
    for sensor in sensors:
        s = sensor.split('_')[1]
        device_name = 'bmFpga1/' + s
        temp = get_device_info(shell, device_name, ic_type)
        temperature_line[f'BM_{s}'] = temp
    client.close()
    global temperature, lock
    lock.acquire()
    temperature = {**temperature, **temperature_line}
    lock.release()
    # return temperature_line


def append_dict_as_row(file_name, dict_of_elem, field_names):
    with open(file_name, 'a+', newline='') as write_obj:
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        dict_writer.writerow(dict_of_elem)


def read_one_cycle(filename):
    print('------Scanning start-------')
    global temperature
    now = datetime.datetime.now()
    temperature = {'time': now}
    sensors = [SENSOR_NAME_LIST[i:i + PIPE_SENSOR_NUM] for i in range(0, len(SENSOR_NAME_LIST), PIPE_SENSOR_NUM)]
    thread_list = []
    start = time.time()
    for made_id in range(MADE_NUM):
        # made_temperature = get_made_temperature(made_id + 1, sensors[made_id])
        # temperature = {**temperature, **made_temperature}
        thread = threading.Thread(target=get_made_temperature, args=(made_id + 1, sensors[made_id]))
        thread.start()
        thread_list.append(thread)
    # beamer_temperature = get_beamer_temperature(sensors[-1])
    thread = threading.Thread(target=get_beamer_temperature, args=(sensors[-1],))
    thread.start()
    thread_list.append(thread)
    for j in thread_list:
        j.join()
    end = time.time()
    # 打印该程序运行了几秒
    print(f'One cycle read time {end - start + READ_INTERVAL}')
    # temperature = {**temperature, **beamer_temperature}
    # print(temperature)
    append_dict_as_row(filename, temperature, ['time'] + SENSOR_NAME_LIST)
    # threads = threading.Thread(target=get_made_temperature, args=(made_id + 1, sensors[made_id]))
    # threads.start()


def initiate():
    time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')  # _%H%M%S')
    get_sensor_name_list(PIPE_NUMBER)
    filename = PROJECT_NAME + '_' + time + '.csv'
    if not os.path.isfile(filename):
        with open(filename, 'a', newline='') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(['Time'] + SENSOR_NAME_LIST)
    print("Testing result will saved to file %s" % filename)
    return filename


class RecordTemperature(object):

    def __init__(self, PIPE_NUMBER, PROJECT_NAME, SENSOR_NAME_LIST):
        self._run = True
        self.PIPE_NUMBER = PIPE_NUMBER
        self.PROJECT_NAME = PROJECT_NAME
        self.SENSOR_NAME_LIST = SENSOR_NAME_LIST
        self.READ_INTERVAL = 18
        self.lock = threading.Lock()
        self.temperature_line = {}

    def get_sensor_name_list(self, pips):
        if pips == 32:
            MADE_NUM = 4
            PIPE_SENSOR_NUM = 18
            for i in range(4):
                pre = f'M{i + 1}_'
                self.SENSOR_NAME_LIST.append(pre + 'external')
                for k in range(7):
                    self.SENSOR_NAME_LIST.append(pre + 'internal' + str(k + 1))
                self.SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 1}_{i * 8 + 4}')
                self.SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 5}_{i * 8 + 8}')
                for m in range(8):
                    self.SENSOR_NAME_LIST.append(f'{pre}pa{i * 8 + m + 1}')
            self.SENSOR_NAME_LIST.append('BM_core')
            self.SENSOR_NAME_LIST.append('BM_serdes')
        elif pips == 64:
            MADE_NUM = 8
            PIPE_SENSOR_NUM = 14
            for i in range(8):
                pre = f'M{i + 1}_'
                self.SENSOR_NAME_LIST.append(pre + 'external')
                for k in range(7):
                    self.SENSOR_NAME_LIST.append(pre + 'internal' + str(k + 1))
                self.SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 1}_{i * 8 + 4}')
                self.SENSOR_NAME_LIST.append(f'{pre}trx{i * 8 + 5}_{i * 8 + 8}')
                for m in range(4):
                    self.SENSOR_NAME_LIST.append(f'{pre}pa{i * 4 + m * 2 + 1}_{i * 4 + m * 2 + 2}')
            self.SENSOR_NAME_LIST.append('BM_core')
            self.SENSOR_NAME_LIST.append('BM_serdes')
        else:
            print("please provide the right PIPE NUMBER, it should be 32 or 64.")
            pass

    def initiate(self):
        time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')  # _%H%M%S')
        self.get_sensor_name_list(self.PIPE_NUMBER)
        filename = self.PROJECT_NAME + '_' + time + '.csv'
        if not os.path.isfile(filename):
            with open(filename, 'a', newline='') as f:
                wr = csv.writer(f, quoting=csv.QUOTE_ALL)
                wr.writerow(['Time'] + self.SENSOR_NAME_LIST)
        print("Testing result will saved to file %s" % filename)
        return filename

    def append_dict_as_row(self, file_name, dict_of_elem, field_names):
        with open(file_name, 'a+', newline='') as write_obj:
            dict_writer = DictWriter(write_obj, fieldnames=field_names)
            dict_writer.writerow(dict_of_elem)

    def read_one_cycle(self, filename):
        print('------Scanning start-------')
        now = datetime.datetime.now()
        self.temperature = {'time': now}
        sensors = [self.SENSOR_NAME_LIST[i:i + self.PIPE_SENSOR_NUM] for i in range(0, len(self.SENSOR_NAME_LIST), self.PIPE_SENSOR_NUM)]
        thread_list = []
        start = time.time()
        for made_id in range(self.MADE_NUM):
            # made_temperature = get_made_temperature(made_id + 1, sensors[made_id])
            # temperature = {**temperature, **made_temperature}
            thread = threading.Thread(target=self.get_made_temperature, args=(made_id + 1, sensors[made_id]))
            thread.start()
            thread_list.append(thread)
        # beamer_temperature = get_beamer_temperature(sensors[-1])
        thread = threading.Thread(target=self.get_beamer_temperature, args=(sensors[-1],))
        thread.start()
        thread_list.append(thread)
        for j in thread_list:
            j.join()
        end = time.time()
        # 打印该程序运行了几秒
        print(f'One cycle read time {end - start + READ_INTERVAL}')
        # temperature = {**temperature, **beamer_temperature}
        # print(temperature)
        self.append_dict_as_row(filename, self.temperature, ['time'] + SENSOR_NAME_LIST)
        # threads = threading.Thread(target=get_made_temperature, args=(made_id + 1, sensors[made_id]))
        # threads.start()

    def run(self):
        filename = self.initiate()
        while self._run:
            self.read_one_cycle(filename)
            print("\nScanning done, wait %s seconds" % READ_INTERVAL, end='')
            for x in range(READ_INTERVAL):
                print('.', end='')
                time.sleep(1)
            print('\n\n')

    def terminate(self):
        self._run = False


if __name__ == '__main__':
    print("........Begin........")
    # SENSOR_NAME_LIST = []
    # filename = initiate()
    # lock = threading.Lock()
    # while True:
    #     read_one_cycle(filename)
    #     print("\nScanning done, wait %s seconds" % READ_INTERVAL, end='')
    #     for x in range(READ_INTERVAL):
    #         print('.', end='')
    #         time.sleep(1)
    #     print('\n\n')

    for i in range(3):
        print(f"cycle {i}")
        record_temp = RecordTemperature()
        t_record_temp = Thread(target=record_temp.run, args=(32, 18, "TEST"))
        t_record_temp.start()
        time.sleep(100)
        print("time to terminate !!!")
        record_temp.terminate()
        t_record_temp.join()
