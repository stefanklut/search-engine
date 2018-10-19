import itertools
import string
import pandas as pd
from pprint import pprint
from elasticsearch import Elasticsearch, helpers

# Delete ES data for windows:
# curl -X DELETE "http://localhost:9200/_all"


# es = Elasticsearch(hosts=["http://localhost:9200/"])

def el_search(query, data, host, init):
    es = Elasticsearch(hosts=[host])
    df = pd.read_csv(data, encoding="utf8")

    # print("q:", query)
    # print("d:", data)
    # print("h:", host)
    # print("i:", init)

    if init:
        import time
        s = time.time()
        init_es(df.head(1000), host)
        print(time.time() - s)

    # Creates a bulk, why would we though????
    # b = helpers.bulk(es, g)

    # print(b)

    q = {
            "query": {
                "match": {
                    "title":"".join(query)
                }
            }
        }
    res = es.search(index="stackoverflow", doc_type="question", body=q)
    # res = res["hits"]["hits"][0]["_source"]["id"]
    # pprint(res)


def generator(df, es):
    for col_id,x in df.iterrows():
        _index = "stackoverflow"
        _type = "question"
        _id = x["Id"]
        _title = x["Title"]
        _body = x["Body"]
        yield {"_index":_index, "_type":_type, "id":_id, "title":_title,
               "body":_body}


def init_es(df, host):
    es = Elasticsearch(hosts=[host])

    _index = "stackoverflow"
    _type = "question"

    # Add index
    if not es.indices.exists(index=_index):
        es.indices.create(_index)

    for col_id,x in df.iterrows():
        b = {"id":x["Id"], "title":x["Title"], "body":x["Body"]}
        es.index(index=_index, doc_type=_type, id=col_id, body=b)
    


if __name__=="__main__":
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("query", metavar="N", type=str, nargs="+",
                   help="an integer for the accumulator")
    p.add_argument("--d", help="dataframe for stackoverflow questions",
                   default="data/Questions.csv", type=str)
    p.add_argument("--h", help="search engine host", \
                   default="http://localhost:9200/", type=str)
    p.add_argument("--i", help="init elastic search", \
                   default=False, type=bool)
    args = p.parse_args(sys.argv[1:])

    el_search(args.query, args.d, args.h, args.i)
