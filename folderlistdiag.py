from PyQt5.QtWidgets import *
from PyQt5 import uic
import indexer
import os

form_class = uic.loadUiType("folderlistdiag.ui")[0]

class FolderListDiag(QDialog, form_class):
    filelist = None
    pathlist = None
    def __init__(self):
        super().__init__()
        if os.path.isfile('filelist'):
            print("filelist exists")
            self.filelist = indexer.open_filelist()
            print("len : " + str(len(self.filelist)))
        else:
            print("filelist not exists")
            self.filelist = indexer.new_filelist() 
        if os.path.isfile('pathlist'):
            print("pathlist exists")
            self.pathlist = indexer.open_pathlist()
        else:
            print("pathlist not exists")
            self.pathlist = indexer.new_pathlist() 
       
        self.setupUi(self)
        for path in self.pathlist:
            self.folderlistBox.addItem(path)
        self.updateButton.clicked.connect(self.updateBtnFunction)
        self.addpathButton.clicked.connect(self.addpathBtnFunction)
        self.deleteButton.clicked.connect(self.deleteBtnFunction)
        
    def updateBtnFunction(self):
        #updaters = [
        #    "D:/판결문/판결문통합\\2000\\가,구\\1.완\\2000가단1370.hwp",
        #    "D:/판결문/판결문통합\\2009\\가,구\\2.잡,지방\\2009가합9680.HWP",
        #    "D:/판결문/판결문통합\\2010\\나,누\\2.잡,지방\\2010나93297.HWP",
        #    "D:/판결문/판결문통합\\2008\\가,구\\2.잡,지방\\2008가합1837.HWP",
        #    "D:/판결문/판결문통합\\2008\\가,구\\2.잡,지방\\2008가합6661.HWP",
        #    "D:/판결문/판결문통합\\2010\\가,구\\2.잡,지방\\2010구합28649.HWP",
        #    "D:/판결문/판결문통합\\2012\\가,구\\완\\2012가단105381.hwp"
        #]
        #indexer.index_specific(updaters,self.filelist)
        path = self.folderlistBox.currentItem().text()
        #indexer.verify_filelist(self.filelist)
        self.filelist = indexer.update_patch_conc(path,self.filelist,self.progressBar)
        indexer.write_filelist(self.filelist)

    def addpathBtnFunction(self):
        path = QFileDialog.getExistingDirectory(self,"폴더 지정","c:\\")
        if path != '':
            print(type(path))
            indexer.add_pathlist(path,self.pathlist)
            print("path added")
            self.filelist = indexer.add_patch_conc(path,self.filelist,self.progressBar)
            print("filelist updated")
            indexer.write_filelist(self.filelist)
            indexer.write_pathlist(self.pathlist)
        self.renewfolderBox()
    def deleteBtnFunction(self):
        path = self.folderlistBox.currentItem().text()
        indexer.delete_patch_conc(path,self.filelist,self.progressBar)
        print(len(self.filelist))
        indexer.write_filelist(self.filelist)
        indexer.delete_pathlist(path,self.pathlist)
        indexer.write_pathlist(self.pathlist)
        self.renewfolderBox()
        print(path)
    def renewfolderBox(self):
        self.folderlistBox.clear()
        for path in self.pathlist:
            self.folderlistBox.addItem(path)

