from django.shortcuts import render
from . import database
results = database.db_get_post_n_analyzed_docs('1b0xd1e')
def post_detail(request):
    data = {}
    if results:
      data = results
    else:
      data = {'post': 'No Data'}
    return render(request, 'posts/post_detail.html', {'data': data})

