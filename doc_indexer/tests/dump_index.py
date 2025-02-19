from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import sys
import json



if __name__=="__main__":
    index_dir = 'whoosh_doc_index'
    ix = open_dir(index_dir)
    for i in ix.searcher().documents():
        print(i)
