# -*- coding: utf-8 -*-
"""
    :author: Wang, Fuqiang Q. (NSB - CN/Hangzhou) <fuqiang.q.wang@nokia-sbell.com>
"""

from threading import Thread
import subprocess
import shlex, os, re, platform

#this is a workaround for callback method.
# sys.setrecursionlimit(10000)

class AsynCommandExecuter:
    """T-Gate 5G L1 DUT control."""

    def __init__( self,  command_line: str, callback=None):
        self.command_line = command_line
        self.callback = callback
        self.system = platform.system()
        self.SYSTEM_WINDOWS = "Windows"
        self.SYSTEM_LINUX = "Linux"
        self.error_info = None
        self.error_pattern = "^[a-zA-Z]+Error:"

    def async_command(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()

        return wrapper

    @async_command
    def start(self):
        _output = ""
        cmd = shlex.split(self.command_line.replace(os.sep, "/"))
        if self.system == self.SYSTEM_WINDOWS:
            self.process = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        # stderr=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        # universal_newlines=True,
                                        shell=True,
                                        # preexec_fn=os.setsid())
                                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            # self.process = subprocess.Popen(cmd,
            #                             stdout=subprocess.PIPE,
            #                             stderr=subprocess.STDOUT,
            #                             universal_newlines=True,
            #                             shell=True,
            #                             preexec_fn=os.setsid())
            self.process = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        universal_newlines=True,
                                        shell=False
                                       )

        print(f"command executer[{self.command_line}] started with process id: {self.process.pid}")
        while True:
            # output = self.process.stdout.readline().decode('utf-8')
            if self.system == self.SYSTEM_WINDOWS:
                try:
                    output = self.process.stdout.readline().decode('utf-8')
                except UnicodeDecodeError as err:
                    print(str(err))
                # output = self.process.stdout.readline()
                # print(f"output: {output}")
                # output = output.decode('utf-8')
            else:
                output = self.process.stdout.readline()

            if re.search(self.error_pattern, output):
                self.error_info = output
            print(f"normal output: {output}")
            # output = self.trim(output)
            # if self.callback is not None:
            #     self.callback(output.strip())

            return_code = self.process.poll()
            # print(f"before return code, return_code: {return_code}")

            # self.process.communicate()
            # return_code_2 = self.process.returncode
            # print(f"before return code, return_code_2: {return_code_2}")
            # return_code = return_code_1
            if return_code is not None:
                # Process has finished, read rest of the output
                for output in self.process.stdout.readlines():
                    output = output.decode('utf-8')
                    # output = self.trim(output)
                    print(f" after returned code, {output.strip()}")
                    # _output += output
                    if self.callback is not None:
                        # self.callback(output.strip())
                        self.callback(output)

                print(f'RETURN CODE {return_code}: {self.error_info}')
                if self.callback is not None:
                    if return_code == 0:
                        self.callback("Done with return code {}".format(return_code))
                    else:
                        self.callback("Done with return code {}: {}".format(return_code, self.error_info))
                break
        return _output

    def trim(self, string: str):
        stripped = string.strip()
        if len(stripped) > 0:
            return string
        else:
            return stripped

    def stop(self):
        print("process id:" + str(self.process.pid))
        if self.system == self.SYSTEM_WINDOWS:
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
        else:
            # os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process.kill()
        # self.process.kill()
        # os.kill(self.process.pid, signal.CTRL_C_EVENT)
        # print("stop invoked!!!")

    def get_status(self):
        status = "Not started"
        if hasattr(self, 'process'):
            return_code = self.process.returncode
            if return_code is None:
                status = "Running"
            else:
                status = "Stopped"
        return status


    def setCommand(self, command):
        self.command_line = command

    def setCallback(self, callback):
        self.callback = callback

    def execute(self):
        _output = ""
        cmd = shlex.split(self.command_line.replace(os.sep, "/"))
        if self.system == self.SYSTEM_WINDOWS:
            self.process = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        # stderr=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        universal_newlines=True,
                                        shell=True,
                                        # preexec_fn=os.setsid())
                                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            self.process = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        universal_newlines=True,
                                        shell=True,
                                        preexec_fn=os.setsid())

        while True:
            _output += self.process.stdout.readline()
            # Do something else
            return_code = self.process.poll()
            if return_code is not None:
                # Process has finished, read rest of the output
                for output in self.process.stdout.readlines():
                    print(output.strip())
                    _output += output
                break

        result = {
            "return_code": return_code,
            "output": _output
        }
        return result

