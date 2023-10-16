#!c:\users\aprilgom\appdata\local\programs\python\python38\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pyhwp==0.1b15','console_scripts','hwp5txt'
__requires__ = 'pyhwp==0.1b15'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pyhwp==0.1b15', 'console_scripts', 'hwp5txt')()
    )
