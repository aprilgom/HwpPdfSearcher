import os

import win32com.client as win32
import win32gui

def startHWP():
    HWPObject = win32.gencache.EnsureDispatch('HWPFrame.HwpObject')
    hwnd = win32gui.FindWindow(None,'빈 문서 1 - 한글')
    HWPObject.RegisterModule('FilePathCheckDLL','FilePathCheckerModule')
    return HWPObject
def saveHWP(HWPObject,path):
    HWPObject.Open(path)
    HWPObject.HAction.GetDefault('FileSave',HWPObject.HParameterSet.HFileOpenSave.HSet)
    HWPObject.HParameterSet.HFileOpenSave.filename = path
    HWPObject.HParameterSet.HFileOpenSave.Format = 'HWP'
    HWPObject.HAction.Execute('FileSave',HWPObject.HParameterSet.HFileOpenSave.HSet)
def saveHWPasPDF(HWPObject,path):
    HWPObject.Open(path)
    HWPObject.HAction.GetDefault('FileSaveAsPdf',HWPObject.HParameterSet.HFileOpenSave.HSet)
    pdfpath = path + ".pdf"
    HWPObject.HParameterSet.HFileOpenSave.filename = pdfpath
    HWPObject.HParameterSet.HFileOpenSave.Format = 'PDF'
    HWPObject.HAction.Execute('FileSaveAsPdf',HWPObject.HParameterSet.HFileOpenSave.HSet)
    return pdfpath
def quitHWP(HWPObject):
    HWPObject.XHwpDocuments.Close(isDirty=False)
    HWPObject.Quit()
    del HWPObject
