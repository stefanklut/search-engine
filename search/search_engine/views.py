from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import el_search

@csrf_exempt
def search(request):
	if request.POST and request.POST['query'] != "":
		q = request.POST['query']
		s = 10 # score
		d = request.POST['date']
		b = request.POST['before']
		a = request.POST['after']
		return render_to_response('search.html', {'result': results(q, s, d, b, a)})
	else:
		return render_to_response('search.html')

def results(q, s, d, b, a):
	return el_search.el_search(q.split(), 'data/Questions.csv', 'http://localhost:9200/', 0, minimum=s, date=d, before=b, after=a)
