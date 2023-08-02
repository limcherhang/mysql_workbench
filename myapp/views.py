from django.shortcuts import render
from django.db import connection

def show_tables(request, database_name):
    with connection.cursor() as cursor:
        cursor.execute(f"USE {database_name};")
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]

    return render(request, 'index.html', {"tables": tables})

def get_databases_with_tables():
    initial = ['information_schema', 'mysql', 'performance_schema', 'sys']
    databases_with_tables = {}

    with connection.cursor() as cursor:
        cursor.execute("SHOW DATABASES;")
        databases = [row[0] for row in cursor.fetchall() if row[0] not in initial]

        for db in databases:
            cursor.execute(f"USE {db};")
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
            databases_with_tables[db] = tables

    return databases_with_tables

def execute_query(request):
    result = None
    query = None
    databases_with_tables = get_databases_with_tables()

    if request.method == 'POST':
        query = request.POST.get('query', '')

        query_type = None
        if query.strip().lower().startswith('select'):
            query_type = "SELECT"
        elif query.strip().lower().startswith('insert'):
            query_type = "INSERT"
        elif query.strip().lower().startswith('delete'):
            query_type = "DELETE"
        else:
            query_type = "UNKNOWN"

        try:
            with connection.cursor() as cursor:
                if query_type in ("INSERT", "DELETE"):
                    cursor.execute(query)
                    if query_type == "INSERT":
                        result = [{"INSERT": "INSERT success"}]
                    else:
                        result = [{"DELETE": "DELETE success"}]
                elif query_type == "SELECT":
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    for res in result:
                        if res.get("date",""):
                            res["date"] = res['date'].strftime("%Y-%m-%d")
                else:
                    result = [{"Error": "unreadable query"}]
        except:
            result = [{"Error": "Query error, Please check your query"}]

    return render(request, 'index.html', {'query': query, 'result': result, 'databases_with_tables': databases_with_tables})
