import logging
import os

import ydb

logger = logging.getLogger()

session_pool = None
session_pool_async = None
driver = None
driver_async = None


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


async def get_driver_async():
    global driver_async

    if driver_async is not None:
        return driver_async
    driver_async = ydb.aio.Driver(
        endpoint=os.getenv('YDB_ENDPOINT'),
        database=os.getenv('YDB_DATABASE')
    )
    await driver_async.wait(fail_fast=True, timeout=5)

    return driver_async


def get_session_pool():
    global session_pool

    if session_pool is not None:
        return session_pool

    ydb_driver = get_driver()
    session_pool = ydb.SessionPool(ydb_driver, 50)
    return session_pool


def dispose_connections():
    global session_pool
    global driver
    session_pool = None
    driver = None


def dispose_connections_async():
    global session_pool_async
    global driver_async
    session_pool_async = None
    driver_async = None


async def get_session_pool_async():
    global session_pool_async

    if session_pool_async is not None:
        return session_pool_async

    ydb_driver_async = await get_driver_async()
    session_pool_async = ydb.aio.SessionPool(ydb_driver_async, 100)
    return session_pool_async
