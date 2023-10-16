import os
from winreg import *

def set_registry():
    path = "Software\Hnc\HwpAutomation\Modules"
    key = None
    try:
        key = CreateKey(HKEY_CURRENT_USER,path)
    except Exception as e:
        print(e)
    try:
        reg_handle = ConnectRegistry(None,HKEY_CURRENT_USER)
        key = OpenKey(reg_handle, path, access=KEY_WRITE)
        SetValueEx(key, "FilePathCheckerModule",0, REG_SZ, os.getcwd() + "\\FilePathCheckerModule.dll")
        print(os.getcwd() + "\\FilePathCheckerModule.dll")
    except Exception as e:
        print(e)


