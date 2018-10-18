import itertools
import string
import pandas as pd
from pprint import pprint
from elasticsearch import Elasticsearch, helpers

# Delete ES data for windows:
# curl -X DELETE "http://localhost:9200/_all"


# es = Elasticsearch(hosts=["http://localhost:9200/"])

def el_search(query, data, host):
    es = Elasticsearch(hosts=[args.h])
    df = pd.read_csv(data)

    g = generator(df.head(100), es)

    # Add index
    if not es.indices.exists(index="stackoverflow"):
        es.indices.create("stackoverflow")

    # Creates a bulk, why would we though????
    b = helpers.bulk(es, g)

    q = {
            "query": {
                "match": {
                    "title":query[0]
                }
            }
        }
    res = es.search(index="stackoverflow", doc_type="foo", body=q)
    pprint(res["hits"]["hits"])

def generator(data, es):
    for col_id,x in data.iterrows():
        _index = "stackoverflow"
        _type = "foo"
        _id = x["Id"]
        _title = x["Title"]
        _body = x["Body"]
        yield {"_index":_index, "_type":_type, "id":_id, "title":_title,
               "body":_body}
        q = {"id":_id, "title":_title, "body":_body}
        es.index(index="stackoverflow", doc_type="foo", id=col_id, body=q)

def process_query():
    pass

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
    args = p.parse_args(sys.argv[1:])

    el_search(args.query, args.d, args.h)
