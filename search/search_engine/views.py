from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search(request):
	if request.POST:
		return render_to_response('search.html', {'result': get_correct_answers([request.POST['term']])})
	else:
		return render_to_response('search.html')


def get_correct_answers(term):
	thing = [['term', 245, 'how do I do this', 0.89], ['term', 245, 'how do I do this', 0.89]]
	return thing
