import logging
import os
import sys
import time
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(current_path)))
# add tools_dev into sys path
from auto_test.start_l1.connections.connection import _SSH_Shell

class CpriSync():
    def __init__(self):
        self.host = "192.168.101.1"
        self.port = 22
        self.username = "toor4nsn"
        self.password = "oZPS0POrRieRtu"
        self.logger = logging.getLogger('main')

    def Cpri_test(self, REPEAT=30):
        command = "/sbin/devmem 0x80301004"
        ssh = _SSH_Shell()
        ssh.open(hostname=self.host, port=self.port, username=self.username, password=self.password)
        test_pass = False
        for i in range(REPEAT):
            stdin, stdout, stderr = ssh.write(command)
            self.logger.info("send command => " + command)
            for line in stdout:
                line = line.strip()
                self.logger.info("get output => " + line)
                if line == "0x00000010":
                    self.logger.info("CPRI LINK sync successully!")
                    ssh.close()
                    return True
                else:
                    self.logger.info("CPRI LINK sync fail!")

            time.sleep(5)
        ssh.close()
        return False
        # return test_pass

if __name__ == "__main__":
    # logging.basicConfig(filename="CpriSync.log", level=logging.INFO)
    CPRISync_handler = CpriSync()
    CpriSync().Cpri_test(REPEAT=300)
