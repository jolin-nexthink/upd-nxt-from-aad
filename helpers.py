"""helper functions for Microsoft Graph"""
from __future__ import print_function

import json
import logging
import time
import urllib
import urlparse
import io

from adal import AuthenticationContext
import requests

import config

# Create the logger
logger = logging.getLogger('logger')

def api_endpoint(url):
    """Convert a relative path such as /me/photo/$value to a full URI based
    on the current RESOURCE and API_VERSION settings in config.py.
    """
    if urlparse.urlparse(url).scheme in ['http', 'https']:
        logger.info('api_endpoint - url: ' + url)
        return url # url is already complete
    newURL = config.RESOURCE + '/' + config.API_VERSION + '/' + url.lstrip('/')
    logger.info('api_endpoint - newURL: ' + newURL)
    return newURL
    # return urllib.parse.urljoin(f'{config.RESOURCE}/{config.API_VERSION}/',
    #                             url.lstrip('/'))

def client_credential_grant_session():
    """Obtain an access token from Azure AD (via client credential grant)
    and create a Requests session instance ready to make authenticated calls to
    Microsoft Graph.

    Returns Requests session object if user signed in successfully. The session
    includes the access token in an Authorization header.

    User identity must be an organizational account (ADAL does not support MSAs).
    """
    ctx = AuthenticationContext(config.AUTHORITY_URL)
    token_response = ctx.acquire_token_with_client_credentials(config.RESOURCE, config.CLIENT_ID, config.CLIENT_SECRET)
    if 'accessToken' not in token_response:
        logger.info('Unable to get access token from ADAL')
        return None

    session = requests.Session()
    session.headers.update({
        'Authorization': token_response['tokenType'] + ' ' + token_response['accessToken'],
        'SdkVersion': 'sample-python-adal',
        'x-client-SKU': 'sample-python-adal',
        'Accept': 'application/json'})
    return session

# pylint: disable=use-before-def
def user_properties(session, save_as=None):
    """Get selected EY specific user properties.

    session = requests.Session() instance with Graph access token
    save_as = optional filename to save the results locally.

    Returns a tuple of the users (raw JSON data), HTTP status code, saved filename.
    """
    start_time = time.time()
    logger.info("================ starting user_properties() ================")

    users_json = None
    users_status_code = None
    filename = None

    endpoint = 'users?$select=' + ','.join(config.AAD_USER_FIELDS) + config.MAX_ROWS  + config.FILTER
    cur_endpoint = api_endpoint(endpoint)
    num_users = 0
    num_pages = 0
    first_row = True

    while cur_endpoint:
        users_response = session.get(cur_endpoint, stream=False)

        users_status_code = users_response.status_code
        logger.info('users_status_code: ' + str(users_status_code))

        if users_response.ok:
            num_pages += 1
            print('Page number: ' + str(num_pages))
            logger.info('Page number: ' + str(num_pages))
            users_json = users_response.json()
            print('num_users so far: ' + str(num_users))
            logger.info('num_users so far: ' + str(num_users))
            num_users += len(users_json['value']) if 'value' in users_json else 0
            logger.info('page size: ' + str(len(users_json['value']) if 'value' in users_json else 0))
            
            if 'value' in users_json and save_as:
                value_extension = 'value.json'
                filename = save_as + '.' + value_extension
                with open(filename, 'a') as fhandle:
                    json.dump(users_json['value'], fhandle)
                    fhandle.write('\n')
                context_extension = 'context.json'
                context_filename = save_as + '.' + context_extension
                with open(context_filename, 'a') as chandle:
                    json.dump(users_json['@odata.context'] + '\n', chandle)
                types_extension = 'types.csv'
                types_filename = save_as + '.' + types_extension
                with io.open(types_filename, 'a', encoding="utf-8") as thandle:
                    if first_row:
                        thandle.write(u'id,userPrincipalName,displayName,EYAccountType\n')
                        first_row = False
                    for usr in users_json['value']:
                        if 'extension_2cc2f842b72044dcaf51a3fc59fc27c8_EYAccountType' in usr:
                            thandle.write(usr['id'] + ',' + usr['userPrincipalName'] + ',' + usr['displayName'] + ',' + usr['extension_2cc2f842b72044dcaf51a3fc59fc27c8_EYAccountType'] + '\n')
                        else:
                            thandle.write(usr['id'] + ',' + usr['userPrincipalName'] + ',' + usr['displayName'] + ',N/A\n')
            elif 'value' in users_json:
                logger.debug('response as json: ' + json.dumps(users_json['value']))
            else:
                filename = ''
            
            cur_endpoint = users_json['@odata.nextLink']  if '@odata.nextLink' in users_json else None
            if num_pages >= config.MAX_PAGES: break

        else:            
            break

    end_time = time.time()
    total = config.timer(start_time, end_time)
    logger.info("================ user_properties() completed in {0} ================".format(total))

    print('num_pages: ' + str(num_pages))
    print('num_users: ' + str(num_users))
    logger.info('num_pages: ' + str(num_pages))
    logger.info('num_users: ' + str(num_users))

    return (users_json, users_status_code, filename)
