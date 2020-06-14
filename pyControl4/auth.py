"""Authenticates with the Control4 API, retrieves account and registered controller info, and retrieves a bearer token for connecting to a Control4 Director.
"""
import aiohttp
import asyncio
import async_timeout
import json

authentication_endpoint = "https://apis.control4.com/authentication/v1/rest"
get_controllers_endpoint = "https://apis.control4.com/account/v3/rest/accounts"
application_key = "78f6791373d61bea49fdb9fb8897f1f3af193f11"


async def __sendAccountAuthRequest(username, password):
    """Used internally to retrieve an account bearer token. Returns the entire JSON response from the Control4 auth API.

    Parameters:
        `username` - Control4 account username/email.

        `password` - Control4 account password.
    """
    dataDictionary = {
        "clientInfo": {
            "device": {
                "deviceName": "pyControl4",
                "deviceUUID": "0000000000000000",
                "make": "pyControl4",
                "model": "pyControl4",
                "os": "Android",
                "osVersion": "10",
            },
            "userInfo": {
                "applicationKey": application_key,
                "password": password,
                "userName": username,
            },
        }
    }
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.post(
                authentication_endpoint, json=dataDictionary
            ) as resp:
                return await resp.text()


async def __sendAccountGetRequest(account_bearer_token, uri):
    """Used internally to send GET requests to the Control4 API, authenticated with the account bearer token. Returns the entire JSON response from the Control4 auth API.

    Parameters:
        `account_bearer_token` - Control4 account bearer token.

        `uri` - Full URI to send GET request to.
    """
    headers = {"Authorization": "Bearer {}".format(account_bearer_token)}
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.get(uri, headers=headers) as resp:
                return await resp.text()


async def __sendControllerAuthRequest(account_bearer_token, controller_common_name):
    """Used internally to retrieve an director bearer token. Returns the entire JSON response from the Control4 auth API.

    Parameters:
        `account_bearer_token` - Control4 account bearer token.

        `controller_common_name`: Common name of the controller. See `getAccountControllers()` for details.
    """
    headers = {"Authorization": "Bearer {}".format(account_bearer_token)}
    dataDictionary = {
        "serviceInfo": {"commonName": controller_common_name, "services": "director"}
    }
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.post(
                authentication_endpoint, headers=headers, json=dataDictionary
            ) as resp:
                return await resp.text()


async def getAccountBearerToken(username, password):
    """Returns an account bearer token for making Control4 online API requests.

    Parameters:
        `username` - Control4 account username/email.

        `password` - Control4 account password.
    """
    data = await __sendAccountAuthRequest(username, password)
    jsonDictionary = json.loads(data)
    return jsonDictionary["authToken"]["token"]


async def getAccountControllers(account_bearer_token):
    """Returns a dictionary of the information for all controllers registered to an account.

    Parameters:
        `account_bearer_token` - Control4 account bearer token.

    Returns:
        ```
        {    
            "controllerCommonName": "control4_MODEL_MACADDRESS",
            "href": "https:\/\/apis.control4.com\/account\/v3\/rest\/accounts\/000000",
            "name": "Name"
        }
        ```
    """
    data = await __sendAccountGetRequest(account_bearer_token, get_controllers_endpoint)
    jsonDictionary = json.loads(data)
    return jsonDictionary["account"]


async def getControllerInfo(account_bearer_token, controller_href):
    """Returns a dictionary of the information of a specific controller.

    Parameters:
        `account_bearer_token` - Control4 account bearer token.

        `controller_href` - The API `href` of the controller (get this from the output of `getAccountControllers()`)

    Returns:
        ```
        {
            'allowsPatching': True,
            'allowsSupport': False,
            'blockNotifications': False,
            'controllerCommonName': 'control4_MODEL_MACADDRESS',
            'controller': {
                'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/controller'
            },
            'created': '2017-08-26T18:33:31Z',
            'dealer': {
                'href': 'https://apis.control4.com/account/v3/rest/dealers/12345'
            },
            'enabled': True,
            'hasLoggedIn': True,
            'href': 'https://apis.control4.com/account/v3/rest/accounts/000000',
            'id': 000000,
            'lastCheckIn': '2020-06-13T21:52:34Z',
            'licenses': {
                'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/licenses'
            },
            'modified': '2020-06-13T21:52:34Z',
            'name': 'Name',
            'provisionDate': '2017-08-26T18:35:11Z',
            'storage': {
                'href': 'https://apis.control4.com/storage/v1/rest/accounts/000000'
            },
            'type': 'Consumer',
            'users': {
                'href': 'https://apis.control4.com/account/v3/rest/accounts/000000/users'
            }
        }
        ```
    """
    data = await __sendAccountGetRequest(account_bearer_token, controller_href)
    jsonDictionary = json.loads(data)
    return jsonDictionary


async def getDirectorBearerToken(account_bearer_token, controller_common_name):
    """Returns a director bearer token for making Control4 Director API requests.

    Parameters:
        `account_bearer_token` - Control4 account bearer token.

        `controller_common_name`: Common name of the controller. See `getAccountControllers()` for details.
    """
    data = await __sendControllerAuthRequest(
        account_bearer_token, controller_common_name
    )
    jsonDictionary = json.loads(data)
    return jsonDictionary["authToken"]["token"]
