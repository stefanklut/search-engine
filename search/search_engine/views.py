from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import el_search

@csrf_exempt
def search(request):
	if request.POST and request.POST['query'] != "":
		return render_to_response('search.html', {'result': results(request.POST['query'])})
	else:
		return render_to_response('search.html')


def get_correct_answers(term):
	thing = [{'title': "term", 'id': 10000, 'description': "hello, uefhuiahuaefh uaja iod jawioj awid jiawjd uiawhi duhawuid hawuh duawh uiawdu hwu uawhd uiwahd uiawh uidhawui hdwaui huiahd"},
	{'title': term, 'id': 20202020, 'description': "whammy"}]
	return thing

def results(query):
	return el_search.el_search(query, 'data/Questions.csv', 'http://localhost:9200/', 0)
