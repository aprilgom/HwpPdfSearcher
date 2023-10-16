import os

def rpath(path):
    if os.path.isdir(path) == False:
        return
    filenames = os.listdir(path)
    result = []
    for i in range(len(filenames)):
        filenames[i] = os.path.join(path,filenames[i])
        if os.path.isfile(filenames[i]) == True:
            result.append(filenames[i])
        else:
            result.extend(rpath(filenames[i]))
    return result 

