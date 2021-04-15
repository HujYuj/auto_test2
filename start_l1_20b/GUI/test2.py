import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
  def setupUi(self, MainWindow):
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(800, 600)
    self.centralwidget = QtWidgets.QWidget(MainWindow)
    self.centralwidget.setObjectName("centralwidget")
    self.pushButton = QtWidgets.QPushButton(self.centralwidget)
    self.pushButton.setGeometry(QtCore.QRect(80, 90, 75, 23))
    self.pushButton.setObjectName("pushButton")
    MainWindow.setCentralWidget(self.centralwidget)
    self.retranslateUi(MainWindow)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)
  def retranslateUi(self, MainWindow):
    _translate = QtCore.QCoreApplication.translate
    MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
    self.pushButton.setText(_translate("MainWindow", "PushButton"))

class Ui_Dialog(object):
  def setupUi(self, Dialog):
    Dialog.setObjectName("Dialog")
    Dialog.resize(400, 300)
    self.pushButton = QtWidgets.QPushButton(Dialog)
    self.pushButton.setGeometry(QtCore.QRect(160, 100, 75, 23))
    self.pushButton.setObjectName("pushButton")
    Dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  #设置窗体总显示在最上面
    self.retranslateUi(Dialog)
    QtCore.QMetaObject.connectSlotsByName(Dialog)
  def retranslateUi(self, Dialog):
    _translate = QtCore.QCoreApplication.translate
    Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
    self.pushButton.setText(_translate("Dialog", "PushButton"))

 
if __name__ == '__main__':
  app = QApplication(sys.argv)
  #实例化主窗口 
  main = QMainWindow() 
  main_ui = Ui_MainWindow()
  main_ui.setupUi(main )
  #实例化子窗口 
  child = QDialog()      
  child_ui = Ui_Dialog()
  child_ui.setupUi(child)
   
  #按钮绑定事件
  btn = main_ui.pushButton
  btn.clicked.connect( child.show ) 
   
  #显示
  main.show()
  sys.exit(app.exec_())
