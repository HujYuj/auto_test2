import os
from ftplib import FTP
import paramiko
import logging
try:
    from scp import SCPClient
    from .connection import SSHClient_noauth
    #from Utils.log import Logger
except:
    from tools_dev.connections.scp import SCPClient
    from tools_dev.connections.connection import SSHClient_noauth

class MiniFTP(object):
    def __init__(self, host, port, username='anonymous', password='anonymous', root_path='', log_level = 'info'):
        ftp = FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        self.ftp = ftp

        for dir_name in root_path.split("/"):
            self.cdw(dir_name)

    def cdw(self, path):
        if not path:
            return

        for dir_name in path.split("/"):
            try:
                self.ftp.cwd(dir_name) #change to directory called "dir_name"
            except:
                self.ftp.mkd(dir_name)
                self.ftp.cwd(dir_name)

#        self.log.debug("cd %s" % path)

    def upload(self, local_path, ftp_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError("Invalid Ftp mode (%s)" % mode)

        file_mode = (mode == 'bin') and 'rb' or 'r'#file_mode = 'rb',rb represent readonly
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.ftp.storbinary('STOR %s' % ftp_path, file) #store a file in binary mode
            else:
                ret = self.ftp.storlines('STOR %s' % ftp_path, file) #store a file in line mode
#            self.log.debug("put %s" % ftp_path)
#            self.log.trace(ret)

            return True
        finally:
            file.close()

        return False

    def upload_dirs(self, local_dir, ftp_dir):
        if not os.path.isdir(local_dir):
            raise RuntimeError("'%s' not a directory!" % local_dir)

        file_count = 0
        dir_count = 0
        path_list = [ [ e for e in os.listdir(local_dir) if e != '.svn' ], ]
        path = [ local_dir ]

        self.cdw(ftp_dir)

        while path_list:
            while path_list[-1]:
                file = path_list[-1].pop()
                cur_path = os.path.join(*path + [ file ])

                if os.path.isdir(os.path.join(*path + [ file ])):
                    self.cdw(file)
                    path.append(file)
                    cur_list = [ e for e in os.listdir(cur_path) if e != '.svn' ]
                    path_list.append(cur_list)
                    dir_count += 1
                else:
                    if self.upload(cur_path, file):
                        file_count += 1

            if len(path) > 1:
                self.cdw("..")
                path.pop()
            path_list.pop()

        return (True, file_count, dir_count)

    def download(self, local_path, ftp_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError("Invalid Ftp mode (%s)" % mode)

        file_mode = (mode == 'bin') and 'w+b' or 'w'
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.ftp.retrbinary('RETR %s' % ftp_path, file.write)
            else:
                ret = self.ftp.retrlines('RETR %s' % ftp_path, file.writelines)

#            self.log.debug("get %s" % ftp_path)
#            self.log.trace(ret)
            file.close()

            return True
        except Exception as e:
            file.close()
            os.remove(local_path)
            raise e

        return False

    def download_dirs(self, local_dir, ftp_dir):
        raise RuntimeError("not supported operation!")


    def list(self, path=""):
        dirs = self.ftp.dir(path)
        print(dirs)


class SFTP(object):
    def __init__(self, host, port, username='root', password='root', root_path='', log_level = 'info'):
        try:
            t = paramiko.Transport(host,port)
            t.connect(hostkey = None,username = 'root',password = 'root')
            self.sftp = paramiko.SFTPClient.from_transport(t)



        except Exception as e:
            logging.info('ssh %s@%s:%s'%(username,host,e))
            exit()

    def cdw(self, path):
        if not path:
            return

        for dir_name in path.split("/"):
            try:
                self.ftp.cwd(dir_name) #change to directory called "dir_name"
            except:
                self.ftp.mkd(dir_name)
                self.ftp.cwd(dir_name)

#        self.log.debug("cd %s" % path)

    def upload(self, local_path, ftp_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError("Invalid Ftp mode (%s)" % mode)

        file_mode = (mode == 'bin') and 'rb' or 'r'#file_mode = 'rb',rb represent readonly
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.sftp.put(local_path,ftp_path) #store a file in binary mode
            else:
                ret = self.sftp.put(local_path,ftp_path) #store a file in line mode
#            self.log.debug("put %s" % ftp_path)
#            self.log.trace(ret)

            return True
        finally:
            file.close()

        return False

    def upload_dirs(self, local_dir, ftp_dir):
        if not os.path.isdir(local_dir):
            raise RuntimeError("'%s' not a directory!" % local_dir)

        file_count = 0
        dir_count = 0
        path_list = [ [ e for e in os.listdir(local_dir) if e != '.svn' ], ]
        path = [ local_dir ]

        #self.cdw(ftp_dir)

        while path_list:
            while path_list[-1]:
                file = path_list[-1].pop()
                cur_path = os.path.join(*path + [ file ])
                ftp_file = ftp_dir+file

                if os.path.isdir(os.path.join(*path + [ file ])):
                    #self.cdw(file)
                    path.append(file)
                    cur_list = [ e for e in os.listdir(cur_path) if e != '.svn' ]
                    path_list.append(cur_list)
                    dir_count += 1
                else:
                    if self.upload(cur_path, ftp_file):
                        file_count += 1

            if len(path) > 1:

                path.pop()
            path_list.pop()

        return (True, file_count, dir_count)

    def download(self, local_path, ftp_path, mode='bin'):

        mode = mode and mode.lower() or 'bin'
        if(mode not in ('bin', 'text')):
            raise RuntimeError("Invalid Ftp mode (%s)" % mode)

        file_mode = (mode == 'bin') and 'w+b' or 'w'
        file = open(local_path, file_mode)
        try:
            if(mode == 'bin'):
                ret = self.sftp.get(ftp_path,local_path)
            else:
                ret = self.sftp.get(ftp_path,local_path)

#            self.log.debug("get %s" % ftp_path)
#            self.log.trace(ret)
            file.close()

            return True
        except Exception as e:
            file.close()
            os.remove(local_path)
            raise e

        return False

    def download_dirs(self, local_dir, ftp_dir):
        raise RuntimeError("not supported operation!")


    def list(self, path=""):
        dirs = self.ftp.dir(path)
        print(dirs)


class SCP(object):
    def __init__(self, host, port, username='root', password='root'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def createSSHClient(self,server,port,user,password):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client

    def createSSHClient_No_password(self,server,port,user,password = None):
        t = SSHClient_noauth()
        t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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

    def connect_noPassword(self):
        try:
            self.ssh= self.createSSHClient_No_password(self.host, self.port, self.username, self.password)
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

    def write(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdin, stdout, stderr

    def close(self):
        self.ssh.close()

'''
scp = SCP('192.168.254.11',22)
scp.connect()
local = '../Template/CALI_D.xml'
remote = '/mnt/CALI_D.xml'
scp.upload(local, remote)
'''
