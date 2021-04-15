import logging
import time
import subprocess
import sys, os

try:
    from auto_test.start_l1.connections.connection import _SSH_Shell, SSHClient_noauth
    from auto_test.start_l1.utils.Exceptions import *
except:
    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(current_path))))
    from auto_test.start_l1.connections.connection import _SSH_Shell, SSHClient_noauth
    from auto_test.start_l1.utils.Exceptions import *

logger = logging.getLogger('main')
# formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
# file_handler = logging.FileHandler(
#     filename="check_dut")
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
# logger.setLevel(logging.DEBUG)


def check_product_key(product_type, product_code_pairs=None):
    if product_code_pairs is None:
        product_code_pairs = {'AEQZ': "475444A",
                              'AENB': "475728A",
                              'AEQE': "474750A",
                              'AEQY': "475538A",
                              'AEQC': "475431A"}
    BEAMER_IP = "192.168.101.1"
    USER_NAME = "toor4nsn"
    PASSWORD = "oZPS0POrRieRtu"
    CHECK_PRODUCT_CODE_COMMAND = "cd /mnt/factory/configs/unit && cat module_product_code.txt"

    ssh = _SSH_Shell()
    ssh.open(BEAMER_IP, 22, username=USER_NAME, password=PASSWORD)
    stdout = ssh.command(CHECK_PRODUCT_CODE_COMMAND)
    product_code = stdout[0].strip().split('.')[0]
    logger.info("get product code => " + product_code)
    ssh.close()

    if not product_code == product_code_pairs[product_type]:
        logger.error("product code NOT match!")
        raise ProductKeyNotMatchException


def ping_duts(ips, time_out=30):
    """

    :param ips: list of strings. like ['192.168.101.1','192.168.101.2']
    :param time_out: int
    :return: None. raise error if not all ips are connected within timeout.
    """
    repeat = 0
    connected_count = 0
    while repeat < time_out:
        for ip in ips:
            with subprocess.Popen(['ping', ip],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT) as out:
                stdout, stderr = out.communicate()
                logger.info(f'ping {ip} with 32 bytes')
                logger.info('get output =>' + stdout.decode('utf-8').split('\n')[2])
                if b'bytes=32 time<1ms TTL=64' in stdout or b'bytes=32 time=1ms TTL=64' in stdout:
                    # print(f"dut {dut_ip} connected")
                    logger.info(f'dut {ip} connected')
                    connected_count += 1
                else:
                    # print(f"dut {dut_ip} not connectd")
                    logger.info(f"dut {ip} not connectd")
        if connected_count == len(ips):
            logger.info('all duts connected!')
            return
        repeat += 1
        connected_count = 0
    raise DUTNotReadyException


def check_testability(made_ips, time_out=30):

    PORT = 22
    USERNAME = "root"
    CHECK_TESTABILITY_COMMAND = "ps | grep lib"

    testability_count = 0
    repeat = 0
    while repeat < time_out:
        for ip in made_ips:
            time.sleep(3)
            ssh = _SSH_Shell()
            ssh.open(hostname=ip, port=PORT, username=USERNAME, password=None)
            stdout, stderr = ssh.command(CHECK_TESTABILITY_COMMAND)
            if "testability" in stdout:
                testability_count += 1
                logger.info(f'{ip} testability readiness status is True')
            else:
                logger.info(f'{ip} testability readiness status is False')
            ssh.close()
        if testability_count == len(made_ips):
            logger.info('Testability is ready!')
            return
        else:
            logger.info('Testability not ready!')
            testability_count = 0
        repeat += 1
    raise DUTNotReadyException


def check_uoam(time_out=30):
    BEAMER_IP = '192.168.101.1'
    PORT = 22
    USERNAME = "toor4nsn"
    PASSWORD = "oZPS0POrRieRtu"
    CHECK_UOAM_COMMAND = "ps | grep lib"

    repeat = 0
    ssh = _SSH_Shell()
    ssh.open(hostname=BEAMER_IP, port=PORT, username=USERNAME, password=PASSWORD)
    while repeat < time_out:
        time.sleep(3)
        stdout, stderr = ssh.command(CHECK_UOAM_COMMAND)
        # print(stdout)
        # for line in stdout.split('\n'):
        #     logging.info(line)
        if "uoamapp" in stdout:
            logger.info('uoam readiness status is true')
            ssh.close()
            return True
        else:
            logger.info('uoam readiness status is false')
            repeat += 1
    ssh.close()
    raise DUTNotReadyException


def check_dut_status(activate_carriers_setting):

    ping_duts(ips=activate_carriers_setting.get_mades())
    check_product_key(product_type=activate_carriers_setting.get_rru())
    check_testability(made_ips=activate_carriers_setting.get_mades())
    check_uoam()

if __name__ == "__main__":
    ping_duts(ips=['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5'])
    check_product_key(product_type="AEQC")
    check_testability(made_ips=['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5'])
    check_uoam()
