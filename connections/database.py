import logging
import os

import ydb

logger = logging.getLogger()

session_pool = None
driver = None


def get_driver():
    global driver

    if driver is not None:
        return driver
    driver = ydb.Driver(
        endpoint=os.getenv('YDB_ENDPOINT'),
        database=os.getenv('YDB_DATABASE')
    )
    driver.wait(fail_fast=True, timeout=5)

    return driver


def get_session_pool():
    global session_pool

    if session_pool is not None:
        return session_pool

    ydb_driver = get_driver()
    session_pool = ydb.SessionPool(ydb_driver, 25)
    return session_pool
