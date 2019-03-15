#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2018 Nexthink SA, Switzerland
# V 1.0.0
# Last Updated 2019.03.11

import os
import subprocess
import logging
import argparse
import time
from logging.handlers import RotatingFileHandler

# Script execution path
path = os.path.dirname(os.path.abspath(__file__))

# Create the logger
logger = logging.getLogger('logger')

handler = RotatingFileHandler('/var/log/nexthink/custom_fields.log', maxBytes=100000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Fields "name" can be retrieved from a xml of an investigation export
# Will need to check the right order of the fields, or the set the fields name afterwards
# Also, update seems to work only on "comment" field in opinion scale questions
LIST_FIELDS = ['euf_f6688ede890346e2baf15963e6b0df90_1_comment',
               'euf_f6688ede890346e2baf15963e6b0df90_0_comment']

# Format can be redefined in case, this was mostly for testing
LIST_USERS = {'nexthink@PS-WIN10': ['This is a test', 'This is my second test'],
              'nexthink@PS-WIN7': ['This is third test', 'This is the last one']}


def set_values(list_fields, list_users):
    """Function to update RA value for user

    Function that will update the value of a set list of fields for a list of users

    Args:
        list_fields: list of the fields name as in the Engine DB
        list_users: list of the users for which we need to update the information
    """

    logger.info("Preparing update statement...")

    update_statement_template = "update "
    variable = 0
    for field in list_fields:
        update_statement_template += "user." + field + "='{" + str(variable) + "}',"
        variable += 1

    # remove last comma
    update_statement_template = update_statement_template[:-1]
    update_statement_template += " where user.name like '{" + str(variable) + "}'"
    logger.debug(update_statement_template)

    logger.info("Running fields update...")
    all_results = []
    # Update the custom fields value
    for user_name, values in list_users.items():
        # Create the final update statement
        statement = update_statement_template.format(values[0], values[1], user_name)
        try:
            update_result = subprocess.check_output(["nxinfo", "shell", "-t", "csv", "-e", statement], stderr=subprocess.STDOUT)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.warning("Couldn't update custom fields of user {0}. Caught an exception".format(user_name))
            logger.exception(message)
        else:
            if len(update_result.split('\n')) > 1:
                logger.debug("Custom fields of user {0} updated successfully".format(user_name))
                all_results.append(user_name)
            else:
                logger.warning("Couldn't update custom fields of user {0}. No matching object".format(user_name))

    changed = len(all_results)
    logger.info("Total users updated: {0}".format(changed))


def timer(start, end):
    sec_elapsed = end - start
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.

    if h > 0:
        return "{} h {:>02} min {:>05.2f} sec".format(h, m, s)
    elif m > 0:
        return "{:>02} min {:>05.2f} sec".format(m, s)
    else:
        return "{:>05.2f} sec".format(s)


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
    logger.info("================ Starting RA custom fields update script ================")

    set_values(LIST_FIELDS, LIST_USERS)

    end_time = time.time()
    total = timer(start_time, end_time)
    logger.info("================ Sript execution completed in {0} ================".format(total))


main()
