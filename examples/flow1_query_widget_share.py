"""
End to end example to:
    - create a query using an existing datasource,
    - create a pie chart widget from the query results, and
    - share widget to group of users with editables permissions
"""

import os

import dotenv

from knowipy import Knowi

dotenv.load_dotenv()

# load credentials from environment or update arguments
knowi = Knowi(clientId=os.getenv("KNOWI_ID"), clientSecret=os.getenv("KNOWI_SECRET"))

# query properties to a Mongo datasource and post-process with Cloud9QL
queryProps = {
    "queryStr":    "db['restaurants'].find().limit(1000)",
    "c9QLFilter":  "select borough, cuisine, grades limit 10; \n"
                   "select *, expand(grades);\n"
                   "select avg(score) as avg_score, borough group by borough;",
    "description": "a new query description, -- restaurant transactions"
}

# widget properties to create a pie chart
widgetProps = {
    "chart.type":           "pie",
    "chart.series.data":    "avg_score",
    "chart.legend.column":  "borough",
    "chart.primary.ylabel": "avg_score",
    "widget.footnote":      "avg restaurant score",
    "chart.percent":        "true"
}

# share properties to share to an existing group
shareProps = [{
    "type":         "groups",
    "access_level": 1,
    "id":           1007
}]

# create query
createQuery = knowi.query_create(datasourceId=1566, queryName='restaurant records', queryProperty=queryProps)['data']
print('***QUERY CREATED*** \n', createQuery, '\n')

# create widget
createWidget = knowi.widget_create(widgetName='restaurant score', widgetType=1,
                                   datasetId=createQuery['datasetId'],
                                   chartProps=widgetProps)['data']
print('***WIDGET CREATED AS PIE CHART*** \n', createWidget, '\n')

# share widget
shareWidget = knowi.widget_shareToUserGroups(widgetId=createWidget['id'], shareProperty=shareProps)
print('***WIDGET SHARED TO GROUP*** \n', createQuery, '\n')
