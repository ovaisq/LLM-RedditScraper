from django.shortcuts import render
from . import database

def post_detail(request):
    results = database.deb_get_post_analysis_comments('RealDictCursor')
    data = {}
    if results:
      data = results
    else:
      data = {'post': 'No Data'}
    return render(request, 'posts/post_detail.html', {'data': data})

