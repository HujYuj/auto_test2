import sys
import os
import traceback
import logging

root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# print('root_path: ' + root_path) # root_path = tools_dev
sys.path.insert(0, os.path.join(root_path, ".."))
# print('sys_path: ', sys.path) # add dut_control to system path
# from checkDUTStatus import DUT_Status
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import threading
import main_window
import settings_subwindow
from tools_dev.start import PreVerification

# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets
from PyQt5 import QtCore



class WorkerSignals(QObject):
    """
    defined the signals available from a running working thread
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Worker(QRunnable):
    """
    Worker Thread
    """

    def __init__(self, fn, para1, para2):
        super(Worker, self).__init__()

        self.fn = fn
        self.para1 = para1
        self.para2 = para2
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs
        """
        try:
            result = self.fn(self.para1, self.para2)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class QTextEditorLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class Main_Window(QMainWindow, main_window.Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.show()

        # self.log_window = QTextEditorLogger(self)
        # self.log_window.setLevel(logging.DEBUG)
        # self.log_window.widget.setGeometry(QtCore.QRect(440, 220, 631, 601))
        # self.log_window.widget.setObjectName("log_window")
        self.logger = logging.getLogger("main")
        self.log_window.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
        self.logger.addHandler(self.log_window)
        self.threadpool = QThreadPool()
        self.cv = threading.Condition()
        self.settings_subwindow = settings_subwindow_Dialog()
        self.settings_btn.clicked.connect(self.settings_subwindow.show)
        self.settings_subwindow.settings_signal.settings.connect(self.get_setting_data)

    def get_setting_data(self, dict):
        self.setting_data = dict

    def get_test_options(self):
        self.test_options = {'CycleTimes': int(self.cycle_time.text()), 'CpriFlag': self.cpri_sync.isChecked(),
                             'CpriRepeatTimes': int(self.cpri_sync_read.text()),
                             'JesdFlag': self.jesd.isChecked(), 'JesdRepeatTimes': int(self.jesd_read.text()), 'UdpcpFlag': self.udhcp.isChecked(),
                             'SoapFlag': self.soap_msg.isChecked(), 'DpdinFlag': self.power.isChecked(), 'DpdinRepeatTimes':int(self.power_read.text())}

    @pyqtSlot()
    def on_start_test_clicked(self):
        self.get_test_options()
        self.preVerification = PreVerification(self.cv)
        worker = Worker(self.preVerification.start, self.setting_data, self.test_options)
        worker.signals.result.connect(self.print_log)
        worker.signals.finished.connect(self.thread_complete)

        self.threadpool.start(worker)

    @pyqtSlot()
    def on_pause_clicked(self):
        print("pause clicked!")
        self.preVerification.set_pause_flag()

    @pyqtSlot()
    def on_resume_clicked(self):
        print("resume clicked!")
        self.preVerification.set_resume_flag()
        with self.cv:
            self.cv.notify_all()
            print("wake thread")

    def print_log(self, s):
        print(s)

    def thread_complete(self):
        print("THRAD COMPLETE")


class SubwindowCommunication(QObject):
    settings = pyqtSignal(dict)


class settings_subwindow_Dialog(QDialog, settings_subwindow.Ui_Dialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.settings_signal = SubwindowCommunication()

    @pyqtSlot()
    def on_save_btn_clicked(self):
        settings_data = self.get_settings_data()
        self.settings_signal.settings.emit(settings_data)

    def get_settings_data(self):
        settings_data = {'made_num': int(self.made_num.currentText()), 'str_rru_mode': self.rru_mode.currentText(), 'str_dl_mode': self.tm.currentText(),
                         'str_bandwidth': self.band_width.text(), 'str_power': self.power.text(), 'str_frequency': self.frequency.text(),
                         'str_pusch_rb_offset': self.pusch_rb_offset.text(),
                         'str_pdsch_power_backoff': self.pdsch_power_backoff.text(), 'str_ul_mode': self.ul_mode.currentText(),
                         'str_test_type': self.test_type.currentText(), 'bool_auto_gen': True if self.auto_gen.currentText() == 'True' else False}
        for key in settings_data.keys():
            print(key, settings_data[key])
            print(type(settings_data[key]))
        return settings_data

    @pyqtSlot()
    def on_reset_btn_clicked(self):
        pass
        # self.made_ip2.setText('')
        # self.beamer_ip.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 实例化主窗口
    main_window = Main_Window()

    # 实例化子窗口
    # reboot_setting_dialog = reboot_setting_subwindow_Dialog()
    # link_setting_dialog = link_setting_subwindow_Dialog()
    #
    # #绑定按钮事件
    # reboot_setting_btn = main_window.reboot_settings
    # reboot_setting_btn.clicked.connect(reboot_setting_dialog.show)
    #
    # link_setting_btn = main_window.link_settings
    # link_setting_btn.clicked.connect(link_setting_dialog.show)

    # 显示
    sys.exit(app.exec_())
