from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from . import database

def post_detail(request):
    results = database.deb_get_post_analysis_comments('RealDictCursor')
    data = {}
    if results:
      data = results
    else:
      data = {'post': 'No Data'}
    return render(request, 'posts/post_detail.html', {'data': data})

def row_counts(request):
    """Get row counts
    """
  
    sql_query = """
                WITH tbl AS (
                             SELECT table_schema, table_name
                             FROM information_schema.tables
                             WHERE table_name NOT LIKE 'pg_%' AND table_schema IN ('public')
                            )
                SELECT
                  table_name,
                  (xpath('/row/c/text()',
                  query_to_xml(format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name),
                  false,
                  true,
                  '')))[1]::text::int AS rows_n
                FROM tbl ORDER BY 2 DESC;
                """
    results = database.get_select_query_result_dicts(sql_query)
    return render(request, 'posts/database_counts.html', {'data': results})
