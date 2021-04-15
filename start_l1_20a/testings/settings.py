import os
import sys
import time
import logging
try:
    from ..connections.miniftp import SCP
    from ..connections.connection import _FRMON, _SSH_Shell
except:
    current_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(current_path)))
    from tools_dev.connections.miniftp import SCP
    from tools_dev.connections.connection import _FRMON, _SSH_Shell

logger = logging.getLogger('main')
def disable_auto_reboot(beamer_ip="192.168.101.1", timeout=10):
    count = 0
    while count < timeout:
        frmon = _FRMON()
        frmon.open(ip_address=beamer_ip, end_str="\r\n")  #
        frmon.command("/ action create ResetControl /resetcontrol /module")
        time.sleep(1)
        out = frmon.command("/resetcontrol set recovery_reset_on false")
        # print("second:"+out)
        time.sleep(1)
        if "RecoveryReset canceled" in out or "RecoveryReset is already off" in out:
            print("disable autorebboot successfully!")
            break
        else:
            count += 1
        time.sleep(1)
    print("finish...")


def download_runtime_log(path=None, log_name=None):
    print("Catching runtime log...")
    if path is None:
        current_path = os.path.dirname(os.path.realpath(__file__))
        folder = current_path
    else:
        folder = path
    time_current = time.strftime("%Y%m%d%H%M%S")
    beamer_ip = "192.168.101.1"

    try:
        scp = SCP(host=beamer_ip, port=22, username="toor4nsn", password="oZPS0POrRieRtu")
        scp.connect()
        scp.write(f"/usr/bin/ccsShell.sh log -a -z runtime_{time_current}_{log_name}.zip")
        time.sleep(30)
        scp.download(local_path=folder + f"runtime_{time_current}_{log_name}.zip",
                     remote_path=f"/ram/runtime_{time_current}_{log_name}.zip", mode='bin')
        scp.close()
    except:
        logger.error("Error occur when grab log from beamer!")

# download_runtime_log(log_name='test')

def reset_reg_jesd(made_ips):
    command = '/sbin/devmem 0xfc980094 32 0x60'
    for ip in made_ips:
        # try:
            ssh = _SSH_Shell()
            ssh.open(hostname=ip, port=22, username='root', password=None)
            stdout, stderr = ssh.command('/sbin/devmem 0xfc980094')
            logger.info("read 0xfc980094 value first time => " + stdout.strip())
            print("read 0xfc980094 value first time => " + stdout)
            stdout, stderr = ssh.command('/sbin/devmem 0xfc980098') # read on regs
            logger.info("read 0xfc980098 value first time => " + stdout.strip())
            print("read 0xfc980094 value first time => " + stdout)
            time.sleep(1)
            ssh.command('/sbin/devmem 0xfc980094 32 0x60')
            ssh.command('/sbin/devmem 0xfc980098 32 0x60')
            time.sleep(1)
            stdout, stderr = ssh.command('/sbin/devmem 0xfc980094')
            logger.info("read 0xfc980094 value second time => " + stdout.strip())
            print("read 0xfc980094 value second time => " + stdout)
            stdout, stderr = ssh.command('/sbin/devmem 0xfc980098')  # read on regs
            logger.info("read 0xfc980098 value second time => " + stdout.strip())
            print("read 0xfc980098 value second time => " + stdout.strip())

            ssh.close()
        # except Exception as e:
        #     logger.info('error accours when write regs 0xfc980094 and 0xfc980098!!')
        #     logger.error(msg=e)

if __name__ == "__main__":
    reset_reg_jesd(made_ips = ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5'])
