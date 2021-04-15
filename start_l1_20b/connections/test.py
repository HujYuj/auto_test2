from paramiko import AutoAddPolicy
from scp import SCPClient
from connection import SSHClient_noauth, _SSH_Shell
import paramiko
from paramiko import SSHClient
import time, os

def download_from_ftp_to_local_SCP(host,port,ftp_path, local_file, mode = 'bin', user = 'root', password = 'root'):
    """ This keyword download a file from Ftp server to local of test case running.
    example usage:
    | Download From Ftp To Local | ftp://10.56.117.112/etc/ipsec_configuration.xml | c:${/}ipsec_configuration.xml | BIN |

    | Return value | the output of command |
    """
    try:
        scp_obj = SCP(host, port, user, password)
        scp_obj.connect()
    except Exception:
        print("error")
        scp_obj = SCP(host, port, user, password)

    if os.path.isdir(local_file):
        print('not support now!')
    else:
        scp_obj.download(local_file, ftp_path, mode)
        scp_obj.close()

class SCP(object):
    def __init__(self, host, port, username='root', password='root'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def createSSHClient(self,server,port,user,password):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(server, port, user, password)
        return client

    def createSSHClient_No_password(self,server,port,user,password = None):
        t = SSHClient_noauth()
        t.set_missing_host_key_policy(AutoAddPolicy())
        t.connect(server,port,user,password)
        return t


    def connect(self):
        try:
            self.ssh= self.createSSHClient(self.host, self.port, self.username, self.password)
            self.scp = SCPClient(self.ssh.get_transport())
            print('success to conenct SCP Client')
        except:
            self.ssh = False
            return self.ssh
    def upload(self, local_path, remote_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError("Invalid Ftp mode (%s)" % mode)

        file_mode = (mode == 'bin') and 'rb' or 'r'#file_mode = 'rb',rb represent readonly
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.scp.put(local_path,remote_path) #store a file in binary mode
                print('success to upload %s to remote_path %s'%(local_path,remote_path))
            else:
                print('error') #store a file in line mode
            return True
        finally:
            file.close()

        return False

    def download(self, local_path, remote_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError("Invalid Ftp mode (%s)" % mode)

        file_mode = (mode == 'bin') and 'w+b' or 'w'
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.scp.get(remote_path,local_path)
                print('success to download remote file to local')
            else:
                print('error')

#            self.log.debug("get %s" % ftp_path)
#            self.log.trace(ret)
            file.close()

            return True
        except Exception as e:
            file.close()
            os.remove(local_path)
            raise e

        return False
    def close(self):
        self.ssh.close()

folder = "./"
t = time.strftime('%Y%m%d%H%M%S')
download_from_ftp_to_local_SCP("192.168.101.1", 22, "/ram/log.zip", folder+t+"_runtime.zip", mode = 'bin', user = 'toor4nsn', password = 'oZPS0POrRieRtu')
