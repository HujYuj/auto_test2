from PyQt5.QtWidgets import *
import sys

class GroupBox(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle("GroupBox")
        layout = QGridLayout()
        self.setLayout(layout)

        groupbox = QGroupBox("Reboot stree test")
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        
        vbox = QVBoxLayout()
        groupbox.setLayout(vbox)

        checkbutton = QCheckBox("Ping DUTs")
        vbox.addWidget(checkbutton)
        
        checkbutton = QCheckBox("Check Testability")
        vbox.addWidget(checkbutton)

        checkbutton = QCheckBox("Check UOAM")
        vbox.addWidget(checkbutton)

        
        
app = QApplication(sys.argv)
screen = GroupBox()
screen.show()
sys.exit(app.exec_())