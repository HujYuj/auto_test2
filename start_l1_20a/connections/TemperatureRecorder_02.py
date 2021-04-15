"""
This script is used to reading and save 32 pipe or 64 pipe products temperature sensors values.
Set the PROJECT_NAME, PIPE_NUMBER and READ_INTERVAL.
Author: colin.yang@nokia-sbell.com
Rev: 0.2
Date: 2020/8/21
"""

import telnetlib
import time, datetime
import re
import threading
from csv import DictWriter
import csv
import os

PROJECT_NAME = 'AENB'  # Project name, the log file name will begin with project name.
PIPE_NUMBER = 32  # Pipe numbers, support 32 and 64 pipe Master, Amber projects, other projects not tested.
READ_INTERVAL = 30  # Read time internal, unit second.


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
                SENSOR_NAME_LIST.append(f'{pre}pa{i * 8 + m * 2 + 1}_{i * 8 + m * 2 + 2}')
        SENSOR_NAME_LIST.append('BM_core')
        SENSOR_NAME_LIST.append('BM_serdes')
    else:
        print("please provide the right PIPE NUMBER, it should be 32 or 64.")
        pass


def get_temperature(ip, path_name):
    tn = telnetlib.Telnet(ip, 2000)
    cmd = f'/ action create ThermometerDevice /ThermometerDevice/temp/{path_name} /temp/{path_name}'
    tn.write(cmd.encode('ascii') + b"\r\n")
    tn.read_until(b'\r\n', 2)
    cmd = f'/ThermometerDevice/temp/{path_name} get temperature'
    tn.write(cmd.encode('ascii') + b"\r\n")
    response = tn.read_until(b'\r\n', 2).decode('ascii')
    # print(response)
    temp = re.findall(r"-?\d+\.\d\d\d", response)[0]
    tn.write(b'/ action terminate\r\n')
    # time.sleep(0.2)
    tn.read_until(b'\r\n', 2)
    return temp


def get_made_temperature(made_id, sensors):
    print('reading MADE %s' % made_id)
    temperature_line = {}
    ip = f'192.168.100.{made_id + 1}'
    ic_type = 'MADE'
    for sensor in sensors:
        s = sensor.split('_', 1)[1]
        if s.startswith(('e', 'i')):
            path_name = f'made{made_id}/{s}'
        elif s.startswith(('pa', 'trx')):
            path_name = s
        temp = get_temperature(ip, path_name)
        temperature_line[f'M{made_id}_{s}'] = temp

    global temperature, lock
    lock.acquire()
    temperature = {**temperature, **temperature_line}
    lock.release()


def get_beamer_temperature(sensors):
    print('reading BEAMER')
    temperature_line = {}
    ip = f'192.168.100.1'
    for sensor in sensors:
        s = sensor.split('_')[1]
        device_name = 'bmFpga1/' + s
        temp = get_temperature(ip, device_name)
        temperature_line[f'BM_{s}'] = temp

    global temperature, lock
    lock.acquire()
    temperature = {**temperature, **temperature_line}
    lock.release()


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

    for made_id in range(MADE_NUM):
        thread = threading.Thread(target=get_made_temperature, args=(made_id + 1, sensors[made_id]))
        thread.start()
        thread_list.append(thread)
    thread = threading.Thread(target=get_beamer_temperature, args=(sensors[-1],))
    thread.start()
    thread_list.append(thread)
    for j in thread_list:
        j.join()
    append_dict_as_row(filename, temperature, ['time'] + SENSOR_NAME_LIST)


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


if __name__ == '__main__':
    print("........Begin........")
    SENSOR_NAME_LIST = []
    filename = initiate()
    lock = threading.Lock()
    N = 1
    start_time = time.time()
    while True:
        next_time = start_time + READ_INTERVAL * N
        N += 1
        read_one_cycle(filename)
        end = time.time()
        print(f'______One scanning done, wait next______')
        wait_time = next_time - end
        time.sleep(wait_time)
