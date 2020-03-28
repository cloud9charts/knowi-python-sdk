# Standard  Imports
from functools import wraps
from itertools import chain
from typing import List

# ThirdParty Imports
import pytz

# Internal Imports
import knowipy.errors as e

ACCESS_LEVEL = (1, 2)  # asset permissions level: 1=edit, 2=view
ASSET_TYPE = (1, 2, 4)  # asset types: 1=Dashboard, 2: widgets, 4:queries
SHARE_TO_USERS = ("type", 'name', 'access_level')
SHARE_TO_GROUPS = ("type", "id", "access_level")
SUPPORTED_DATASOURCES = ('cloud9charts', 'cloudant', 'couchbase', 'datastax', 'elasticsearch', 'hana', 'hive',
                         'influxdb', 'marklogic', 'mongo', 'mongoatlas' 'mysql', 'oracle', 'orientdb', 'postgresql',
                         'presto', 'redshift', 'restapi', 'snowflake', 'spark', 'sqlserver', 'teradata')


def validateCategoryAssets(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        assetType = kwargs.get('assetType')

        if assetType not in ASSET_TYPE:
            raise ValueError(f'invalid/missing assetType={assetType}. supported values are: {ASSET_TYPE}')
        return func(*args, **kwargs)

    return wrapper


def validateShareParams(func):
    """check and validate passed arguments in sharing assets to users and groups

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('shareProperty') or kwargs.get('userGroups'):
            shareProperties = kwargs.get('shareProperty') or kwargs.get('userGroups')

            for i in shareProperties:
                if 'type' not in i:
                    raise e.KnowiException('missing attribute `type` in shareProperty')
                i['type'] = i['type'].capitalize()

                # sharing to users
                if i["type"] == 'Users':
                    if not all(key in i for key in ['access_level', 'name']):
                        raise e.KnowiException(f"invalid/missing user property  key. must include: {SHARE_TO_USERS}")
                    if i['access_level'] not in ACCESS_LEVEL:
                        raise e.KnowiException(f'invalid/missing property. access_level must be 1 or 2')

                # sharing to group
                elif i['type'] == 'Groups':
                    if not all(key in i for key in ['access_level', 'id']):
                        raise e.KnowiException(f"invalid/missing group property. must include: {SHARE_TO_GROUPS}")
                    if i['access_level'] not in ACCESS_LEVEL:
                        raise ValueError(f'missing/invalid property. access_level must be 1 or 2')
                else:
                    raise ValueError(f"Invalid share `type`. allowed values: (`users`, `groups`)")

        return func(*args, **kwargs)

    return wrapper


def validateUserParams(func):
    """validate passed arguments when creating/editing a user

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if kwargs.get('timezone'):
            userTz = kwargs.get('timezone')
            if not isinstance(userTz, str):
                raise TypeError(f"Got {type(userTz)}, expected type is string, {userTz}")
            if userTz not in pytz.all_timezones:
                raise ValueError(f"Invalid timezone `{userTz}`! \n"
                                 f"For reference, see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")

        if kwargs.get('twoFA'):
            twoFA = kwargs.get('twoFA')
            phone = kwargs.get('phone')
            if not isinstance(kwargs.get('twoFA'), bool):
                raise TypeError(f"`twoFA` type must be bool. Got {type(twoFA)}.")
            if not phone:
                raise ValueError(f"`phone` is needed with twoFactorAuth= {twoFA}")

        if kwargs.get('phone'):
            kwargs['phone'] = str(kwargs.get('phone'))

        if kwargs.get('userInviteJson'):
            userProps = kwargs.get('userInviteJson')
            addGroups = userProps.get('userGroups', [])
            for i in addGroups:
                if not all(s in ['access_level', 'id'] for s in list(i)):
                    raise ValueError(f'missing/invalid userGroups property: {i}')

        if kwargs.get('contentFilters') or kwargs.get('contentFilter'):
            userFilter = kwargs.get('contentFilter') or kwargs.get('contentFilters')
            _validateContentFilters(userFilter)

        # editing existing user groups
        if kwargs.get('groups'):
            keys_ = ['access_level', 'id']
            userGroups = kwargs.get("groups")
            if not isinstance(userGroups, List):
                raise TypeError(f"groups must be a array of dicts")

            for i in userGroups:
                # TODO: refactor to use _check_dict_key(userGroups, keys_)
                if not all(key in i for key in ['access_level', 'id']):
                    raise e.KnowiException('missing/invalid properties. Required keys are `access_level` `id`')
                if i['access_level'] not in ACCESS_LEVEL:
                    raise e.KnowiException(f'access_level must be `1` or `2`, got {i["access_level"]}')

        if kwargs.get('autoShareTo'):
            # keys_ = ['id']
            autoShare = kwargs.get('autoShareTo')
            if isinstance(autoShare, dict):
                autoShare = [autoShare]
            elif isinstance(autoShare, List):
                pass
            else:
                raise TypeError('`autoShareTo` must be dict of array of dict ')

            # TODO: refactor to use _check_dict_key(autoShare, keys_)
            for i in autoShare:
                if not all(key in i for key in ['id']):
                    raise e.KnowiException('missing `id` field')

        return func(*args, **kwargs)

    return wrapper


def validateSubCustomer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('subCustomerFilters'):
            customerFilters = kwargs.get("subCustomerFilters")
            _validateContentFilters(customerFilters)
        return func(*args, **kwargs)

    return wrapper


def validateQueryParams(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        queryProperty = kwargs.get("queryProperty")
        if queryProperty.get('categories'):
            if not isinstance(queryProperty['categories'], list):
                raise e.KnowiException(f"invalid categories type should be list of int i.e. `[123, 456]`")
        if queryProperty.get("direct"):
            if not isinstance("direct", bool):
                raise e.KnowiException(f"invalid `direct` type, should be a bool: (`True`, `False`)")

        return func(*args, **kwargs)

    return wrapper


def validateDatasourceParams(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if 'datasource' not in kwargs:
            raise e.KnowiException('missing parameter "datasource"')

        if kwargs.get('datasource') not in SUPPORTED_DATASOURCES:
            raise e.KnowiException(f" invalid/unsupported datasource={kwargs['datasource']}")

        if kwargs.get('datasource') == 'restapi':
            if 'url' not in kwargs:
                raise e.KnowiException(f'Missing restapi host url={kwargs["url"]}')

        if kwargs['privateDatasource']:
            if not kwargs.get('privateConnector'):
                raise e.KnowiException('privateConnector is needed with a privateDatasource')
        if kwargs.get('tunnel'):
            if 'tunnelAddress' not in kwargs:
                raise e.KnowiException('tunnelAddress is needed with tunnel')

        return func(*args, **kwargs)

    return wrapper


def _validateContentFilters(contentFilter: List[dict] = None):
    """ validate passed arguments in constructing a user or customer content filter

    :param contentFilter: parsing contentFilters as arrays of dict i.e.
    [{"fieldName": "Zip Code", "values": ["11787"], "operator": "="}]
    :return:
    """

    OPERATOR_NAME = ['equals', 'not equals', 'greater than', 'greater than or equals', 'less than',
                     'less than or equals', 'contains', 'does not contain']
    OPERATOR_VALUE = ['=', '!=', '>', '>=', '<', '<=', 'like', 'not like']
    CONTENT_FILTER_FIELDS = ['fieldName', 'values', 'operator']

    if contentFilter and isinstance(contentFilter, list):
        for i in contentFilter:
            if all(elem in list(i) for elem in CONTENT_FILTER_FIELDS):
                filterValue = i['values']
                if not isinstance(i['values'], list):
                    i['values'] = [str(filterValue)]

                if i.get('operator') not in chain(OPERATOR_NAME, OPERATOR_VALUE):
                    raise e.KnowiException(f"invalid `operator` value in contentFilter= `{i['operator']}` ")

            else:
                raise e.KnowiException(f"missing/invalid contentFilter parameter. must have {CONTENT_FILTER_FIELDS}")

    return contentFilter

# TODO:  refactor to generalize type validations
