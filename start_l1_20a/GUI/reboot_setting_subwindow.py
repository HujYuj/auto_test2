# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'reboot_setting_subwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(527, 407)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(70, 80, 68, 19))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(70, 130, 68, 19))
        self.label_2.setObjectName("label_2")
        self.made_ip1 = QtWidgets.QLineEdit(Dialog)
        self.made_ip1.setGeometry(QtCore.QRect(160, 80, 161, 25))
        self.made_ip1.setObjectName("made_ip1")
        self.made_ip2 = QtWidgets.QLineEdit(Dialog)
        self.made_ip2.setGeometry(QtCore.QRect(160, 130, 161, 25))
        self.made_ip2.setObjectName("made_ip2")
        self.save_btn = QtWidgets.QPushButton(Dialog)
        self.save_btn.setGeometry(QtCore.QRect(230, 250, 112, 34))
        self.save_btn.setObjectName("save_btn")
        self.reset_btn = QtWidgets.QPushButton(Dialog)
        self.reset_btn.setGeometry(QtCore.QRect(230, 300, 112, 34))
        self.reset_btn.setObjectName("reset_btn")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(70, 190, 81, 19))
        self.label_3.setObjectName("label_3")
        self.beamer_ip = QtWidgets.QLineEdit(Dialog)
        self.beamer_ip.setGeometry(QtCore.QRect(160, 190, 161, 25))
        self.beamer_ip.setObjectName("beamer_ip")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "made ip1"))
        self.label_2.setText(_translate("Dialog", "made ip2"))
        self.save_btn.setText(_translate("Dialog", "save"))
        self.reset_btn.setText(_translate("Dialog", "reset"))
        self.label_3.setText(_translate("Dialog", "beamer ip"))

