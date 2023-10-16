import indexer

soso,sl = indexer.make_pathtree("""sample_data""")

for pre, fill, node in indexer.RenderTree(soso):
    print("%s%s" %(pre,node.name))
print(sl)
