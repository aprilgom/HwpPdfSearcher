from anytree import Node, RenderTree
import os
import zlib

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

def make_path_tree(rootNode,path):
    filenames = os.listdir(path)
    for filename in filenames:
        childPath = os.path.join(path,filename)
        if os.path.isfile(childPath)==True or os.listdir(childPath):
            crc = 0
            if os.path.isfile(childPath) == True:
                with open(childPath,"rb") as f:
                    crc = zlib.crc32(f.read()) 
            childNode = Node(filename,parent=rootNode,data = crc)
        if os.path.isdir(childPath) == True:
            make_path_tree(childNode,childPath)

def print_path_tree(rootNode):
    for row in RenderTree(rootNode):
        pre,fill,node = row
        print(f"{pre}{node.name}")

def split_path(path):
    splpath = list(os.path.split(path))
    if splpath[1]=='':
        splpath[0] = splpath[0].replace("/","")
        return [splpath[0]]
    ret = []
    ret.extend(split_path(splpath[0]))
    ret.append(splpath[1])
    return ret

def make_full_path_tree(path):
    pathlist = split_path(path)
    root = Node(pathlist[0],data = 0)
    nodelist = [root]
    for i in range(1,len(pathlist)):
        newNode = Node(pathlist[i],parent = nodelist[i-1])
        nodelist.append(newNode)
    make_path_tree(nodelist[len(nodelist)-1],path)
    return root

#def get_leaves_tree(root):


#def renew_path_tree(root,path):
    

print(split_path("C:/Users/aprilgom/Desktop/1998(3033)"))
root = make_full_path_tree("C:/Users/aprilgom/Desktop/1998(3033)")
print_path_tree(root)
print(root.path)