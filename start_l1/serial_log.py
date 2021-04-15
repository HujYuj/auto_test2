"""
Create serial log in separate thread
Use t.catch_log() to terminate logging and save file
Use t.terminate() to terminate logging and remove file

"""
import logging
import os, sys
import time
import threading

try:
    from auto_test.start_l1.connections.connection import _COM
    from auto_test.lib_service.log_handler.socketio_handler import SocketIOHandler
except:
    root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    print('root_path: ' + root_path)  # root_path = auto_test
    sys.path.insert(0, os.path.join(root_path, ".."))
    from auto_test.start_l1.connections.connection import _COM
    from auto_test.lib_service.log_handler.socketio_handler import SocketIOHandler


class SerialLog(object):
    """port: COM port number, like "COM7"
    log_path: absolute file path
    """

    def __init__(self, port: str, log_path=None):
        self._running = True
        self._catchlog = False
        self.port = port
        self._init_log_file_path(log_path=log_path)

    def _init_log_file_path(self, log_path):
        root_path = os.path.dirname(os.path.realpath(__file__))
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        time_current = time.strftime("%Y%m%d%H%M%S")

        if log_path:
            self.log_file = os.path.join(log_path, f'SerialLog_{time_current}.log')
            self.file_handler = logging.FileHandler(filename=self.log_file)
        else:
            self.log_file = os.path.join(root_path, f'testings/MainTestResults/serialLog/SerialLog_{time_current}.log')
            self.file_handler = logging.FileHandler(filename=self.log_file)
        print("created logfile: " + time_current)
        self.file_handler.setFormatter(formatter)
        self.logger = logging.getLogger("serial_log")
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)
        server_url = "http://localhost:5000"
        event = "serial_message_event"
        socket_io_handler = SocketIOHandler(server_url, event)
        socket_io_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(socket_io_handler)

    def catch_log(self):
        self._catchlog = True
        print("catch log set to true!")

    def terminate(self):
        self._running = False
        print('terminate serial connection!')

    def run(self):
        COM = _COM(name="s", com_port=self.port, baudrate=115200, timeout=1)
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
                # self.logger.removeHandler(h)
            else:
                h.close()
                # self.logger.removeHandler(h)
        if not self._catchlog:
            os.remove(self.log_file)


if __name__ == "__main__":
    s = SerialLog(port="COM11")
    t1 = threading.Thread(target=s.run)
    t1.start()

    time.sleep(15)
    # s.catch_log()
    s.terminate()
    t1.join()
