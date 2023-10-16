import indexer

soso,sl = indexer.make_pathtree("""C:\\Users\\aprilgom\\Desktop\\a""")

for pre, fill, node in indexer.RenderTree(soso):
    print("%s%s" %(pre,node.name))
print(sl)
