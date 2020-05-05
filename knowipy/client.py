# Standard Imports
import json
from typing import Dict, List, Union

# Internal Imports
from knowipy.base_client import BaseClient, HTTPMethod
from knowipy.decorators import (
    validateCategoryAssets, validateQueryParams, validateShareParams, validateSubCustomer, validateUserParams)


class Knowi(BaseClient):
    """A WebClient allows apps to communicate with the Knowi Platform's API.

    The Knowi API is an interface for querying information from
    and enacting change in a Knowi workspace for Management API and Single Sign On (SSO) API.

    This client handles constructing and sending HTTP requests to Knowi
    as well as parsing any responses received.

    Attributes:
        clientId (str): A string specifying a Knowi client id.
        clientSecret (str): A string specifying a Knowi client secret.
        host (str): A string representing the Knowi API base URL.
            Default is 'https://www.knowi.com/'.
        flag (str): A string specifying which API to use. Options are `mgmt` or `sso`
                    Default is mgmt.


    Methods:
        api_call: Constructs a request and executes the API call to Knowi.

    Example of recommended usage:
    ```python
        import os
        from knowipy import Knowi

        client = Knowi(clientId=os.environ['KNOWI_CLIENT_ID'], clientSecret=os.environ['KNOWI_CLIENT_SECRET'])
        response = client.dashboard_create(
            dashboardName='sales and marketing')
    ```

    Note:
        Any attributes or methods prefixed with _underscores are
        intended to be "private" internal use only. They may be changed or
        removed at anytime.

    """

    # DASHBOARDS
    def dashboard_list(self, *, categories: List[int] = None, **kwargs):
        """List all dashboards in user account

        :param categories: (list) Show dashboards for particular category e.g. '[1411,1443]'

        """
        kwargs.update({"byCategory": categories})

        return self.api_call('/dashboards', HTTPMethod.GET, params=kwargs)

    def dashboard_getById(self, *, dashboardId: int, **kwargs):
        """Retrieve dashboard details by Id"""
        return self.api_call(f'/dashboards/{dashboardId}', HTTPMethod.GET, params=kwargs)

    def dashboard_listWidgetsInDashboard(self, *, dashboardId: int, **kwargs):
        return self.api_call(f'/dashboards/{dashboardId}/widgets', HTTPMethod.GET, params=kwargs)

    @validateShareParams
    def dashboard_shareToUserGroups(self, *, dashboardId: int, shareProperty: List[dict], **kwargs):
        """Share dashboard to user/groups

        :param dashboardId:
        :param shareProperty:
            [{"type": "Users", "access_level": 1, "name": "someUser1@host.com", "sso_user": false},
            {"type": "Groups", "access_level": 1, "id": 10001}]
        :param kwargs:
        :return:
        """

        kwargs.update({"shareProperties": shareProperty})

        return self.api_call(f'/dashboards/{dashboardId}/share', HTTPMethod.PUT, json=kwargs)

    def dashboard_clone(self, *, dashboardId: int, clonedName: str, **kwargs):
        """Clone existing dashboard to a new name

        :param dashboardId: (int) dashboard Id to be cloned e.g. 797901
        :param clonedName: (str) name for cloned dashboard e.g. 'New Dashboard'

        :param kwargs:
             :keyword screenWidth (int):
             :keyword screenHeight (int):
        """
        width = kwargs['screenWidth'] if "screenWidth" in kwargs else 1000
        height = kwargs['screenHeight'] if "screenWidth" in kwargs else 800

        kwargs.update({"dashName": clonedName, "screenWidth": width, "screenHeight": height})

        return self.api_call(f'/dashboards/{dashboardId}', HTTPMethod.POST, json=kwargs)

    def dashboard_delete(self, *, dashboardId: int, **kwargs):
        return self.api_call(f'/dashboards/{dashboardId}', HTTPMethod.DELETE, params=kwargs)

    def dashboard_create(self, *, dashboardName: Union[str, int], **kwargs):
        width = kwargs['screenWidth'] if "screenWidth" in kwargs else 1000
        height = kwargs['screenHeight'] if "screenWidth" in kwargs else 800

        kwargs.update({"dashName": dashboardName, "screenWidth": width, "screenHeight": height})

        return self.api_call('/dashboards', HTTPMethod.POST, json=kwargs)

    @validateUserParams
    def dashboard_shareViaUrl(self, *, dashboardId: int, shareType: str = 'simple', contentFilters: List[dict] = None,
                              fullUrl: bool = False, **kwargs):
        """Retrieve a dashboard share Url for simple and secure share. This changes the dashboard URL each time this
        endpoint is called.

        :param fullUrl: (bool) - True to return full asset Url with host and shareUrl
        :param contentFilters: (List[dict]) contentFilter to filter contents.
            [{"fieldName": "State", "values": ["AZ"], "operator": "="},
            {"fieldName": "Year", "values": [2016], "operator": "="}]
        :param dashboardId: (int) dashboard Id to share via Url
        :param shareType: (bool) If true a new shareUrl will be generated

        """
        # TODO: add _ttl and t for link expiry in epoch: expireIn=
        if shareType == 'simple':
            path = 'share/url'
        elif shareType == 'secure':
            path = 'share/url/secure'
        else:
            raise ValueError(f'invalid shareType={shareType}')

        kwargs.update({"contentFilters": json.dumps(contentFilters)})
        if fullUrl:
            fullRsp = self.api_call(f'/dashboards/{dashboardId}/{path}', HTTPMethod.POST, data=kwargs)

            if shareType == 'simple':
                fullRsp['fullUrl'] = self.host + '/d/' + fullRsp['data']['shareUrl']
                return fullRsp

            if shareType == 'secure':
                fullRsp['fullUrl'] = self.host + '/share/secure/' + fullRsp['data']['secureShareUrl']
                return fullRsp

        else:
            return self.api_call(f'/dashboards/{dashboardId}/{path}', HTTPMethod.POST, data=kwargs)

    @validateUserParams
    def dashboard_hashContentFilters(self, dashboardId: int, contentFilters: List[dict] = None, **kwargs):
        """ Generate a hash for a contentFilter without resetting or changing the dashboard URL

        :param dashboardId: (int) dashboard Id to generate hash for
        :param contentFilters: (List[dict]) contentFilter to filter contents.
            [{"fieldName": "State", "values": ["AZ"], "operator": "="},
            {"fieldName": "Year", "values": [2016], "operator": "="}]
        :param kwargs:
        :return:
        """

        kwargs.update({"contentFilters": json.dumps(contentFilters)})

        return self.api_call(f'/dashboards/{dashboardId}/share/url/secure/hash', HTTPMethod.POST, data=kwargs)

    def dashboard_exportToPDF(self, dashboardId: int, **kwargs):

        return self.api_call(f'/dashboards/{dashboardId}/export/pdf', HTTPMethod.GET, params=kwargs)

    def dashboard_edit(self, dashboardId: int, newName: Union[str, int], categories: List[int] = None, **kwargs):
        kwargs.update({"dashName": newName, "categories": [] if not categories else categories})

        return self.api_call(f'/dashboards/{dashboardId}', HTTPMethod.PUT, json=kwargs)

    def dashboard_listFilterSet(self, **kwargs):
        return self.api_call('/dashboards/filterset', HTTPMethod.GET, params=kwargs)

    @validateShareParams
    def dashboard_shareFilterSet(self, *, filterId: int, shareProperty: List[dict], **kwargs):
        kwargs.update({"shareProperties": shareProperty})

        return self.api_call(f'/dashboards/filterset/{filterId}/share', HTTPMethod.PUT, json=kwargs)

    def dashboard_deleteFilterSet(self, *, filterId: int, **kwargs):
        return self.api_call(f'/dashboards/filterset/{filterId}', HTTPMethod.DELETE, params=kwargs)

    # WIDGETS
    def widget_list(self, *, categories: List[int] = None, **kwargs):
        """List all widgets in user account

               :param categories: (list) Show widgets for particular category e.g. '[1411,1443]'

               """
        kwargs.update({"byCategory": categories})

        return self.api_call('/widgets', HTTPMethod.GET, params=kwargs)

    def widget_getById(self, *, widgetId: int, **kwargs):
        """Retrieve widget by an Id"""
        return self.api_call(f'/widgets/{widgetId}', HTTPMethod.GET, params=kwargs)

    @validateUserParams
    def widget_shareViaUrl(self, *, widgetId: int, shareType: str = 'simple', contentFilters: List[dict] = None,
                           fullUrl: bool = False, **kwargs):
        """Retrieve a widgets share Url for simple and secure share.

        :param fullUrl: (bool) - True to return full asset Url with host and shareUrl
        :param contentFilters: (List[dict]) contentFilter to filter contents.
            [{"fieldName": "State", "values": ["AZ"], "operator": "="},
            {"fieldName": "Year", "values": [2016], "operator": "="}]
        :param widgetId: (int) widget Id to share via Url
        :param shareType: (bool) If true a new shareUrl will be generated

        """
        if shareType == 'simple':
            path = 'share/url'
        elif shareType == 'secure':
            path = 'share/url/secure'
        else:
            raise ValueError(f'invalid shareType={shareType}')

        kwargs.update({"contentFilters": json.dumps(contentFilters)})

        if fullUrl:
            fullRsp = self.api_call(f'/widgets/{widgetId}/{path}', HTTPMethod.POST, data=kwargs)

            if shareType == 'simple':
                fullRsp['fullUrl'] = self.host + '/w/' + fullRsp['data']['shareUrl']
                return fullRsp
            if shareType == 'secure':
                fullRsp['fullUrl'] = self.host + '/w-secure/' + fullRsp['data']['secureShareUrl']
                return fullRsp

        else:
            return self.api_call(f'/widgets/{widgetId}/{path}', HTTPMethod.POST, data=kwargs)

    @validateShareParams
    def widget_shareToUserGroups(self, *, widgetId: int, shareProperty: List[dict], **kwargs):
        """ share widget to users/groups
        
        :param widgetId: widget id
        :param shareProperty: share properties
            [   
                  {
                    "type" : "Users",
                    "access_level" : 1,
                    "name" : "someUser1@host.com",
                    "sso_user": false
                  },
                  {
                    "type" : "Groups",
                    "access_level" : 1,
                    "id" : 10001
                  }
            ]
        :param kwargs: 
        :return: 
        """

        kwargs.update({"shareProperties": shareProperty})

        return self.api_call(f'/widgets/{widgetId}/share', HTTPMethod.PUT, json=kwargs)

    def widget_create(self, *, datasetId: int, widgetName: Union[str, int], widgetType: int = None,
                      chartProps: Dict = None, **kwargs):

        kwargs.update({"widgetName":      widgetName,
                       "datasetId":       datasetId,
                       "widgetType":      widgetType,
                       "chartProperties": chartProps
                       })

        return self.api_call('/widgets', HTTPMethod.POST, json=kwargs)

    def widget_clone(self, *, widgetId: int, newWidgetName: Union[str, int], **kwargs):
        kwargs.update({"widgetName": newWidgetName})

        return self.api_call(f'/widgets/{widgetId}', HTTPMethod.POST, json=kwargs)

    def widget_delete(self, *, widgetId: int, **kwargs):
        return self.api_call(f'/widgets/{widgetId}', HTTPMethod.DELETE, params=kwargs)

    def widget_edit(self, *, widgetId: int, categories: List[int] = None, widgetType: int = None,
                    chartProps: Dict = None, **kwargs):

        kwargs.update({"widgetName":      kwargs.get("widgetName"),
                       "categories":      [] if not categories else categories,
                       "widgetType":      widgetType,
                       "chartProperties": chartProps
                       })

        return self.api_call(f'/widgets/{widgetId}', HTTPMethod.PUT, json=kwargs)

    # DATASOURCES
    def datasource_list(self, **kwargs):
        return self.api_call('/datasources', HTTPMethod.GET, params=kwargs)

    def datasource_getById(self, *, datasourceId: int, **kwargs):
        return self.api_call(f'/datasources/{datasourceId}', HTTPMethod.GET, params=kwargs)

    # @validateDatasourceParams
    def datasource_create(self, **kwargs):
        """
        Create a new datasource
        :param kwargs:
        :return:
        """

        # TODO: Not yet implemented
        kwargs.update({
            "authEndPoint":      kwargs.get('authEndPoint'),  # restapi
            "authHeaders":       kwargs.get('authHeaders'),  # restapi
            "authPostPayload":   kwargs.get('authPostPayload'),  # restapi
            "authUrlParams":     kwargs.get('authUrlParams'),  # restapi
            "datasource":        kwargs.get('datasource'),
            "dataverse":         kwargs.get('dataverse'),  # couchbase analytics
            "dbName":            kwargs.get('dbName'),
            "host":              kwargs.get('host'),
            "name":              kwargs.get('name'),
            "password":          kwargs.get('password'),
            "port":              kwargs.get('port'),
            "privateConnector":  kwargs.get("privateConnector", None),  # if privateDatasource is true
            "privateDatasource": kwargs.get('privateDatasource', False),
            "tunnel":            kwargs.get("tunnel", False),
            "tunnelAddress":     kwargs.get("tunnelAddress"),  # if tunnel is true
            "url":               kwargs.get('url'),  # restapi/restHost
            "userId":            kwargs.get("userId"),  # user
            "version":           kwargs.get("version", "5.X.X")  # elastic ["Older Versions"]
        })

        # return self.api_call('/datasources', HTTPMethod.POST, json=kwargs)

        raise NotImplementedError

    # @validateDatasourceParams
    def datasource_edit(self, *, datasourceId: int, **kwargs):
        """
        Edit an existing datasource

        :param datasourceId:
        :param kwargs:
        :return:
        """
        # TODO: Not yet implemented
        # return self.api_call(f'/datasources/{datasourceId}', HTTPMethod.PUT, json=kwargs)

        raise NotImplementedError

    @validateShareParams
    def datasource_shareToUserGroups(self, *, datasourceId: int, shareProperty: List[dict],
                                     **kwargs):
        kwargs.update({"shareProperties": shareProperty})

        return self.api_call(f'/datasources/{datasourceId}/share', HTTPMethod.PUT, json=kwargs)

    def datasource_clone(self, *, datasourceId: int, clonedName, **kwargs):
        kwargs.update({"clonedQueryName": clonedName})

        return self.api_call(f'/datasources/{datasourceId}', HTTPMethod.POST, json=kwargs)

    def datasource_delete(self, *, datasourceId: int, **kwargs):

        return self.api_call(f'/datasources/{datasourceId}', HTTPMethod.DELETE, params=kwargs)

    # QUERIES
    def query_list(self, *, categories: List[int] = None, **kwargs):
        """List all dashboards in user account

        :param categories: (list) Show dashboards for particular category e.g. '[1411,1443]'

        """
        kwargs.update({"byCategory": categories})

        return self.api_call('/queries', HTTPMethod.GET, params=kwargs)

    def query_getById(self, *, queryId: int, withJoins: bool = False, **kwargs):
        """Get query details for a given query id

        :param queryId: (int) unique query id
        :param withJoins: (bool) Include datasources for query joins. Defaults to False.
        :param kwargs:
        :return:
        """

        kwargs.update({"loadJoinDataSources": withJoins})

        return self.api_call(f'/queries/{queryId}', HTTPMethod.GET, params=kwargs)

    def query_refresh(self, *, queryId: int, **kwargs):
        kwargs.update({"runNow": True})

        return self.api_call(f'/queries/{queryId}/refreshQuery', HTTPMethod.POST, json=kwargs)

    @validateQueryParams
    def query_create(self, *, datasourceId: int = None, queryName: str = None, queryProperty: dict = None, **kwargs):
        """ create a query using an existing datasource

        :param datasourceId: datasource ID
        :param queryName: name of query
        :param queryProperty: query properties
        :param kwargs:
        :return:
        """

        kwargs.update({
            "properties": {
                "c9QLFilter":      queryProperty.get("c9QLFilter", "select *"),
                "categories":      queryProperty.get("categories"),
                "datasourceId":    datasourceId,
                "description":     queryProperty.get("description"),
                "direct":          queryProperty.get("direct", False),
                "dsName":          queryProperty.get("dsName"),
                "entityName":      queryName,
                "queryStr":        str(queryProperty.get("queryStr")),
                "triggered":       queryProperty.get("triggered"),
                "overrideVals":    queryProperty.get("overrideVals", "All"),
                "c9ExportDataset": queryProperty.get("c9ExportDataset", None)  # for cloud9charts warehouse
            },
            "runNow":     queryProperty.get("runNow", True),
            "drafted":    queryProperty.get("drafted", None)
        })

        return self.api_call('/queries', HTTPMethod.POST, json=kwargs)

    @validateQueryParams
    def query_edit(self, *, queryId: int = None, datasourceId: int = None, queryProperty: dict = None, **kwargs):
        """ edit an existing query

        :param queryId: query ID to edit
        :param datasourceId: datasource ID for existing query
        :param queryProperty: query properties to update
        :param kwargs:
        :return:
        """
        kwargs.update({
            "properties": {
                "c9QLFilter":      queryProperty.get("c9QLFilter"),
                "categories":      queryProperty.get("categories"),
                "datasourceId":    datasourceId,
                "description":     queryProperty.get("description"),
                "direct":          queryProperty.get("direct"),
                "dsName":          queryProperty.get("dsName"),
                "entityName":      queryProperty.get("entityName"),
                "queryStr":        str(queryProperty.get("queryStr")),
                "triggered":       queryProperty.get("triggered"),
                "overrideVals":    queryProperty.get("overrideVals", "All"),
                "c9ExportDataset": queryProperty.get("c9ExportDataset")  # for cloud9charts warehouse
            },
            "runNow":     queryProperty.get("runNow", True),
            "drafted":    queryProperty.get("drafted")
        })

        return self.api_call(f'/queries/{queryId}', HTTPMethod.PUT, json=kwargs)

    def query_delete(self, *, queryId: int, removeWidgets: bool = False, **kwargs):
        kwargs.update({"removeWidgets": removeWidgets})

        return self.api_call(f'/queries/{queryId}', HTTPMethod.DELETE, params=kwargs)

    def query_clone(self, *, queryId: int, clonedName: str, **kwargs):
        kwargs.update({"clonedQueryName": clonedName})

        return self.api_call(f'/queries/{queryId}', HTTPMethod.POST, json=kwargs)

    @validateShareParams
    def query_shareToUserGroups(self, *, queryId: int, shareProperty: List[dict], **kwargs):
        """Share query to users or groups.

        :param queryId: query id
        :param shareProperty: share properties
            [
                  {
                    "type" : "Users",
                    "access_level" : 1,
                    "name" : "someUser1@host.com",
                    "sso_user": false
                  },
                  {
                    "type" : "Groups",
                    "access_level" : 1,
                    "id" : 10001
                  }
            ]
        :param kwargs:
        :return:
        """

        kwargs.update({"shareProperties": shareProperty})

        return self.api_call(f'/queries/{queryId}/share', HTTPMethod.PUT, json=kwargs)

    # CATEGORIES
    @validateCategoryAssets
    def category_list(self, *, assetType: int, sharing: bool = False, **kwargs):
        """List all categories details for a given user

        :param assetType: (int) assetTypes of categories to list [1-dashboards, 2-widgets, 4-queries]
        :param sharing: (bool) set to true to show which users/groups each category is shared to
        :param kwargs:
        :return:
        """
        kwargs.update({"objectType": assetType, "withSharing": sharing})

        return self.api_call('/category', HTTPMethod.GET, params=kwargs)

    @validateCategoryAssets
    @validateShareParams
    def category_shareToUserGroups(self, *, assetType: int, categoryId: int, shareProperty: List[dict], **kwargs):
        """Share category to users or groups. i.e.
                    [
                      {
                        "type" : "Users",
                        "access_level" : 1,
                        "name" : "someUser1@host.com",
                        "sso_user": false
                      },
                      {
                        "type" : "Groups",
                        "access_level" : 1,
                        "id" : 10001
                      }
                    ]

        :param assetType:
        :param categoryId:
        :param shareProperty:
        :param kwargs:
        :return:
        """

        kwargs.update({"shareProperties": shareProperty})
        return self.api_call(f'/category/{categoryId}/share?objectType={assetType}', HTTPMethod.PUT, json=kwargs)

    @validateCategoryAssets
    def category_create(self, *, assetType: int, parentId: int = 0, name: str, **kwargs):
        kwargs.update({"parentId": parentId, "categoryName": name})

        return self.api_call(f'/category?objectType={assetType}', HTTPMethod.POST, json=kwargs)

    @validateCategoryAssets
    def category_delete(self, *, assetType: int, categoryId: int, **kwargs):
        """delete category"""
        kwargs.update({"objectType": assetType})

        return self.api_call(f'/category/{categoryId}', HTTPMethod.DELETE, params=kwargs)

    @validateCategoryAssets
    def category_edit(self, *, assetType: int, categoryId: int, name: str, parentId: int, **kwargs):
        kwargs.update({"categoryName": name, "parentId": parentId})

        return self.api_call(f'/category/{categoryId}?objectType={assetType}', HTTPMethod.PUT, json=kwargs)

    @validateCategoryAssets
    def category_assignCatToAsset(self, *, assetType: int, categoryIds: List[int], assetId: int, **kwargs):
        """ assigns a list categories to an asset, replacing any existing categories on that asset
        :param assetType:
        :param categoryIds:
        :param assetId:
        :param kwargs:
        :return:
        """

        kwargs.update({"categories": categoryIds, "objectId": assetId})

        return self.api_call(f'/category/assign?objectType={assetType}', HTTPMethod.POST, json=kwargs)

    @validateCategoryAssets
    def category_addCatToAsset(self, *, assetType: int, categoryId: int, assetId: int, **kwargs):
        """ adds a category to an asset. Any existing asset will be left as is.

        :param assetType:
        :param categoryId:
        :param assetId:
        :param kwargs:
        :return:
        """
        kwargs.update({"category": categoryId, "objectId": assetId})

        return self.api_call(f'/category/add?objectType={assetType}', HTTPMethod.POST, json=kwargs)

    @validateCategoryAssets
    def category_removeCatFromAsset(self, *, assetType: int, categoryId: int, assetId: int, **kwargs):
        kwargs.update({"category": categoryId, "objectId": assetId})

        return self.api_call(f'/category/remove?objectType={assetType}', HTTPMethod.POST, json=kwargs)

    @validateCategoryAssets
    def category_copy(self, *, assetType: int, sourceId: int, targetId: int, **kwargs):
        """Copies a category structure from source category to a destination category including assets association.
        The assets will not be cloned, only put into new category structure.

        :param assetType: asset id to
        :param sourceId: (int) source category id to copy from
        :param targetId: (int) target category id in which put the copy of source category
        :return:
        """
        kwargs.update({"sourceCategoryId": sourceId, "targetParentCategoryId": targetId})

        return self.api_call(f'/category/copy?objectType={assetType}', HTTPMethod.POST, json=kwargs)

    # GROUPS
    def group_list(self, **kwargs):
        """List all groups belonging to current user"""

        return self.api_call('/groups', HTTPMethod.GET, params=kwargs)

    def group_listByUser(self, *, userId: int, **kwargs):
        """Retrieve groups for a user by an user id"""
        return self.api_call(f'/users/{userId}/groups', HTTPMethod.GET, params=kwargs)

    def group_getGroupDetails(self, *, groupId: int, sharing: bool = False, **kwargs):
        """Retrieve group by an id"""
        kwargs.update({"withSharing": sharing})

        return self.api_call(f'/groups/{groupId}', HTTPMethod.GET, params=kwargs)

    def group_getGroupDetailsForUser(self, *, userId: int, groupId: int, sharing: bool = False, **kwargs):
        """Retrieve group details for a user by id"""
        kwargs.update({"withSharing": sharing})

        return self.api_call(f'/users/{userId}/groups/{groupId}', HTTPMethod.GET, params=kwargs)

    def group_create(self, *, groupName: Union[str, int], **kwargs):
        kwargs.update({"groupName": groupName})

        return self.api_call('/groups', HTTPMethod.POST, json=kwargs)

    def group_createGroupForUser(self, *, groupName: Union[str, int], userId: int, **kwargs):
        kwargs.update({"groupName": groupName})

        return self.api_call(f'/users{userId}/groups', HTTPMethod.POST, json=kwargs)

    def group_delete(self, *, groupId: int, **kwargs):
        return self.api_call(f'/groups/{groupId}', HTTPMethod.DELETE, params=kwargs)

    def group_deleteGroupForUser(self, groupId: int, userId: int, **kwargs):
        return self.api_call(f'/users/{userId}/groups/{groupId}', HTTPMethod.DELETE, params=kwargs)

    def group_edit(self, *, newGroupName: Union[str, int], groupId: int, **kwargs):
        kwargs.update({"groupName": newGroupName})

        return self.api_call(f'/groups/{groupId}', HTTPMethod.PUT, data=kwargs)

    def group_editGroupForUser(self, *, userId: int, groupId: int, newGroupName: Union[str, int], **kwargs):
        kwargs.update({"groupName": newGroupName})

        return self.api_call(f'users/{userId}/groups/{groupId}', HTTPMethod.PUT, data=kwargs)

    # USERS
    def users_list(self, **kwargs):
        return self.api_call('/users', HTTPMethod.GET, params=kwargs)

    def users_getById(self, *, userId: int, **kwargs):
        return self.api_call(f'/users/{userId}', HTTPMethod.GET, params=kwargs)

    @validateUserParams
    def users_create(self, *, email: str, password: str, phone: int, groups: List[dict] = None,
                     role: str = 'user', twoFA: bool = False, **kwargs):
        """Create a new regular user with a username/password

        :param email: username/email for new user
        :param password: password for new user
        :param phone: phone number to associate with user. needed for two factor authentication
        :param groups: groups to associate user
            [{"id": 889, "access_level": 1}, {"id": 889, "access_level": 1}]
        :param role: role based access to associate user. defaults to `user`
        :param twoFA: if two factor auth is required. requires phone number
        :param kwargs:
        :return:
        """

        kwargs.update({
            "username":           email,
            "password":           password,
            "phone":              phone,
            "twoFactorAuth":      twoFA,
            "timezone":           kwargs.get('timezone', None),
            "autoShareTo":        kwargs.get('autoShareTo', []),
            "contentFilters":     kwargs.get('contentFilters', []),
            "defaultDashboardId": kwargs.get('defaultDashboardId', None),
            "userInviteJson":     {
                "userGroups": groups,
                "userRole":   role
            }
        })

        return self.api_call('/users', HTTPMethod.POST, json=kwargs)

    @validateUserParams
    def users_edit(self, *, userId: int, **kwargs):
        """edit an existing user

        :param userId: user id to be edited
        :param kwargs:
        :return:
        """
        kwargs.update({
            "name":               kwargs.get("name"),
            "roles":              kwargs.get("roles"),
            "groups":             kwargs.get("groups"),
            "autoShareTo":        kwargs.get("autoShareTo"),
            "twoFactorAuth":      kwargs.get("twoFA"),
            "phone":              kwargs.get('phone'),
            "contentFilters":     kwargs.get('contentFilters'),
            "timezone":           kwargs.get('timezone'),
            "defaultDashboardId": kwargs.get("defaultDashboardId")

        })

        return self.api_call(f'/users/{userId}', HTTPMethod.PUT, json=kwargs)

    def users_delete(self, *, userId: int, **kwargs):
        """ delete users and all assets within account

        :param userId: user ID
        :param kwargs:
        :return:
        """
        return self.api_call(f'/users/{userId}', HTTPMethod.DELETE, params=kwargs)

    def users_transferUserAssets(self, *, fromUserId: int, toUserId: int, **kwargs):
        """ transfer user assets to a different user before deleting account

        :param fromUserId: source user id to be deleted
        :param toUserId: destination user ID assets will be transferred to
        :param kwargs:
        :return:
        """
        kwargs.update({"toUserId": toUserId})
        return self.api_call(f'/users/{fromUserId}/moveAssets', HTTPMethod.PUT, json=kwargs)

    def dataset_getData(self, *, identifier: str = None, entityName: str = None, c9Filter: str = None,
                        exportFormat: str = 'json', limit: int = 10000, runtimeToken: List[dict] = None, **kwargs):
        """Access data from a widget/query

        :param identifier: query identifier. From UI go to query status to get `identifier`
        :param entityName: name of widget/dataset/query
        :param c9Filter: C9QL filter to manipulate/transform data during retrieval
        :param exportFormat: data format to return. Options: `csv, json`
        :param limit: number of records to return
        :param runtimeToken: runtime tokens for direct queries. Must be url encoded
            [{"parameterName":"$c9_customerName$", "parameterValue":"Facebook"}, {...}]
        :param kwargs:
        :return:
        """
        if runtimeToken:
            for i in runtimeToken:
                if not all(key in i for key in ['parameterName', 'parameterValue']):
                    raise ValueError('missing runtimeToken attribute: parameterName or parameterValue')

        if not any([identifier, entityName]):
            raise ValueError(f'missing parameter `identifier` or `entityName`')

        if exportFormat not in ('json', 'csv'):
            raise ValueError(f'exportFormat=`{exportFormat}` must be "csv" or "json"')

        kwargs.update({
            "identifier":    identifier,
            "entityName":    entityName,
            "c9SqlFilter":   c9Filter,
            "exportFormat":  exportFormat.lower(),
            "optimized":     kwargs.get('optimized', False),  # If True, output as json compressed gzip
            "version":       kwargs.get('version', 0),  # used with optimized
            "limit":         limit,
            "runtimeTokens": json.dumps(runtimeToken) if runtimeToken else None
        })

        return self.api_call(f'/datasets', HTTPMethod.GET, params=kwargs)

    # SYSTEM STATUS
    def system_checkAll(self, **kwargs):
        """ The status API is a public-facing API for determining the status of components and subcomponents in the
        Knowi infrastructure. checks all system components for health status. Requires system super admin permissions
        to access.

        :param kwargs:
        :return:
        """
        return self.api_call('/kpi', HTTPMethod.GET, params=kwargs)

    def system_checkMySQL(self, **kwargs):
        """ check system status for Mongo """

        return self.api_call('/kpi/checkMySQL', HTTPMethod.GET, params=kwargs)

    def system_checkMongoDB(self, **kwargs):
        """ check system status for MySQL """

        return self.api_call('/kpi/checkMongoDB', HTTPMethod.GET, params=kwargs)

    def system_checkMessageMQ(self, **kwargs):
        """ check system status for Rabbit MQ """

        return self.api_call('/kpi/checkMessageMQ', HTTPMethod.GET, params=kwargs)

    def system_checkHostedConnector(self, **kwargs):
        """ check system status for Hosted Agent """

        return self.api_call('/kpi/checkHostedConnector', HTTPMethod.GET, params=kwargs)

    def system_checkQueryPreview(self, **kwargs):
        """ check system status for query preview """
        return self.api_call('/kpi/checkQueryPreview', HTTPMethod.GET, params=kwargs)

    def system_checkQuerySaveAndRunNow(self, **kwargs):
        """ check system status for direct query """

        return self.api_call('/kpi/checkQuerySaveAndRunNow', HTTPMethod.GET, params=kwargs)

    def system_checkDashboardLoad(self, **kwargs):
        """ check system status for dashboard loading """

        return self.api_call('/kpi/checkDashboardLoad', HTTPMethod.GET, params=kwargs)

    def system_checkWidgetLoad(self, **kwargs):
        """ check system status for widget loading """

        return self.api_call('/kpi/checkWidgetLoad', HTTPMethod.GET, params=kwargs)

    @property
    def getBearerToken(self):
        if self.flag == 'mgmt':
            if self.session.headers.get('authorization'):
                return {"Authorization": self.session.headers.get('authorization')}
            else:
                self.auth()
                return {"Authorization": self.session.headers.get('authorization')}

    # SINGLE SIGN ON ENDPOINTS
    @validateUserParams
    def sso_createNewUser(self, *, email: str, userGroups: List[str] = None, userFilters: List[dict] = None,
                          updateUser: bool = False, **kwargs):
        """ creates a new SSO user

        :param email: email/username for an existing/new user
        :param userGroups: assign user to existing groups. group will be created under new user if it does not exist
        :param userFilters: assign content filters to user
        :param updateUser: (bool) If True, user details (userGroups, contentFilters, role) will be updated
                                for existing user
        :param kwargs:
        :return:
        """
        kwargs.update({"user":             email,
                       "ssoCustomerToken": self.ssoCustomerToken,
                       "userGroups[]":     userGroups if userGroups else [],
                       "role":             kwargs.get('role', 'user'),
                       "contentFilter":    json.dumps(userFilters) if userFilters else [],
                       "refresh":          updateUser
                       })

        return self.api_call('/sso/user/create', HTTPMethod.POST, data=kwargs)

    def sso_createUserSession(self, *, email: str, userToken: str, loginUrl: bool = False, **kwargs):
        """ creates a new session for an SSO user. Must create a new user token to use this endpoint

        :param email: email/username of an existing user
        :param userToken: user token of an existing user
        :param loginUrl: (bool) if True, the full login url will be returned
        :param kwargs:
        :return:
        """
        kwargs.update({"user": email, "userToken": userToken})
        if loginUrl:
            fullRsp = self.api_call('/sso/session/create', HTTPMethod.POST, data=kwargs)
            fullRsp['loginUrl'] = self.host + f'/sso/user/login?token={fullRsp["data"]}'
            return fullRsp
        else:
            return self.api_call('/sso/session/create', HTTPMethod.POST, data=kwargs)

    @validateUserParams
    def sso_updateUserContentFilters(self, *, email: str, userFilters: List[dict], **kwargs):
        kwargs.update({"ssoCustomerToken": self.ssoCustomerToken,
                       "user":             email,
                       "contentFilter":    json.dumps(userFilters) if userFilters else []
                       })

        return self.api_call('/sso/user/contentfilters/update', HTTPMethod.POST, data=kwargs)

    def sso_deleteUser(self, *, email: str, userToken: str, **kwargs):
        kwargs.update({"user":             email,
                       "ssoCustomerToken": self.ssoCustomerToken,
                       "userToken":        userToken
                       })

        return self.api_call('/sso/user/remove', HTTPMethod.POST, data=kwargs)

    def sso_listDashboards(self, *, sessionToken: str, **kwargs):
        """List all dashboards belonging to an SSO user

        :param sessionToken: (str) session token after authenticating sso user
        """
        kwargs.update({"token": sessionToken})

        return self.api_call('/sso/dashboards', HTTPMethod.GET, params=kwargs)

    def sso_listWidgets(self, *, sessionToken: str, **kwargs):
        """List all widgets belonging to an SSO user

        :param sessionToken: (str) session token after authenticating sso user
        """
        kwargs.update({"token": sessionToken})

        return self.api_call('/sso/widgets', HTTPMethod.GET, params=kwargs)

    def sso_listGroups(self, *, sessionToken: str, **kwargs):
        """List all groups belonging to an SSO user

        :param sessionToken: (str) session token after authenticating sso user
        """
        kwargs.update({"token": sessionToken})

        return self.api_call('/sso/groups', HTTPMethod.GET, params=kwargs)

    def sso_listQueries(self, *, sessionToken: str, **kwargs):
        """List all queries belonging to an SSO user

        :param sessionToken: (str) session token after authenticating sso user
        """
        kwargs.update({"token": sessionToken})

        return self.api_call('/sso/queries', HTTPMethod.GET, params=kwargs)

    def sso_lastActivity(self, sessionToken: str, **kwargs):
        """Get the latest timestamp in milliseconds for an SSO user's activity. Returns "-1" if user is inactive.

        :param sessionToken: (str) session token after authenticating sso user
        """

        kwargs.update({"token": sessionToken})

        return self.api_call('/sso/session/lastActive', HTTPMethod.GET, params=kwargs)

    def sso_sessionKeepAlive(self, sessionToken: str, **kwargs):
        """Extend lifetime of SSO session token by 30 minutes

        :param sessionToken: (str) session token after authenticating sso user
        """

        kwargs.update({"token": sessionToken})
        return self.api_call('/sso/session/keepAlive', HTTPMethod.PUT, params=kwargs)

    def sso_logout(self, sessionToken: str, **kwargs):
        """Logout and terminate an SSO session

        :param sessionToken: (str) session token after authenticating sso user
        """

        kwargs.update({"token": sessionToken})
        return self.api_call('/sso/user/logout', HTTPMethod.PUT, params=kwargs)

    # SSO USER NATURAL LANGUAGE PROCESSING
    def sso_listNlpSuggestions(self, *, sessionToken: str, query: str, **kwargs):
        kwargs.update({"token": sessionToken, "query": query})

        return self.api_call('/sso/nlp/suggestions', HTTPMethod.GET, params=kwargs)

    def sso_parseNlpSuggestions(self, *, sessionToken: str, query: str, datasetId: int, **kwargs):
        kwargs.update({"query":     query,
                       "datasetId": datasetId,
                       "format":    kwargs.get("format", "json")
                       })
        params = {"token": sessionToken, }

        return self.api_call('/sso/nlp/query/parse', HTTPMethod.POST, data=kwargs, params=params)

    def nlp_listNlpSuggestions(self, *, query: str, **kwargs):
        kwargs.update({"query": query})

        return self.api_call('/nlp/suggestions', HTTPMethod.GET, params=kwargs)

    def nlp_parseNlpSuggestions(self, *, query: str, datasetId: int, **kwargs):
        kwargs.update({"query":     query,
                       "datasetId": datasetId,
                       "format":    kwargs.get("format", "json")
                       })

        return self.api_call('/nlp/query/parse', HTTPMethod.POST, data=kwargs)

    # SUB-CUSTOMER MANAGEMENT
    @validateSubCustomer
    def sso_createSubCustomer(self, *, email: str, subCustomerName: str, groups: List[str] = None,
                              subCustomerFilters: List[dict] = None, roles: List[str] = None, **kwargs):
        """Creates a subCustomer account under the parent  customer.

        :param roles: (list) clone a custom role from a parentCustomer to a subCustomer
        :param subCustomerFilters: (list) apply a customer level contentFilter to a subCustomer
        :param email: (str) First admin user account/email for newly created subCustomer
        :param subCustomerName: (str) Name of subCustomer account
        :param groups: (list) groups to share from parentCustomer to subCustomer
        :param kwargs:
        :return: subCustomerToken and an ssoUserToken
        """
        kwargs.update({"ssoCustomerToken": self.ssoCustomerToken,
                       "subCustomerUser":  email,
                       "subCustomerName":  subCustomerName,
                       "contentFilter":    json.dumps(subCustomerFilters) if subCustomerFilters else [],
                       "userGroups[]":     groups,
                       "roles[]":          roles
                       })

        return self.api_call('/sso/customer', HTTPMethod.POST, data=kwargs)

    @validateSubCustomer
    def sso_updateSubCustomer(self, *, subCustomerToken: str, subCustomerName: str = None, email: str = None,
                              groups: List[str] = None, refreshToken: bool = False,
                              subCustomerFilters: List[dict] = None, roles: List[str] = None,
                              overwriteRoles: bool = False,
                              **kwargs):
        """ Update attributes an existing subCustomer

        :param subCustomerToken: subCustomer token
        :param subCustomerName: update subCustomer name
        :param email: associate/disassociate a subCustomerUser to/from with parentCustomer group.
        :param groups: associate a group from parentCustomer to subCustomer.
                        Leave empty to disassociate user (email) from group, i.e. (groups=[])
        :param refreshToken: (bool) If True, a new subCustomer token is generated
        :param subCustomerFilters: (list) update subCustomer content filter
        :param roles: update copied role from parentCustomer to subCustomer
        :param overwriteRoles: (bool) If true, it overwrites existing role with new role
        :param kwargs:
        :return:
        """
        kwargs.update({"ssoCustomerToken": self.ssoCustomerToken,
                       "subCustomerUser":  email,
                       "subCustomerName":  subCustomerName,
                       "userGroups[]":     groups if groups else [],
                       "contentFilter":    json.dumps(subCustomerFilters) if subCustomerFilters else [],
                       "refreshToken":     refreshToken,
                       "subCustomerToken": subCustomerToken,
                       "roles[]":          roles,
                       "overwriteRoles":   overwriteRoles
                       })

        return self.api_call('/sso/customer', HTTPMethod.PUT, data=kwargs)

    def sso_listSubCustomers(self, byName: str = None, **kwargs):
        """List all subCustomers within a parentCustomer

        :param byName: filter subCustomers by name
        :param kwargs:
        :return:
        """
        kwargs.update({"ssoCustomerToken": self.ssoCustomerToken,
                       "filterByName":     byName})

        return self.api_call('/sso/customer', HTTPMethod.GET, params=kwargs)

    def sso_getSubCustomerByIdentifier(self, identifier: Union[str, int], **kwargs):
        """Get details of a customer by subCustomerToken or subCustomerId

        :param identifier: this can be subCustomerToken or subCustomerId
        :return:
        """
        kwargs.update({"ssoCustomerToken": self.ssoCustomerToken})

        return self.api_call(f'/sso/customer/{identifier}', HTTPMethod.GET, params=kwargs)

    def sso_listSubCustomerUsers(self, identifier: Union[str, int], **kwargs):
        """List users belonging to subCustomer

        :param identifier: this can be subCustomerToken or subCustomerId
        :param kwargs:
        :return:
        """

        kwargs.update({"ssoCustomerToken": self.ssoCustomerToken})

        return self.api_call(f'/sso/customer/{identifier}/users', HTTPMethod.GET, params=kwargs)
