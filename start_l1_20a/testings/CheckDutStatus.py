import logging, subprocess
import time
from tools_dev.connections.connection import _SSH_Shell, SSHClient_noauth


class DUT_Status():
    def __init__(self, made_ips, beamer_ip, product_type):
        self.dut_ips = made_ips
        self.beamer_ip = beamer_ip
        self.product_type = product_type
        self.logger = logging.getLogger('main')
        self.logger.info(f'DUT IP: {self.dut_ips}')
        self.logger.info(f'beamer_ip: {self.beamer_ip}')

    def _product_key_check(self):
        ssh = _SSH_Shell()
        ssh.open(self.beamer_ip, 22, username='toor4nsn', password='oZPS0POrRieRtu')
        stdout = ssh.command("cd /mnt/factory/configs/unit && cat module_product_code.txt")
        product_code = stdout[0].strip().split('.')[0]
        self.logger.info("get product code => "+product_code)
        print("get product code => "+product_code)
        ssh.close()
        product_code_pairs = {
            'AEQZ': "475444A",
            'AENB': "475728A",
            'AEQE': "474750A"
        }
        if product_code == product_code_pairs[self.product_type]:
            return True
        else:
            self.logger.error("product code NOT match!")
            print("product code NOT match!")
            raise ProductKeyNotMatchError

    def ping_duts(self, time_out=300):
        repeat = 0
        connected_count = 0 # made connected count
        while repeat < time_out/10:
            for dut_ip in self.dut_ips:
                with subprocess.Popen(['ping',dut_ip],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT) as out:
                    stdout, stderr = out.communicate()
                    self.logger.info(f'ping {dut_ip} with 32 bytes')
                    self.logger.info('get output =>' + stdout.decode('utf-8').split('\n')[2])
                    if b'bytes=32 time<1ms TTL=64' in stdout or b'bytes=32 time=1ms TTL=64' in stdout:
                        # print(f"dut {dut_ip} connected")
                        self.logger.info(f'dut {dut_ip} connected')
                        connected_count += 1
                    else:
                        # print(f"dut {dut_ip} not connectd")
                        self.logger.info(f"dut {dut_ip} not connectd")

            repeat += 1
            if connected_count == len(self.dut_ips):
                self.logger.info('all duts connected!')
                return True
            connected_count = 0
        return False

    def check_testability(self):

        port = 22
        username = "root"
        command = "ps | grep lib"
        testability = False
        testability_count = 0
        repeat = 0
        while repeat < 30:
            for dut_ip in self.dut_ips:
                time.sleep(3)
                ssh = _SSH_Shell()
                ssh.open(hostname = dut_ip, port = port, username = username , password = None)
                stdout, stderr = ssh.command(command)
                # print(stdout)
                # logging.info('get output =>')
                # for line in stdout.split('\n'):
                #     logging.info(line)
                testability = "testability" in stdout
                if testability:
                    testability_count += 1
                self.logger.info(f'{dut_ip} testability readiness status is ' + str(testability))
                ssh.close()
            if testability_count == len(self.dut_ips):
                self.logger.info('Testability is ready!')
                return True
            else:
                self.logger.info('Testability not ready!')
                testability_count = 0
            repeat += 1
        return False



    def check_uoam(self):

        port = 22
        username = "toor4nsn"
        password = "oZPS0POrRieRtu"
        command = "ps | grep lib"
        uoam_readiness = False
        repeat = 0

        ssh = _SSH_Shell()
        ssh.open(hostname = self.beamer_ip, port=port, username = username , password = password )
        while repeat < 6:
            time.sleep(3)
            stdout,stderr = ssh.command(command)
            # print(stdout)
            # for line in stdout.split('\n'):
            #     logging.info(line)
            uoam_readiness = "uoamapp" in stdout
            self.logger.info('uoam readiness status is ' + str(uoam_readiness))
            if uoam_readiness:
                ssh.close()
                return True
            repeat += 1
        ssh.close()
        return False

    def check_dut_status(self):

        return self.ping_duts(time_out=300) and self._product_key_check() and self.check_testability() and self.check_uoam()
