# ThirdPart Imports
import requests

# Internal Imports
from knowipy import errors as e
from knowipy.utils import cleanNullTerms


class BaseClient:
    BASE_URL = "https://www.knowi.com"

    def __init__(
            self, *,
            host: str = BASE_URL,
            clientId: str = None,
            clientSecret: str = None,
            customerToken: str = None,
            flag: str = 'mgmt',

    ):
        self.host = host[:-1] if host.endswith('/') else host
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.ssoCustomerToken = customerToken
        self.flag = flag
        self.session = requests.Session()

        if self.flag not in ('mgmt', 'sso'):
            raise e.KnowiException(f'invalid flag=`{flag}`. supported flag inputs are (`mgmt` or `sso`)')

        if self.flag == 'mgmt':
            if not all([clientId, clientSecret]):
                raise e.KnowiException(f'client id/secret needed to use management api with flag=`{flag}`')
            else:
                self.auth()
        if self.flag == 'sso' and not customerToken:
            raise e.KnowiException(f'sso customer token needed to use single sign on api with flag=`{flag}`')

    def auth(self):
        """Constructs session with auth headers for management api

        :return:
            The headers dictionary.
                e.g. {
                    'Authorization': 'Bearer agag4345qtgq'
                }
        """

        url = f"{self.host}/api/1.0/login"
        data = {'client_id': self.clientId, 'client_secret': self.clientSecret}

        rsp = self.session.request('POST', url=url, data=data).json()
        self.session.headers.update({'Authorization': f"Bearer {rsp.get('access_token')}"})

    def _get_url(self, apiMethod: str):
        """Joins the base Knowi URL and an API method to form an absolute URL.

        :param apiMethod: The Knowi API method. e.g. '/dashboards/{dashboardId}'
        :return: The absolute API URL.
                e.g. 'https://www.knowi.com/api/1.0/api/dashboards/123'
        """
        mgmtUrl = self.host + '/api/1.0' + apiMethod
        return mgmtUrl if self.flag == 'mgmt' else self.host + apiMethod

    def _request(self, *, httpVerb: str, apiUrl: str, requestArgs: dict):
        """Submit the HTTP request with the running session.
        Returns:
            A dictionary of the response data.
        """

        if self.flag == 'mgmt':
            rsp = self.session.request(httpVerb, apiUrl, **requestArgs, stream=True)
        else:
            rsp = requests.request(httpVerb, apiUrl, **requestArgs)

        if rsp.ok:
            try:
                data = rsp.json()
            except ValueError:
                data = rsp.text

            if apiUrl.endswith('/pdf'):
                return self._download_pdf(rsp)
            else:
                return {"data": data, "headers": rsp.headers, "statusCode": rsp.status_code}
        else:
            raise e.KnowiApiException(rsp)

    @staticmethod
    def _download_pdf(rsp: requests.models.Response):
        """ download pdf from binary """

        filename = rsp.headers['content-disposition'].split('=')[1].replace('"', '')
        with open(filename, 'wb') as f:
            f.write(rsp.content)
            return {"data": f"{filename} downloaded", "headers": rsp.headers, "statusCode": rsp.status_code}

    def api_call(self, apiMethod: str, httpVerb: str, *, files: dict = None, data: dict = None, params: dict = None,
                 json: dict = None):
        """Create a request and execute the API call to Knowi.

        :param apiMethod: The target Knowi API method.
        :param httpVerb: HTTP Verb. e.g. 'GET'
        :param files:
        :param data: The body to attach to the request. If a dictionary is
                provided, form-encoding will take place.
                e.g. {'key1': 'value1', 'key2': 'value2'}
        :param params: The URL parameters to append to the URL.
                e.g. {'key1': 'value1', 'key2': 'value2'}
        :param json: JSON for the body to attach to the request
                (if files or data is not specified).
                e.g. {'key1': 'value1', 'key2': 'value2'}
        :return:
        """

        if apiMethod.startswith("/sso/") and self.flag != "sso":
            raise e.KnowiException(f'invalid method=`{apiMethod}` with flag=`{self.flag}`, use flag `sso`')
        if not apiMethod.startswith('/sso') and self.flag == 'sso':
            raise e.KnowiException(f'invalid method=`{apiMethod}` with flag=`{self.flag}` use flag `mgmt`')

        apiUrl = self._get_url(apiMethod)
        if data:
            data = cleanNullTerms(data)
        elif json:
            json = cleanNullTerms(json)
        requestArgs = {
            "data":   data,
            "files":  files,
            "params": params,
            "json":   json
        }

        return self._request(httpVerb=httpVerb, apiUrl=apiUrl, requestArgs=requestArgs)


class HTTPMethod:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
