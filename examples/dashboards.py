from knowipy import Knowi
import dotenv
import os

# load credentials from environment variables
dotenv.load_dotenv()

k = Knowi(clientId=os.getenv('KNOWI_ID_PROD'), clientSecret=os.getenv('KNOWI_SECRET_PROD'))

# generate a secure share url with content filters
secure_share = k.dashboard_shareViaUrl(dashboardId=164945, shareType='secure',
                                       fullUrl=True,
                                       contentFilters=[
                                           {"fieldName": "employee_id", "values": "1242", "operator": "<"},
                                           {"fieldName": "region", "values": ["Canada", "Spain"], "operator": "="}
                                       ])

print(secure_share)

# clone an existing dashboard
clone_dash = k.dashboard_clone(dashboardId=133092, clonedName='fancy name')
print(clone_dash)
