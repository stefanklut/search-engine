from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search(request):
	if request.POST:
		print(request.POST['Capital'])
		return render_to_response('search.html', {'result': [request.POST['term']]})
	else:
		return render_to_response('search.html')
