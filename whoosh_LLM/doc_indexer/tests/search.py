from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import sys
import json



def query(ix, search_terms):
    query = QueryParser("content", ix.schema).parse(search_terms)
    return query

def search(searcher, query):
     search_res = []
     results = searcher.search(query, terms=True)
     for r in results:
         d = dict(r) | {"score": r.score}
         search_res.append(d)
     ord_search_res = sorted(search_res, key=lambda d: d['score'], reverse=True)
     return ord_search_res


if __name__=="__main__":
    index_dir = 'whoosh_doc_index'
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        res= search(searcher, query(ix, ' '.join(sys.argv[1:])))
    for i in res:
        print(i['title'], i['path'], i['score'], i['content'])
