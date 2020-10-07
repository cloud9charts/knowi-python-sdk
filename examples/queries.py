from knowipy import Knowi

knowi = Knowi(clientId='<your Client ID here>', clientSecret='<your Client Secret here>')

# creates a query with the following properties
props = {
    "runNow": True,
    "c9QLFilter": "select * limit 10",
    "categories": [247],
    "queryStr": "db['restaurants'].find().limit(10000)",
    "description": "add query description, i.e., -- query calculates monthly restaurant sales"
}
create_query = knowi.query_create(datasourceId=1425, queryName='sales', queryProperty=props)

print(create_query)

# refresh an existing query to retrieve new data
run_query = knowi.query_refresh(queryId=2026)
print(run_query)

# list queries belonging to a category
list_query = knowi.query_list(categories=[123, 423])
print(list_query)

# create a new REST API query using an existing datasource
rest_props = {
    "runNow": True,
    "headers": "Authorization: Bearer {token}",
    "urlParams": "ba=CAISO_SP15&style=all&starttime={$c9_today:yyyyMMdd}",
    "direct": True,
    "endPoint": "/data/6cda4330"

}

api_query = knowi.query_create(queryName="rest query", queryProperty=rest_props, datasourceId=1447)
print(api_query)
