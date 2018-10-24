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

def el_search(query, data, host, init, wc=False):
	es = Elasticsearch(hosts=[host])
	df = pd.read_csv(data, encoding="utf8")

	if init:
		s = time.time()
		init_es(df.head(init), host)
		print(time.time() - s)

	q = {
			"query": {
				"match": {
					"title":"".join(query)
				}
			}
		}
	res = es.search(index="stackoverflow", doc_type="question", body=q)

	# Yield all results without including any code in the body.
	# Set include_code=True to include code. 
	results = output_results(res['hits']['hits'])
	i = 0
	try:
		shutil.rmtree('wordclouds')
	except OSError:
		pass
	os.makedirs('wordclouds')
	while True:
		try:
			r = results.__next__()
			print(r)
			if wc:
				make_word_cloud(r, i)
		except StopIteration:
			print('Oh sod it')
			break
		print('\n\n')
		i += 1


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

	el_search(args.query, args.d, args.H, args.i, args.w)