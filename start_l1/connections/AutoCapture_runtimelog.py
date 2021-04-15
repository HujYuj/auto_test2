# import wx,time,pyvisa,os
import time
import subprocess as sp
from paramiko import *

import locale
import os
import re
from socket import timeout as SocketTimeout


# this is quote from the shlex module, added in py3.3
_find_unsafe = re.compile(br'[^\w@%+=:,./~-]').search


def _sh_quote(s):
    """Return a shell-escaped version of the string `s`."""
    if not s:
        return b""
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return b"'" + s.replace(b"'", b"'\"'\"'") + b"'"


# Unicode conversion functions; assume UTF-8

def asbytes(s):
    """Turns unicode into bytes, if needed.

    Assumes UTF-8.
    """
    if isinstance(s, bytes):
        return s
    else:
        return s.encode('utf-8')


def asunicode(s):
    """Turns bytes into unicode, if needed.

    Uses UTF-8.
    """
    if isinstance(s, bytes):
        return s.decode('utf-8', 'replace')
    else:
        return s


# os.path.sep is unicode on Python 3, no matter the platform
bytes_sep = asbytes(os.path.sep)


# Unicode conversion function for Windows
# Used to convert local paths if the local machine is Windows

def asunicode_win(s):
    """Turns bytes into unicode, if needed.
    """
    if isinstance(s, bytes):
        return s.decode(locale.getpreferredencoding())
    else:
        return s
class SCPClient(object):
    """
    An scp1 implementation, compatible with openssh scp.
    Raises SCPException for all transport related errors. Local filesystem
    and OS errors pass through.

    Main public methods are .put and .get
    The get method is controlled by the remote scp instance, and behaves
    accordingly. This means that symlinks are resolved, and the transfer is
    halted after too many levels of symlinks are detected.
    The put method uses os.walk for recursion, and sends files accordingly.
    Since scp doesn't support symlinks, we send file symlinks as the file
    (matching scp behaviour), but we make no attempt at symlinked directories.
    """
    def __init__(self, transport, buff_size=16384, socket_timeout=5.0,
                 progress=None, sanitize=_sh_quote):
        """
        Create an scp1 client.

        @param transport: an existing paramiko L{Transport}
        @type transport: L{Transport}
        @param buff_size: size of the scp send buffer.
        @type buff_size: int
        @param socket_timeout: channel socket timeout in seconds
        @type socket_timeout: float
        @param progress: callback - called with (filename, size, sent) during
            transfers
        @param sanitize: function - called with filename, should return
            safe or escaped string.  Uses _sh_quote by default.
        @type progress: function(string, int, int)
        """
        self.transport = transport
        self.buff_size = buff_size
        self.socket_timeout = socket_timeout
        self.channel = None
        self.preserve_times = False
        self._progress = progress
        self._recv_dir = b''
        self._rename = False
        self._utime = None
        self.sanitize = sanitize
        self._dirtimes = {}

    def __enter__(self):
        self.channel = self._open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def put(self, files, remote_path=b'.',
            recursive=False, preserve_times=False):
        """
        Transfer files to remote host.

        @param files: A single path, or a list of paths to be transfered.
            recursive must be True to transfer directories.
        @type files: string OR list of strings
        @param remote_path: path in which to receive the files on the remote
            host. defaults to '.'
        @type remote_path: str
        @param recursive: transfer files and directories recursively
        @type recursive: bool
        @param preserve_times: preserve mtime and atime of transfered files
            and directories.
        @type preserve_times: bool
        """
        self.preserve_times = preserve_times
        self.channel = self._open()
        self._pushed = 0
        self.channel.settimeout(self.socket_timeout)
        scp_command = (b'scp -t ', b'scp -r -t ')[recursive]
        self.channel.exec_command(scp_command +
                                  self.sanitize(asbytes(remote_path)))
        self._recv_confirm()

        if not isinstance(files, (list, tuple)):
            files = [files]

        if recursive:
            self._send_recursive(files)
        else:
            self._send_files(files)

        self.close()

    def get(self, remote_path, local_path='',
            recursive=False, preserve_times=False):
        """
        Transfer files from remote host to localhost

        @param remote_path: path to retreive from remote host. since this is
            evaluated by scp on the remote host, shell wildcards and
            environment variables may be used.
        @type remote_path: str
        @param local_path: path in which to receive files locally
        @type local_path: str
        @param recursive: transfer files and directories recursively
        @type recursive: bool
        @param preserve_times: preserve mtime and atime of transfered files
            and directories.
        @type preserve_times: bool
        """
        if not isinstance(remote_path, (list, tuple)):
            remote_path = [remote_path]
        remote_path = [self.sanitize(asbytes(r)) for r in remote_path]
        self._recv_dir = local_path or os.getcwd()
        self._rename = (len(remote_path) == 1 and
                        not os.path.isdir(os.path.abspath(local_path)))
        if len(remote_path) > 1:
            if not os.path.exists(self._recv_dir):
                raise SCPException("Local path '%s' does not exist" %
                                   asunicode(self._recv_dir))
            elif not os.path.isdir(self._recv_dir):
                raise SCPException("Local path '%s' is not a directory" %
                                   asunicode(self._recv_dir))
        rcsv = (b'', b' -r')[recursive]
        prsv = (b'', b' -p')[preserve_times]
        self.channel = self._open()
        self._pushed = 0
        self.channel.settimeout(self.socket_timeout)
        self.channel.exec_command(b"scp" +
                                  rcsv +
                                  prsv +
                                  b" -f " +
                                  b' '.join(remote_path))
        self._recv_all()
        self.close()

    def _open(self):
        """open a scp channel"""
        if self.channel is None:
            self.channel = self.transport.open_session()

        return self.channel

    def close(self):
        """close scp channel"""
        if self.channel is not None:
            self.channel.close()
            self.channel = None

    def _read_stats(self, name):
        """return just the file stats needed for scp"""
        if os.name == 'nt':
            name = asunicode(name)
        stats = os.stat(name)
        mode = oct(stats.st_mode)[-4:]
        size = stats.st_size
        atime = int(stats.st_atime)
        mtime = int(stats.st_mtime)
        return (mode, size, mtime, atime)

    def _send_files(self, files):
        for name in files:
            basename = asbytes(os.path.basename(name))
            (mode, size, mtime, atime) = self._read_stats(name)
            if self.preserve_times:
                self._send_time(mtime, atime)
            file_hdl = open(name, 'rb')

            # The protocol can't handle \n in the filename.
            # Quote them as the control sequence \^J for now,
            # which is how openssh handles it.
            self.channel.sendall(("C%s %d " % (mode, size)).encode('ascii') +
                                 basename.replace(b'\n', b'\\^J') + b"\n")
            self._recv_confirm()
            file_pos = 0
            if self._progress:
                if size == 0:
                    # avoid divide-by-zero
                    self._progress(basename, 1, 1)
                else:
                    self._progress(basename, size, 0)
            buff_size = self.buff_size
            chan = self.channel
            while file_pos < size:
                chan.sendall(file_hdl.read(buff_size))
                file_pos = file_hdl.tell()
                if self._progress:
                    self._progress(basename, size, file_pos)
            chan.sendall('\x00')
            file_hdl.close()
            self._recv_confirm()

    def _chdir(self, from_dir, to_dir):
        # Pop until we're one level up from our next push.
        # Push *once* into to_dir.
        # This is dependent on the depth-first traversal from os.walk

        # add path.sep to each when checking the prefix, so we can use
        # path.dirname after
        common = os.path.commonprefix([from_dir + bytes_sep,
                                       to_dir + bytes_sep])
        # now take the dirname, since commonprefix is character based,
        # and we either have a seperator, or a partial name
        common = os.path.dirname(common)
        cur_dir = from_dir.rstrip(bytes_sep)
        while cur_dir != common:
            cur_dir = os.path.split(cur_dir)[0]
            self._send_popd()
        # now we're in our common base directory, so on
        self._send_pushd(to_dir)

    def _send_recursive(self, files):
        for base in files:
            if not os.path.isdir(base):
                # filename mixed into the bunch
                self._send_files([base])
                continue
            last_dir = asbytes(base)
            for root, dirs, fls in os.walk(base):
                self._chdir(last_dir, asbytes(root))
                self._send_files([os.path.join(root, f) for f in fls])
                last_dir = asbytes(root)
            # back out of the directory
            while self._pushed > 0:
                self._send_popd()

    def _send_pushd(self, directory):
        (mode, size, mtime, atime) = self._read_stats(directory)
        basename = asbytes(os.path.basename(directory))
        if self.preserve_times:
            self._send_time(mtime, atime)
        self.channel.sendall(('D%s 0 ' % mode).encode('ascii') +
                             basename.replace(b'\n', b'\\^J') + b'\n')
        self._recv_confirm()
        self._pushed += 1

    def _send_popd(self):
        self.channel.sendall('E\n')
        self._recv_confirm()
        self._pushed -= 1

    def _send_time(self, mtime, atime):
        self.channel.sendall(('T%d 0 %d 0\n' % (mtime, atime)).encode('ascii'))
        self._recv_confirm()

    def _recv_confirm(self):
        # read scp response
        msg = b''
        try:
            msg = self.channel.recv(512)
        except SocketTimeout:
            raise SCPException('Timout waiting for scp response')
        # slice off the first byte, so this compare will work in py2 and py3
        if msg and msg[0:1] == b'\x00':
            return
        elif msg and msg[0:1] == b'\x01':
            raise SCPException(asunicode(msg[1:]))
        elif self.channel.recv_stderr_ready():
            msg = self.channel.recv_stderr(512)
            raise SCPException(asunicode(msg))
        elif not msg:
            raise SCPException('No response from server')
        else:
            raise SCPException('Invalid response from server', msg)

    def _recv_all(self):
        # loop over scp commands, and receive as necessary
        command = {b'C': self._recv_file,
                   b'T': self._set_time,
                   b'D': self._recv_pushd,
                   b'E': self._recv_popd}
        while not self.channel.closed:
            # wait for command as long as we're open
            self.channel.sendall('\x00')
            msg = self.channel.recv(1024)
            if not msg:  # chan closed while recving
                break
            assert msg[-1:] == b'\n'
            msg = msg[:-1]
            code = msg[0:1]
            try:
                command[code](msg[1:])
            except KeyError:
                raise SCPException(asunicode(msg[1:]))
        # directory times can't be set until we're done writing files
        self._set_dirtimes()

    def _set_time(self, cmd):
        try:
            times = cmd.split(b' ')
            mtime = int(times[0])
            atime = int(times[2]) or mtime
        except:
            self.channel.send(b'\x01')
            raise SCPException('Bad time format')
        # save for later
        self._utime = (atime, mtime)

    def _recv_file(self, cmd):
        chan = self.channel
        parts = cmd.strip().split(b' ', 2)

        try:
            mode = int(parts[0], 8)
            size = int(parts[1])
            if self._rename:
                path = self._recv_dir
                self._rename = False
            elif os.name == 'nt':
                path = os.path.join(asunicode_win(self._recv_dir),
                                    parts[2].decode('utf-8'))
            else:
                path = os.path.join(asbytes(self._recv_dir),
                                    parts[2])
        except:
            chan.send('\x01')
            chan.close()
            raise SCPException('Bad file format')

        try:
            file_hdl = open(path, 'wb')
        except IOError as e:
            chan.send(b'\x01' + str(e).encode('utf-8'))
            chan.close()
            raise

        if self._progress:
            if size == 0:
                # avoid divide-by-zero
                self._progress(path, 1, 1)
            else:
                self._progress(path, size, 0)
        buff_size = self.buff_size
        pos = 0
        chan.send(b'\x00')
        try:
            while pos < size:
                # we have to make sure we don't read the final byte
                if size - pos <= buff_size:
                    buff_size = size - pos
                file_hdl.write(chan.recv(buff_size))
                pos = file_hdl.tell()
                if self._progress:
                    self._progress(path, size, pos)

            msg = chan.recv(512)
            if msg and msg[0:1] != b'\x00':
                raise SCPException(asunicode(msg[1:]))
        except SocketTimeout:
            chan.close()
            raise SCPException('Error receiving, socket.timeout')

        file_hdl.truncate()
        try:
            os.utime(path, self._utime)
            self._utime = None
            os.chmod(path, mode)
            # should we notify the other end?
        finally:
            file_hdl.close()
        # '\x00' confirmation sent in _recv_all

    def _recv_pushd(self, cmd):
        parts = cmd.split(b' ', 2)
        try:
            mode = int(parts[0], 8)
            if self._rename:
                path = self._recv_dir
                self._rename = False
            elif os.name == 'nt':
                path = os.path.join(asunicode_win(self._recv_dir),
                                    parts[2].decode('utf-8'))
            else:
                path = os.path.join(asbytes(self._recv_dir),
                                    parts[2])
        except:
            self.channel.send(b'\x01')
            raise SCPException('Bad directory format')
        try:
            if not os.path.exists(path):
                os.mkdir(path, mode)
            elif os.path.isdir(path):
                os.chmod(path, mode)
            else:
                raise SCPException('%s: Not a directory' % path)
            self._dirtimes[path] = (self._utime)
            self._utime = None
            self._recv_dir = path
        except (OSError, SCPException) as e:
            self.channel.send(b'\x01' + asbytes(str(e)))
            raise

    def _recv_popd(self, *cmd):
        self._recv_dir = os.path.split(self._recv_dir)[0]

    def _set_dirtimes(self):
        try:
            for d in self._dirtimes:
                os.utime(d, self._dirtimes[d])
        finally:
            self._dirtimes = {}


class SCPException(Exception):
    """SCP exception class"""
    pass

class SSHClient_noauth(SSHClient):
    def _auth(self, username, *args):
        self._transport.auth_none(username)
        return

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
class _SSH_Shell():
    def __init__(self):
        None

    def open(self,hostname,port,username = 'root',password = None):
        if password == "None":
            password = None
        if password == None:
            self.ssh = SSHClient_noauth()
        else:
            self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.ssh.connect(hostname,port,username,password)
            return self
        except Exception:
            return False

    def write(self,command):
        stdin,stdout,stderr = self.ssh.exec_command(command)
        print("send command => %s"%command)#logging.info

        return stdin,stdout,stderr

    def write_long(self,command):
        stdin,stdout,stderr = self.ssh.exec_command(command)
        print("send command => %s"%command)
        result = ""
        for line1 in stderr.readlines():
            print("stdout=>"+str(line1))
            result = result+line1
        for line1 in stdout.readlines():
            print("stdout=>"+str(line1))
            result = result+line1
        return result


    def read(self,std):
        cmd_result = std[1].read().decode(encoding='utf-8'),std[2].read().decode(encoding='utf-8')
        print(time.strftime('%Y%m%d%H%M%S') + '=>'+cmd_result[0])
        return cmd_result

    def command(self,command):
        std = self.write(command)
        time.sleep(0.5)
        res = self.read(std)

        return res



    def close(self):
        self.ssh.close()
class Dialog(wx.App):
    def __init__(self,window):
        wx.App.__init__(self)
        self.window = window

    def erroralert(self,msg,title):
        dlg = wx.MessageDialog(None,msg,title,wx.OK|wx.CANCEL|wx.ICON_ERROR)
        result = dlg.ShowModal()
        if result == wx.CANCEL:
            dlg.Destroy()
        else:
            dlg.Destroy()
        return result

    def Infoalert(self,msg,title):
        dlg = wx.MessageDialog(None,msg,title,wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        if result == wx.CANCEL:
            dlg.Destroy()
        else:
            dlg.Destroy()
        return result

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
        scp_obj = SCP(host, port, user, password)

    if os.path.isdir(local_file):
        print('not support now!')
    else:
        scp_obj.download(local_file, ftp_path, mode)
        scp_obj.close()
def PowerSuppy_Init(interface,address):
    ''' sn should be string, eg: Init_NRP('103123'), '103123' is from NRP_Z21 power viewer
        Z11 productID: 0x000c, Z21 productID: 0x0003
    '''
    visaDLL = 'c:/windows/system32/visa64.dll'
    resourceManager = pyvisa.ResourceManager(visaDLL)
    if interface == "GPIB":
        print("PowerSupply remote mode is:"+ interface+", GPIB Address is:"+address)
        try:
            PS_handler = resourceManager.open_resource("GPIB0::%s::INSTR"%(address))
            return PS_handler
        except Exception:
            return False
    elif interface == "TCPIP":
        print("PowerSupply remote mode is:"+ interface+", IP Address is:"+address)
        try:
            PS_handler = resourceManager.open_resource("TCPIP0::%s::INSTR"%(address))
            return PS_handler
        except Exception:
            return False
    else:
        print("Not Supply this remote mode now")
        return False
def Set_Power_mode(handler,mode):
    if mode == "ON":
        handler.write("OUTPUT:STAT ON")
    else:
        handler.write("OUTPUT:STAT OFF")
def check_ip_pingable(ip_address):
    status, result = sp.getstatusoutput("ping " + ip_address + " -w 2000")
    print(status, "result="+result)
    if ("timed out" in result) or ("fail" in result):
        return False
    return True
def waitfor_pingable(ip_address,try_times):
    times = 1
    while True:

        res = check_ip_pingable(ip_address)
        if not res:
            print("ping %s Failed %s times"%(ip_address,times))

            if times > try_times:
                break
        else:
            print("ping %s Successfully!"%ip_address)

            break
        times+=1
    if times > try_times:
        return False
    else:
        return True
def Init_Breamer_shell():
    #Init beamer port
    #Input: config_file
    #Output: beamer handler or false if one is not avaliable
    beamer_ip = "192.168.101.1"
    beamer_port = 22
    beamer_username = "toor4nsn"
    beamer_pwd = "oZPS0POrRieRtu"
    beamer_c = _SSH_Shell()
    for try_time in range(1,10):
        beamer_handler = beamer_c.open(beamer_ip, beamer_port, beamer_username,beamer_pwd)
        print("init beamer:%s for %s times, result is %s"%(beamer_ip,try_time,beamer_handler))
        if beamer_handler == False:
            if try_time == 9:
                break
            else:
                pass
        else:
            break
        time.sleep(1)
    #beamer_handler.write("su root")
    return beamer_handler
def check_beamer_processer(beamer_handler):
    re = beamer_handler.command("ps")[0]
    print(re.find("libtestabilitytcp.so.1.0"))
    if re.find("libtestabilitytcp.so.1.0")>0:
        return True
    return False
dialog = Dialog(wx.App)
def Bring_up():
    dialog.Infoalert("Make sure the RRU is power on", "info")
    sum_run_count = 0
    fail_count = 0
    while True:
        #self.dialog.Infoalert("We will bring up beamer from flash,Please make sure the WE is UNCONNECTED!!!", "Warning")

#         powersuppy_handler = PowerSuppy_Init(interface,address)
#         if not powersuppy_handler:
#             dialog.erroralert("The Power supply init failed! Please check", "ERROR")
#             return False
#         Set_Power_mode(powersuppy_handler,"OFF")
#         time.sleep(5)
#         Set_Power_msode(powersuppy_handler,"ON")
        beamer_handler = Init_Breamer_shell()
        if not beamer_handler:
            dialog.erroralert("Beamer handler init failed for 10 times", "ERROR")
            return False

        beamer_handler.write("/usr/bin/rfsw-ncfg-reboot")
        sum_run_count+=1
        print("waiting for 60s...")
        time.sleep(120)
        beammer_ip = "192.168.101.1"
        T = waitfor_pingable(beammer_ip,1000)
        if not T:
            fail_count+=1
            print("reboot for %s times, beamer run failed %s times"%(sum_run_count,fail_count))
            continue

        print("Beamer Start up normally Now!")

        beamer_handler = Init_Breamer_shell()
        if not beamer_handler:
            dialog.erroralert("Beamer handler init failed for 10 times", "ERROR")
            return False

        retry_beamer = 0
        for retry_beamer in range(20):
            res = check_beamer_processer(beamer_handler)
            if res:

                break
            else:
                if retry_beamer == 19:
                    print("beamer can't start up correctly,will power down and up again")
                    beamer_handler.write("/usr/bin/ccsShell.sh log -c full")
                    time.sleep(10)
                    t = time.strftime('%Y%m%d%H%M%S')
                    folder = "./runtimelog"
                    if not os.path.exists(folder):
                        os.mkdir(folder)
                    download_from_ftp_to_local_SCP(beammer_ip,22,"/ram/1011_runtime.zip", folder+"/"+t+"_runtime.zip", mode = 'bin', user = 'toor4nsn', password = 'oZPS0POrRieRtu')
                    download_from_ftp_to_local_SCP(beammer_ip,22,"/ram/1011_startup.zip", folder+"/"+t+"_runtime.zip", mode = 'bin', user = 'toor4nsn', password = 'oZPS0POrRieRtu')
                    fail_count+=1
                    break
                time.sleep(2)
        print("reboot for %s times, beamer run failed %s times"%(sum_run_count,fail_count))

def runtimelog():
    beamer_handler = Init_Breamer_shell()
    beamer_handler.write("/usr/bin/ccsShell.sh log -c full")
    time.sleep(10)
    t = time.strftime('%Y%m%d%H%M%S')
    folder = "./runtimelog"
    if not os.path.exists(folder):
        os.mkdir(folder)
    download_from_ftp_to_local_SCP(beammer_ip, 22, "/ram/1011_runtime.zip", folder + "/" + t + "_runtime.zip",
                                   mode='bin', user='toor4nsn', password='oZPS0POrRieRtu')
    download_from_ftp_to_local_SCP(beammer_ip, 22, "/ram/1011_startup.zip", folder + "/" + t + "_runtime.zip",
                                   mode='bin', user='toor4nsn', password='oZPS0POrRieRtu')



# runtimelog()




