import signal
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import indexer
import settingdiag
import folderlistdiag
import os
import subprocess
import pickle
from elasticsearch import Elasticsearch
from multiprocessing import freeze_support
from time import sleep
import atexit
import rag

form_class = uic.loadUiType("window.ui")[0]
ld_form_class = uic.loadUiType("loadingdiag.ui")[0]
class LdWindow(QDialog,ld_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class MyWindow(QMainWindow, form_class):
    filelist = None
    pathlist = None
    setting = None
    def __init__(self):
        super().__init__()
        rag.set_registry()
        if os.path.isfile('filelist'):
            print("filelist exists")
            self.filelist = indexer.open_filelist()
        else:
            print("filelist not exists")
            self.filelist = indexer.new_filelist() 
        if os.path.isfile('pathlist'):
            print("pathlist exists")
            self.pathlist = indexer.open_pathlist()
        else:
            print("pathlist not exists")
            self.pathlist = indexer.new_pathlist() 
        if os.path.isfile('setting'):
            print("settingfile exists")
            with open('setting','rb') as f:
                self.setting = pickle.load(f)
        else:
            print("settingfile not exists")
            self.setting = {}
            with open('setting','wb') as f:
                pickle.dump(self.setting,f) 
        self.setupUi(self)
        self.searchButton.clicked.connect(self.searchBtnFunction)
        self.searchBoxEdit.returnPressed.connect(self.searchBtnFunction)
        self.settingButton.clicked.connect(self.settingBtnFunction)
        self.indexeditButton.clicked.connect(self.indexeditBtnFunction)
        self.searchResListBox.itemDoubleClicked.connect(self.pathOpenFunction)
    def pathOpenFunction(self):
        path = self.searchResListBox.currentItem().text()
        extension = os.path.splitext(path)[1].lower()
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        if extension == '.hwp': 
            subprocess.Popen(args=[self.setting['hwppath'],path],creationflags=DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP)
            #ptt = "\""+self.setting['hwppath']+"\""
            #os.system(ptt + " " + path)
        elif extension == '.pdf':
            subprocess.Popen(args=[self.setting['pdfpath'],path],creationflags=DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP)
            #subprocess.run(args=[self.setting['pdfpath'],path])

    def indexeditBtnFunction(self):
        dlg = folderlistdiag.FolderListDiag()
        dlg.exec_()
        
    def settingBtnFunction(self):
        dlg = settingdiag.SettingDiag()
        dlg.exec_()
        with open('setting','rb') as f:
            self.setting = pickle.load(f)
    def searchBtnFunction(self):
        self.searchResListBox.clear()
        spopt = "contents_spremoved"
        extopt = "match"
        lcopt = "must"
        if self.spcheckBox.isChecked():
            spopt = "contents_spremoved"
        else:
            spopt = "contents"
        if self.optcmplButton.isChecked():
            extopt = "term"
            #searchRes = indexer.search_exact_index(self.searchBoxEdit.text(),spopt)
        elif self.optpartialButton.isChecked():
            extopt = "match"
        if self.andradioButton.isChecked():
            lcopt = "must"
        elif self.orradioButton.isChecked():
            lcopt = "should"
        searchRes = indexer.search_index(self.searchBoxEdit.text(), spopt,extopt,lcopt)
        for path in searchRes:
            self.searchResListBox.addItem(path)


def quitproc(pid):
    print("quited")
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.call(['taskkill','/F','/T','/PID',str(pid)],startupinfo=si)


if __name__ == "__main__":
    freeze_support()
    print(os.getcwd())
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    proc = subprocess.Popen([".\\elasticsearch-7.8.1\\bin\\elasticsearch.bat"],startupinfo=si)
    atexit.register(quitproc,proc.pid)
    app = QApplication(sys.argv)
    ldWindow = LdWindow()
    ldWindow.show()
    loaded = False
    while not loaded:
        sleep(3)
        try:
            es = Elasticsearch('127.0.0.1:9200')
            health = es.cluster.health()['status']
            if health == 'yellow' or health == 'green':
                loaded = True
            print(es.cluster.health())
        except:
            loaded = False
            print("es connect error")

    ldWindow.close()
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()