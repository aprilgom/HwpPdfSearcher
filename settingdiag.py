import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
import os
import pickle

form_class = uic.loadUiType("settingdiag.ui")[0]

class SettingDiag(QDialog, form_class):
    setting = {}
    def __init__(self):
        super().__init__()
        if os.path.isfile('setting'):
            print("settingfile exists")
            with open('setting','rb') as f:
                self.setting = pickle.load(f)
        else:
            print("settingfile not exists")
            self.setting = {}
            self.setting['hwppath'] = ""
            self.setting['pdfpath'] = ""
            with open('setting','wb') as f:
                pickle.dump(self.setting,f) 
        self.setupUi(self)
        self.hwppushButton.clicked.connect(self.hwppathFunction)
        self.pdfpushButton.clicked.connect(self.pdfpathFunction)
        self.saveButton.clicked.connect(self.saveFunction)
        self.saveButton.clicked.connect(self.close)
        self.hwppathEdit.setText(self.setting['hwppath'])
        self.pdfpathEdit.setText(self.setting['pdfpath'])
    def hwppathFunction(self):
        text = QFileDialog.getOpenFileName(self,"파일 찾기","C:\\")
        print(text[0])
        self.setting['hwppath'] = text[0]
        self.hwppathEdit.setText(text[0])
    def pdfpathFunction(self):
        text = QFileDialog.getOpenFileName(self,"파일 찾기","C:\\")
        self.setting['pdfpath'] = text[0]
        self.pdfpathEdit.setText(text[0])
    def saveFunction(self):
        with open('setting','wb') as f:
            pickle.dump(self.setting,f)
