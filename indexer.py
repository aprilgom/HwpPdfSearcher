from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError,NotFoundError
from concurrent.futures import ProcessPoolExecutor,as_completed
from PyQt5.QtCore import pyqtSignal,QObject
import multiprocessing
from anytree import Node,RenderTree
import subprocess
import zlib
import pickle
import os
from travel import rpath
import copy
import hgulsave as hgsave


def read_pdf_PDFMINER(pdf_file_path):

    output_string = StringIO()
    with open(pdf_file_path, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return str(output_string.getvalue())

def read_hwp(path):
    args = ['hwp5txt',path]
    ret = None
    h2cpdf = False
    try:
        ret = subprocess.check_output(args)
        ret = ret.decode('utf-8')
    except Exception as e:
        print(e)
        print(path + " read failed")
        h2cpdf = True
    if ret != None and len(ret) == 0:
        print(path + " read failed len0")
        h2cpdf = True
    print(h2cpdf)
    if h2cpdf == True:
        try:
            print("convert started")
            hwp = hgsave.startHWP()
            pdfpath = hgsave.saveHWPasPDF(hwp,path)
            hgsave.quitHWP(hwp)
            ret = read_pdf_PDFMINER(pdfpath)
            print("convert success")
            os.remove(pdfpath)
        except Exception as e:
            print(path + " pdf conversion failed")
            print(e)
    return ret
    
def insert_index(path,content):
    es = Elasticsearch('127.0.0.1:9200')
    content_sprm = content.replace(" ","")
    content_sprm = content_sprm.replace("\n","")
    doc = {
       "contents" : content, 
       "contents_spremoved" : content_sprm
    }
    for i in range(100):
        try:
            es.index(index="hwpnpdf", doc_type="_doc", body=doc,id=path)
        except TransportError as te:
            print(te)
            print(path + " transport error.")
            flush_index()
        except Exception as e:
            print(e)
            print(path + "error")
        else:
            break


def delete_index(path):
    es = Elasticsearch('127.0.0.1:9200')
    successed = False
    while successed == False:
        try:
            es.delete(index="hwpnpdf",id=path)
            successed = True
        except NotFoundError as nfe:
            print(nfe)
            print(path + " not exists in elasticsearch")
            successed = True
        except Exception as e:
            print(e)
            print(path + " delete failed")


def flush_index():
    es = Elasticsearch('127.0.0.1:9200')
    es.flush(index="hwpnpdf")

def search_index(keyword,spopt,extopt,lcopt):
    es = Elasticsearch('127.0.0.1:9200')
    keywords = keyword.split(' ')
    print(keywords)
    bools = []
    for k in keywords:
        query = {
            extopt:{
                spopt:k
            }
        }
        bools.append(query)
    doc = {
        "_source":["_id"],
        "query":{
            "bool":{
                lcopt:bools
            }
        },
        "size":10000
    } 
    result = es.search(index="hwpnpdf", body=doc)
    result = result['hits']['hits']
    res = []
    for strt in result:
        res.append(strt['_id'])
    return res

def search_exact_index(keyword,option):
    es = Elasticsearch('127.0.0.1:9200')
    doc = {
        "_source":["_id"],
        "query":{
            "term":{
                option:keyword
            }
        },
        "size":10000
    }
    result = es.search(index="hwpnpdf", body=doc)
    result = result['hits']['hits']
    res = []
    for strt in result:
        res.append(strt['_id'])
    return res

def parse_content(path):
    
    extension = os.path.splitext(path)[1]
    extension = extension.lower()
    content = 0
    if extension == '.hwp': 
        content = read_hwp(path) 
        content = content.decode('utf-8')
    elif extension == '.pdf':
        content = read_pdf_PDFMINER(path)
    content = content.replace(" ","")
    content = content.replace("\n","")
    return content

def insert_doc_index(path):
    extension = os.path.splitext(path)[1]
    extension = extension.lower()
    content = 0
    if extension == '.hwp': 
        content = read_hwp(path) 
    elif extension == '.pdf':
        content = read_pdf_PDFMINER(path)
    insert_index(path,content)


#def make_filelist(path):
#    filepathes = rpath(path)
#    filelist = {}
#    for filepath in filepathes:
#        crc = 0
#        if os.path.isfile(filepath):
#            with open(filepath,"rb") as f:
#                crc = zlib.crc32(f.read())
#        filelist[filepath] = crc
#    return filelist
def make_filelist(path):
    pool = ProcessPoolExecutor(max_workers=16)
    filepathes = rpath(path)
    filelist = {}
    futures = []
    for filepath in filepathes:
        future = pool.submit(getcrc,filepath)
        futures.append(future)
    for future in as_completed(futures):
        res = future.result()
        if res[1] == 0:
            print(res[0] + " failed")
        filelist[res[0]] = res[1]
    return filelist

def getcrc(path):
    crc = 0
    if os.path.isfile(path):
        with open(path,"rb") as f:
            crc = zlib.crc32(f.read())
    return (path,crc)

def new_filelist():
    filelist = {} 
    with open('filelist','wb') as f:
        pickle.dump(filelist,f)
    return filelist

def write_filelist(filelist):
    with open('filelist','wb') as f:
        pickle.dump(filelist,f)

def open_filelist():
    with open('filelist','rb') as f:
        filelist = pickle.load(f)
    return filelist

def add_filelist(path,filelist):
    updatelist = []
    deletelist = []
    old_filelist = copy.deepcopy(filelist)
    new_filelist = make_filelist(path)
    old_filelist.update(new_filelist)
    new_filelist = old_filelist
    print("oldfilelist_len:" + str(len(filelist)))
    print("newfilelist_len:" + str(len(new_filelist)))
    for k,v in new_filelist.items():
        try:
            if filelist[k] != v:
                updatelist.append(k)
        except:
            updatelist.append(k)
    print("updatelist_len:" + str(len(updatelist)))
    return new_filelist,updatelist,deletelist

def update_filelist(path,filelist):
    updatelist = []
    deletelist = []
    print("making new filelist...")
    new_filelist = make_filelist(path)
    print("done")
    renewed_filelist = copy.deepcopy(filelist)
    print("comparing with old one")
    for k,v in new_filelist.items():
        try:
            if filelist[k] != v:
                renewed_filelist[k] = v
                updatelist.append(k)
        except:
            renewed_filelist[k] = v
            updatelist.append(k)
    for k,v in filelist.items():
        if path in k:
            if k not in new_filelist:
                deletelist.append(k)
                del renewed_filelist[k]
    return renewed_filelist,updatelist,deletelist

def search_n_fill(path):
    extension = os.path.splitext(path)[1]
    extension = extension.lower()
    if extension == '.pdf':
        return True
    try:
        content = read_hwp(path)
    except Exception as ex:
        print(path+ " is wrong, read failed",ex)
        return False
    if len(content) == 0:
        print(path+ " is wrong, content length 0")
        return False
    return True

def index_specific(splist,filelist):
    for sppath in splist:
        if os.path.isfile(sppath):
            with open(sppath, "rb") as f:
                crc = zlib.crc32(f.read())
        filelist[sppath] = crc
        insert_doc_index(sppath)

    write_filelist(filelist)


def verify_filelist(filelist):
    pool = ProcessPoolExecutor(max_workers = 16)
    pool.map(search_n_fill,filelist)

class pgr_setter(QObject):
    m = None
    lock = None
    pgi = 0
    signal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        m = multiprocessing.Manager()
        self.lock = m.Lock()
    def init_pgr(self,progress):
        self.signal.connect(progress.setValue)
    def update(self):
        self.lock.acquire()
        self.pgi += 1
        try:
            #self.pg.setValue(self.pgi)
            self.signal.emit(self.pgi)
        except Exception as e:
            print(e)
        self.lock.release()

def add_patch_conc(path,filelist,progress):
    new_filelist,updatelist,deletelist = add_filelist(path,filelist)
    pool = ProcessPoolExecutor(max_workers = 16)
    progress.setMaximum(len(updatelist))
    pgs = pgr_setter()
    pgs.init_pgr(progress)
    for upath in updatelist:
        future = pool.submit(insert_doc_index,upath)
        future.add_done_callback(lambda p: pgs.update())
    return new_filelist

def add_patch(path,filelist,progress):
    new_filelist,updatelist,deletelist = add_filelist(path,filelist)
    patch_len = len(updatelist) + len(deletelist)
    progress.setMaximum(patch_len)
    for i in range(len(updatelist)):
        try:
            path = updatelist[i]
            insert_doc_index(path)
            progress.setValue(i+1)
            print("inserted "+path)
        except TransportError:
            flush_index()
            print("flushed")
            i = i-1
            
    for i in range(len(deletelist)):
        path = deletelist[i]
        delete_index(path)
        progress.setValue(i+len(updatelist)+1)
        print("deleted" +path)
    return new_filelist

def update_patch(path,filelist,progress):
    #verify_filelist(filelist)
    new_filelist,updatelist,deletelist = update_filelist(path,filelist)
    patch_len = len(updatelist) + len(deletelist)
    if patch_len == 0:
        print("nothing to patch")
    progress.setMaximum(patch_len)
    for i in range(len(updatelist)):
        path = updatelist[i]
        insert_doc_index(path)
        progress.setValue(i+1)
        print("inserted "+path)
    for i in range(len(deletelist)):
        path = deletelist[i]
        delete_index(path)
        progress.setValue(i+len(updatelist)+1)
        print("deleted" +path)
    return new_filelist

def update_patch_conc(path,filelist,progress):
    new_filelist,updatelist,deletelist = update_filelist(path,filelist)
    pool = ProcessPoolExecutor(max_workers = 16)
    print("ul:"+str(len(updatelist)))
    for u in updatelist:
        print(u)
    print("dl:"+str(len(deletelist)))
    for d in deletelist:
        print(d)
    progress.setMaximum(len(updatelist)+len(deletelist))
    pgs = pgr_setter()
    pgs.init_pgr(progress)
    for upath in updatelist:
        future = pool.submit(insert_doc_index,upath)
        future.add_done_callback(lambda p: pgs.update())
    for upath in deletelist:
        future = pool.submit(delete_index,upath)
        future.add_done_callback(lambda p: pgs.update())
    return new_filelist

def delete_patch(path,filelist,progress):
    del_pathes = rpath(path)
    patch_len = len(del_pathes)
    progress.setMaximum(patch_len)
    for i in range(len(del_pathes)):
        k = del_pathes[i]
        del filelist[k]
        delete_index(k)
        progress.setValue(i+1)

def delete_patch_conc(path,filelist,progress):
    deletelist = rpath(path)
    pool = ProcessPoolExecutor(max_workers = 16)
    progress.setMaximum(len(deletelist))
    pgs = pgr_setter()
    pgs.init_pgr(progress)
    for upath in deletelist:
        future = pool.submit(delete_index,upath)
        future.add_done_callback(lambda p: pgs.update())
        del filelist[upath]

def write_pathlist(pathlist):
    with open('pathlist','wb') as f:
        pickle.dump(pathlist,f)

def open_pathlist():
    with open('pathlist','rb') as f:
        pathlist = pickle.load(f)
    return pathlist

def new_pathlist():
    pathlist = {}
    with open('pathlist','wb') as f:
        pickle.dump(pathlist,f)
    return pathlist

def add_pathlist(path,pathlist):
    isSubfolder = False
    isParent = False
    for exp,val in pathlist.items():
        if exp in path:
            isSubfolder = True
        if path in exp:
            isParent = True
            child = exp
        if isSubfolder or isParent:
            break
    if not isSubfolder and not isParent:
        pathlist[path] = path
    elif not isSubfolder and isParent:
        del pathlist[child]
        pathlist[path] = path

def make_pathtree(path,parent = None):
    if os.path.isdir(path) == False:
        return
    nodelist = []
    if parent == None:
        me = Node(path)
    else:
        me = Node(path, parent)
    nodelist.append(me)
    childs = os.listdir(path)
    for i in range(len(childs)):
        child_full_path = os.path.join(path,childs[i])
        if os.path.isdir(child_full_path) == True:
            cd,cdnl = make_pathtree(child_full_path,me)
            nodelist.extend(cdnl)
    return me,nodelist



def delete_pathlist(path,pathlist):
    del pathlist[path]



