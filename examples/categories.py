from knowipy import Knowi

knowi = Knowi(clientId='<your Client ID here>', clientSecret='<your Client Secret here>', flag='mgmt')

# create widget category
category = knowi.category_create(assetType=2, parentId=0, name='Regional Sales')

# assign widget to category
assign_widget = knowi.category_assignCatToAsset(assetType=2, categoryIds=[3, 7], assetId=28802)

# share widget category to group
group = [{"type": "groups", "access_level": 2, "id": 142}]
share_category = knowi.category_shareToUserGroups(assetType=2, categoryId=3, shareProperty=group)
knowi.query_refresh(queryId=1231)