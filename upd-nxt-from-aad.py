"""Python console app with client credential grant authentication."""
from __future__ import print_function

import json
import pprint
import os
import subprocess
import logging
import argparse
import time
from logging.handlers import RotatingFileHandler

import config
from helpers import api_endpoint, client_credential_grant_session, user_properties

# Script execution path
path = os.path.dirname(os.path.abspath(__file__))

# Create the logger
logger = logging.getLogger('logger')
# handler = RotatingFileHandler('/var/log/nexthink/upd-nxt-from-aad.log', maxBytes=100000000, backupCount=5)
handler = RotatingFileHandler(path + '/upd-nxt-from-aad.log', maxBytes=600000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_user_properties(session):
    """Get the users with the special EY properties.
    
    session = requests.Session() instance with a valid access token for
              Microsoft Graph in its default HTTP headers

    This app retrieves the user's basic and extended properties.
 
    The code in this function includes many print statements to provide
    information about which endpoints are being called and the status and
    size of Microsoft Graph responses. This information is helpful for
    understanding how the sample works with Graph, but would not be included
    in a typical production application.
    """

    logger.info('Get users and properties --------> https://graph.microsoft.com/v1.0/users...')
    users_json, users_status_code, filename = user_properties(session, save_as='users')
    if not users_status_code: return
    logger.info('users_status_code: ' + str(users_status_code) + ', bytes returned: ' + str(len(users_json)) + ', saved as: ' + filename)
    if not 200 <= users_status_code <= 299:
        return
    logger.debug (json.dumps(users_json)+'\n')
    for user in users_json['value']:
        logger.info('Processing User: ' + user['displayName'])
        logger.debug(json.dumps(user))
        for k,v in user.items():
            prefix = '!!****EXTENSION****!! ' if k.startswith('extension_') else ''
            v = v if v else ''
            logger.debug(prefix + '"'+k+'": "'+v+'"')

def main():
    # Define argument parser
    parser = argparse.ArgumentParser()

    # Define the arguments
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    # Set log to debug if argument passed
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    os.chdir(path)

    start_time = time.time()
    logger.info("================ Starting Update Nexthink Custom Fields form EY AAD script ================")

    GRAPH_SESSION = client_credential_grant_session()
    if GRAPH_SESSION:
        get_user_properties(GRAPH_SESSION)
    # set_values(LIST_FIELDS, LIST_USERS)

    end_time = time.time()
    total = config.timer(start_time, end_time)
    logger.info("================ Sript execution completed in {0} ================".format(total))

if __name__ == '__main__':
    main()
