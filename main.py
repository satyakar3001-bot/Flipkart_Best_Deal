from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys

import os
import subprocess

qtCreatorFile = "main1.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

_translate = QtCore.QCoreApplication.translate

class Start_Screen(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.search.clicked.connect(self.load_ps)
        self.change.clicked.connect(self.display)
        self.exit.clicked.connect(self.Exit_GUI)

    def display(self):
        # file_name = 'd.py'
        self.close()
        os.system('python d.py')
    
    def load_ps(self):
        comm = self.product.text()
        start_price = self.start_price.text()
        end_price = self.end_price.text()
        execute='python web.py'+' -i '+comm+' -j '+start_price+' -k '+end_price
        subprocess.call(execute,shell=True)
        self.close()
        os.system('python d.py')
    
    def Exit_GUI(self):
        sys.exit()

    
if __name__ == "__main__":
	
	start_screen = QtWidgets.QApplication(sys.argv)

	

	window = Start_Screen()
	window.show()

	sys.exit(start_screen.exec_())