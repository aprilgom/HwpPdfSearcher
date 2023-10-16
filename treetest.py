import indexer
import os

sample_path = "sample_data"
if not os.path.isdir(sample_path):
    print("sample_data directory not found")
    raise SystemExit(0)

soso,sl = indexer.make_pathtree(sample_path)

for pre, fill, node in indexer.RenderTree(soso):
    print("%s%s" %(pre,node.name))
print(sl)
