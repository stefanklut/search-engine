import itertools
import string
import pandas as pd
from pprint import pprint
from elasticsearch import Elasticsearch, helpers
from bs4 import BeautifulSoup
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import shutil
import os

# Delete ES data for windows:
# curl -X DELETE "http://localhost:9200/_all"


# es = Elasticsearch(hosts=["http://localhost:9200/"])

def el_search(query, data, host, init, minimum=None, date='', before=0, after=0, wc=False):
    es = Elasticsearch(hosts=[host])
    df = pd.read_csv(data, encoding="utf8")

    if init:
        init_es(df.head(init), host)

    q = {
            'query': {
                'bool': {
                    'should': [{'match': {'title': {'query': term, 'boost': 5}}} for term in query] + \
                              [{'match': {'body': {'query': term}}} for term in query],
                    'minimum_should_match': 1,
                    'filter': []
                }
            }
        }

    # add minimum stackoverflow score to query
    if minimum != None:
        q['query']['bool']['filter'] += [{'range': {'score' : {"gte" : minimum}}}]
    if date != '':
        if before and not after:
            q['query']['bool']['filter'] += [{'range': {'date' : {"lte" : date}}}]
        if after and not before:
            q['query']['bool']['filter'] += [{'range': {'date' : {"gte" : date}}}]
    print(q)

    res = es.search(index="stackoverflow", doc_type="question", body=q)
    res = res['hits']['hits']
    #pprint(res)

    # Yield all results without including any code in the body.
    # Set include_code=True to include code. 
    result_strings = output_results(res)
    i = 0
    try:
        shutil.rmtree('wordclouds')
    except OSError:
        pass
    os.makedirs('wordclouds')
    while True:
        try:
            r = result_strings.__next__()
            # print('\n\n')
            # print(r)
            if wc:
                make_word_cloud(r, i)
        except StopIteration:
            break
        i += 1

    results = get_results(res)
    top = []
    while True:
        try:
            top.append(results.__next__())
        except StopIteration:
            break
    return top


def init_es(df, host):
    es = Elasticsearch(hosts=[host])

    _index = "stackoverflow"
    _type = "question"

    # Add index
    if not es.indices.exists(index=_index):
        es.indices.create(_index)

    for col_id,x in df.iterrows():
        b = {"id":x["Id"], "title":x["Title"], "body":x["Body"], "score":x["Score"], "date": x["CreationDate"]}
        es.index(index=_index, doc_type=_type, id=col_id, body=b)

    
def output_results(res, include_code=False):
    for item in res:
        result_string = ''
        question = item['_source']
        qb = question['body']
        result_string += question['title'] + '\t' + str(question['id']) + '\n'

        while (not include_code) and '<code>' in qb:
            # Remove all code from the body of the question (optional)
            qb = qb[:qb.find('<code>')]+qb[qb.find('</code>')+7:]

        # Remove all html tags from the body
        result_string += BeautifulSoup(qb, "html.parser").text
        yield(result_string)


def get_results(res, include_code=False):
    for item in res:
        question = item['_source']

        result_string = question['title'] + '\t' + str(question['id']) + '\n'
        qb = question['body']
        while (not include_code) and '<code>' in qb:
            # Remove all code from the body of the question (optional)
            qb = qb[:qb.find('<code>')]+qb[qb.find('</code>')+7:]

        # Remove all html tags from the body
        result_string += BeautifulSoup(qb, "html.parser").text

        web_id = 'https://stackoverflow.com/questions/' + str(question['id'])
        yield({'title':question['title'], 'id': web_id, 'description': result_string, 'question_date': question['date'][:10]})


def make_word_cloud(question, i):
    wc = WordCloud().generate(question)
    plt.imshow(wc)
    plt.axis('off')
    plt.savefig('wordclouds/' + str(i) + '.png')


if __name__=="__main__":
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("query", metavar="N", type=str, nargs="+",
                   help="an integer for the accumulator")
    p.add_argument("-d", help="dataframe for stackoverflow questions",
                   default="data/Questions.csv", type=str)
    p.add_argument("-H", help="search engine host", \
                   default="http://localhost:9200/", type=str)
    p.add_argument("-i", help="init elastic search", \
                   default=0, type=int)
    p.add_argument("-w", help="show word cloud of questions", \
                   default=False, type=bool)
    args = p.parse_args(sys.argv[1:])

    el_search(args.query, args.d, args.H, args.i, 10, date='2018-10-26', before=0, after=1, wc=args.w)