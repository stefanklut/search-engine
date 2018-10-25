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
from collections import defaultdict
import numpy as np

# Delete ES data for windows:
# curl -X DELETE "http://localhost:9200/_all"


# es = Elasticsearch(hosts=["http://localhost:9200/"])

def el_search(query, data, host, init, minimum=None, date='', before=0, after=0, wc=False):
    es = Elasticsearch(hosts=[host])
    df = pd.read_csv(data, encoding="utf8")

    if init:
        init_es(df.head(init), host)

    # ! title=hond and body=cat or period=2009
    q = process_query(query)

    # add minimum stackoverflow score to query
    if minimum != None:
        q['query']['bool']['filter'] += [{'range': {'score' : {"gte" : minimum}}}]
    if date != '':
        if before and not after:
            q['query']['bool']['filter'] += [{'range': {'date' : {"lte" : date}}}]
        if after and not before:
            q['query']['bool']['filter'] += [{'range': {'date' : {"gte" : date}}}]

    res = es.search(index="stackoverflow", doc_type="question", body=q)
    res = res['hits']['hits']

    # Yield all results without including any code in the body.
    # Set include_code=True to include code.
    result_strings = output_results(res)
    make_word_cloud(' '.join([i for i in output_results(res)]))

    results = get_results(res)

    returned_results = []
    timeline = defaultdict(int)
    while True:
        try:
            n = results.__next__()
            returned_results.append(n)
            timeline[n['question_date'][:4]] += 1
        except StopIteration:
            break

    x = sorted(dict(timeline).keys())
    y = [timeline[i] for i in x]
    y_pos = np.arange(len(x))
    plt.figure()
    plt.bar(y_pos, y, align='center', alpha=0.5)
    plt.xticks(y_pos, x)
    plotquery = ' '.join(query) if len(' '.join(query)) < 40 else ' '.join(query)[:37] + '...'
    plt.ylabel(plotquery)
    plt.title('Year')
    plt.bar(x,y)
    plt.savefig('media/timeline.jpg')
    return returned_results


def process_query(query):
    if query[0] != '?':
        q = {
                'size' : 20,
                'query': {
                    'bool': {
                        'should': [{'match': {'title': {'query': term, 'boost': 5}}} for term in query] + \
                                  [{'match': {'body': {'query': term}}} for term in query],
                        'minimum_should_match': 1,
                        'filter': []
                    }
                }
            }
        return q
    q = {
            'size' : 20,
            'query': {
                'bool': {
                    'must': [],
                    'must_not': [],
                    'filter': []
                }
            }
        }

    for item in query[1:]:
        if len(item.split('=')) != 2:
            continue
        k,v = item.split('=')
        if k == 'title' or k == 'body':
            q['query']['bool']['must'] += [{'match': {k: v}}]
        elif k == '!title' or k == '!body':
            q['query']['bool']['must_not'] += [{'match': {k[1:]: v}}]
        elif k == 'year':
            q['query']['bool']['filter'] += [{'range': {'date' : {'gte' : v+'-01-01', 'lte': v+'-12-31'}}}]
        elif k == '!year':
            q['query']['bool']['filter'] += [{'range': {'date' : {'lte' : v+'-01-01', 'gte': v+'-12-31'}}}]
    return q



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
        question = item['_source']
        qb = question['body']
        result_string = question['title'] + '\n'

        while (not include_code) and '<code>' in qb:
            # Remove all code from the body of the question (optional)
            qb = qb[:qb.find('<code>')]+qb[qb.find('</code>')+7:]

        # Remove all html tags from the body
        result_string += BeautifulSoup(qb, "html.parser").text
        yield(result_string)


def get_results(res, include_code=False):
    for item in res:
        question = item['_source']

        qb = question['body']
        while (not include_code) and '<code>' in qb:
            # Remove all code from the body of the question (optional)
            qb = qb[:qb.find('<code>')]+qb[qb.find('</code>')+7:]

        # Remove all html tags from the body
        result_string = BeautifulSoup(qb, "html.parser").text
        if len(result_string) > 400:
            result_string = result_string[:400] + '...'

        web_id = 'https://stackoverflow.com/questions/' + str(question['id'])
        date = question['date'][:10]
        yield({'title':question['title'], 'id': web_id, 'description': result_string, 'question_date': date, 'score': question['score']})


def make_word_cloud(question):
    wc = WordCloud(width=1600, height=900, background_color=None, mode='RGBA').generate(question)
    plt.figure(figsize=(16,9), facecolor='k')
    plt.imshow(wc)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig('media/wordcloud.jpg')
    

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

    el_search(args.query, args.d, args.H, args.i, wc=args.w)
