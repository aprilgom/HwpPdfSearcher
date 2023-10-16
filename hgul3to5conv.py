import os
import hgulsave as hgsave
from travel import rpath

hwp = hgsave.startHWP()

filepathes = rpath("")//한글 버전 3 파일이 있는 위치
for filepath in filepathes:
    extension = os.path.splitext(filepath)[1]
    if  extension == '.hwp' or extension == '.HWP':
        print(filepath)
        hgsave.saveHWP(hwp,filepath)
hgsave.quitHWP(hwp)