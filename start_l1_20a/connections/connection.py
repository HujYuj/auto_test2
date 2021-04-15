'''
Created on Feb 23, 2019

@author: hwiv
'''
import os, sys, time
import socket
import telnetlib
import logging
import serial
import paramiko
from paramiko import SSHClient

class SSHClient_noauth(SSHClient):
    def _auth(self, username, *args):
        self._transport.auth_none(username)

        return

class _SSH_Shell():
    def __init__(self):
        None

    def open(self, hostname, port, username = 'root', password = None):
        if password == "None":
            password = None
        if password == None:
            self.ssh = SSHClient_noauth()

        else:
            self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname,port,username,password)
            transport = self.ssh.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            return self
        except Exception:
            return False

    def write(self,command):
        stdin,stdout,stderr = self.ssh.exec_command(command)
        logging.info("send command => %s"%command)

        return stdin,stdout,stderr

    def write_long(self,command):
        stdin,stdout,stderr = self.ssh.exec_command(command)
        logging.info("send command => %s"%command)
        result = ""
        for line1 in stderr.readlines():
            logging.info("stdout=>"+str(line1))
            result = result+line1
        for line1 in stdout.readlines():
            logging.info("stdout=>"+str(line1))
            result = result+line1
        return result


    def read(self,std):
        cmd_result = std[1].read().decode(encoding='utf-8'),std[2].read().decode(encoding='utf-8')
        logging.info(time.strftime('%Y%m%d%H%M%S') + '=>'+cmd_result[0])
        return cmd_result

    def command(self,command):
        std = self.write(command)
        time.sleep(0.5)
        res = self.read(std)

        return res



    def close(self):
        self.ssh.close()


class _FRMON():
    """
    FRMON command class
    """
    def __init__(self):

        pass

    def open(self, ip_address,end_str, cmon_port = 2000):
        self.ip_address = ip_address
        self.end_str = end_str
        socket.setdefaulttimeout(10)
        try:
            self.session=telnetlib.Telnet(ip_address,int(cmon_port))
            self.session.read_until(end_str)
            print(self.session)
            self.end_str = end_str
            return self
        except:
            return False

    def command(self, command):
        """
        write a command to CMON port and read back response
        input: command, string
        return: response in string
        """
        self.write(command)
        return self.read()

    def write(self, command):
        try:
            self.session.write(command.encode(encoding='utf-8'))
            time.sleep(1)
            self.session.write(b"\r\n")
            logging.info("Send command:"+command)
        except Exception:
            logging.info("IP address is %s"%self.ip_address)
            open_flag = self.open(self.ip_address,self.end_str)
            time.sleep(1)
            self.session.write(command.encode(encoding='utf-8'))
            time.sleep(1)
            self.session.write(b"\r\n")
            time.sleep(1)
            logging.info("Send command:"+command)


    def read(self):
#        time.sleep(0.3)
        response = self.session.read_until(b'\r\n', 500).decode(encoding='utf-8')
        print(response)

        logging.info("response:  "+ response)
        return response

    def error(self, error_code):

        x="No error"

        response ={
                   "":     lambda x: "Fail connect to CMON",
                   "0x00": lambda x: "No error",
                   "0x01": lambda x: "Command not found",
                   "0x02": lambda x: "Invalid number of arguments",
                   "0x03": lambda x: "Invalid arguments",
                   "0x04": lambda x: "Invalid address",
                   "0x05": lambda x: "Invalid value",
                   "0x11": lambda x: "File not found",
                   "0x12": lambda x: "File name already exists",
                   "0x13": lambda x: "File size error",
                   "0x21": lambda x: "Time out",
                   "0xff": lambda x: "Undefined error"
        }[error_code](x)

        return response+"\n\n"


class _COM():
    def __init__(self, name, com_port, baudrate,timeout=1):
        self.name=name
        self.opened=False
        self.com_port=com_port
        self.baudrate = baudrate
        self.timeout = timeout

    def open(self):
        """
        This is a necessary function
        open this equipment, and get ready to use
        self.get_id() will be called and information will be save in log
        every time the equipment is opened.
        return: None
        """
        if self.opened:
            logging.info("Aready opened")
        else:
            # do something here to open equipment
            try:
                self.ser = serial.Serial(port=self.com_port, baudrate=self.baudrate, timeout=self.timeout)
                #self.read()
                self.opened=True
                return self
            except Exception as e:
                print(e)
                return False

    def read_until(self,read_string,write_command):
        flag = False
        while not flag:
            response=self.ser.readall()
            print('=>'+str(response))
            f = str(response).find(read_string)
            if f != -1:
                flag = True

        self.write(write_command)
        self.ser.readlines()


    def close(self):
        """
        This is a necessary function
        close this equipment
        return: None
        """
        if not self.opened:
            self.logger.warning("already closed")
        else:
            # do something here to close equipment
            self.ser.close()
            self.opened=False


    def read(self):
        response=self.ser.readlines()
        # print(response)
        response = response[-2]
        return response

    def read_all(self):
        response=self.ser.readall()
        # logging.info(time.strftime('%y%m%d_%H:%M:%S ')+'response =>'+str(response))
        return response

    def write(self, command):
        self.ser.write(command + b"\n")
        time.sleep(0.05)
        # logging.info(time.strftime('%y%m%d_%H:%M:%S ')+str(command))

    def write_re(self, command):
        self.ser.write(command + "\n")
        logging.info(time.strftime('%y%m%d_%H:%M:%S ')+str(command))
        #ime.sleep(0.01)
        res = self.read_all()
        logging.info(time.strftime('\n%y%m%d_%H:%M:%S ')+'res => '+str(res))
        return res

    def command(self, command):
        """
        write a command to shell and read back response
        input: command, string
        return: response in string
        """
        self.write(command)
        return self.read()

# COM = _COM(name='s', com_port="COM5", baudrate=115200)
# COM.open()
# COM.write(b"\n")
# stdout = COM.read_all().decode(encoding="utf-8")
# print(stdout)
# COM.close()
    # '''
    # def start(self, program):
    #     """
    #     Start chamber room.
    #     Input: program number.
    #     """
    #     self.write("z:Set:AutoStart:%s:CC" % program) #216,217,218,219
    #
    # def stop(self):
    #     """
    #     Stop chamber room running temp program.
    #     """
    #     self.write("z:Set:AutoStop:CC")
    # '''

class _Shell():
    """
    shell command class
    """
    def __init__(self, ip_address, shell_port,unit,end_str):
        socket.setdefaulttimeout(20)
        self.session=telnetlib.Telnet(ip_address,int(shell_port))
        self.session.read_until(end_str)#\n$
        self.unit = unit
        self.end_str = end_str

    def command(self, command):
        """
        write a command to shell and read back response
        input: command, string
        return: response in string
        """
        self.write(command)
        return self.read()

    def read(self):
        response=self.session.read_until(b"\n").decode(encoding='utf-8')
        logging.info("Get response <=="+response)
        return response


    def write(self, command):
        self.session.write(command.encode(encoding='utf-8'))
        time.sleep(1)
        self.session.write(b"\r\n")
        logging.info("Send command ==>"+command)

'''
com_c = _COM("COM38","COM38",115200)
com_handler = com_c.open()

com_handler.write(chr(0x03).encode(encoding='utf-8'))
print(com_handler.read())
com_handler.close()

a = _SSH_Shell()
a.open("192.168.101.7",22)
a.command("HAHA")
'''
# frmon = _FRMON()
# frmon.open("192.168.101.1",2000)
# frmon.command("kerjwejra")

