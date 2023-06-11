import logging
import uuid
from typing import Optional, List, Dict

from ydb import BaseRequestSettings, RetrySettings, BackoffSettings

from connections import get_session_pool, get_session_pool_async

logger = logging.getLogger(__name__)


def fix_query_params(params: Dict) -> Dict:
    fixed_params = {}
    for k, v in params.items():
        if isinstance(v, list):
            fixed_list = []
            for i in v:
                if isinstance(i, str):
                    fixed_list.append(i.encode('utf-8'))
                else:
                    fixed_list.append(i)
            fixed_params[f'${k}'] = fixed_list

        else:
            fixed_params[f'${k}'] = v.encode('utf-8') if isinstance(v, str) else v
    return fixed_params


def prepare_and_execute_query(query: str, **kwargs) -> Optional[List]:
    pool = get_session_pool()
    params = fix_query_params(kwargs)

    def callee(session):
        prepared_query = session.prepare(query)
        query_result = session.transaction().execute(
            prepared_query,
            params,
            commit_tx=True,
            settings=BaseRequestSettings().with_timeout(0.5).with_operation_timeout(0.4).with_cancel_after(0.4)
        )
        return query_result

    result = pool.retry_operation_sync(
        callee=callee,
        retry_settings=RetrySettings().with_fast_backoff(
            backoff_settings=BackoffSettings()
        )
    )
    if result:
        if rows := result[0].rows:
            return rows
    return []


async def prepare_and_execute_query_async(query: str, **kwargs) -> Optional[List]:
    pool = await get_session_pool_async()

    params = fix_query_params(kwargs)

    # logger.info(f'Prepared query: {prepared_query.yql_text}')

    async def callee(session):
        prepared_query = await session.prepare(query)
        query_result = await session.transaction().execute(
            prepared_query,
            params,
            commit_tx=True,
            settings=BaseRequestSettings().with_timeout(1).with_operation_timeout(0.8).with_cancel_after(0.8)
        )
        return query_result

    result = await pool.retry_operation(
        callee=callee,
        retry_settings=RetrySettings().with_fast_backoff(
            backoff_settings=BackoffSettings()
        )
    )

    if result:
        if rows := result[0].rows:
            return rows
    return []


def get_or_generate_id(query: str, **kwargs) -> str:
    if 'select id' not in query.lower():
        return str(uuid.uuid4())

    rows = prepare_and_execute_query(query=query, **kwargs)
    if rows:
        return rows[0].id.decode('utf-8')
    return str(uuid.uuid4())
