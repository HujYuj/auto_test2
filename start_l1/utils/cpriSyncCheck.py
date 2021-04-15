import logging
import os
import sys
import time

try:
    from auto_test.start_l1.connections.connection import _SSH_Shell
    from auto_test.start_l1.utils.Exceptions import *
except:
    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(current_path))))
    from auto_test.start_l1.connections.connection import _SSH_Shell
    from auto_test.start_l1.utils.Exceptions import *


def cpri_check(time_out=30):
    logger = logging.getLogger("main")
    CHECK_CPRI_SYNC_COMMAND = "/sbin/devmem 0x80301004"
    BEAMER_IP = "192.168.101.1"
    PORT = 22
    USER_NAME = "toor4nsn"
    PASSWORD = "oZPS0POrRieRtu"

    ssh = _SSH_Shell()
    ssh.open(hostname=BEAMER_IP, port=PORT, username=USER_NAME, password=PASSWORD)
    repeat = 0
    while repeat < time_out:
        stdin, stdout, stderr = ssh.write(CHECK_CPRI_SYNC_COMMAND)
        logger.info("send command => " + CHECK_CPRI_SYNC_COMMAND)
        for line in stdout:
            line = line.strip()
            logger.info("get output => " + line)
            if line == "0x00000010":
                logger.info("CPRI LINK sync successfully!")
                ssh.close()
                return
            else:
                logger.info("CPRI LINK sync fail!")
        repeat += 1
        time.sleep(5)
    ssh.close()
    raise CpriSyncFailException

if __name__ == "__main__":
    # logging.basicConfig(filename="CpriSync.log", level=logging.INFO)
    cpri_check(time_out=30)
