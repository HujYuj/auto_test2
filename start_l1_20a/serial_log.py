import logging
import os
import time
import threading

try:
    from tools_dev.connections.connection import _COM
except:
    from .connections.connection import _COM


class SerialLog(object):

    def __init__(self):
        self._running = True
        self._catchlog = False
        self._init_log_file_path()

    def _init_log_file_path(self):
        self.logger = logging.getLogger("serial_log")
        root_path = os.path.dirname(os.path.realpath(__file__))
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        time_current = time.strftime("%Y%m%d%H%M%S")
        file_handler = logging.FileHandler(
            filename=os.path.join(root_path, f'testings/MainTestResults/serialLog/SerialLog_{time_current}.log'))
        print("created logfile: " + time_current)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        self.log_file_path = os.path.join(root_path, f'testings/MainTestResults/serialLog/SerialLog_{time_current}.log')

    def catch_log(self):
        self._catchlog = True
        print("catch log set to true!")

    def terminate(self):
        self._running = False
        print('terminate serial connection!')

    def run(self):
        COM = _COM(name="s", com_port="COM9", baudrate=115200, timeout=1)
        COM.open()
        self.logger.info("this is serial logger")
        while self._running and not self._catchlog:
            # COM.write(b'\n')
            out = COM.read_all().decode('utf-8')
            if len(out):
                self.logger.info(out)
        COM.close()
        print("serial closed!!")
        self.close_logger()

    def close_logger(self):
        for h in self.logger.handlers:
            if logging.FileHandler == type(h):
                h.close()
                self.logger.removeHandler(h)
        if not self._catchlog:
            os.remove(self.log_file_path)


if __name__ == "__main__":
    s = SerialLog()
    t1 = threading.Thread(target=s.run)
    t1.start()

    time.sleep(15)
    # s.catch_log()
    s.terminate()
    t1.join()
