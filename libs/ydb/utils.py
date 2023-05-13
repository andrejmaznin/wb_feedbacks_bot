import logging
import uuid
from typing import Optional, List, Dict

from connections import get_session_pool, get_session_pool_async

logger = logging.getLogger(__name__)


def fix_query_params(params: Dict) -> Dict:
    fixed_params = {}
    for k, v in params.items():
        fixed_params[f'${k}'] = v.encode('utf-8') if isinstance(v, str) else v
    return fixed_params


def prepare_and_execute_query(query: str, **kwargs) -> Optional[List]:
    pool = get_session_pool()

    params = fix_query_params(kwargs)
    with pool.checkout() as session:
        prepared_query = session.prepare(query)
        result = session.transaction().execute(
            prepared_query,
            params,
            commit_tx=True
        )

    if result:
        if rows := result[0].rows:
            return rows
    return []


async def prepare_and_execute_query_async(query: str, **kwargs) -> Optional[List]:
    pool = await get_session_pool_async()
    session = await pool.acquire()

    params = fix_query_params(kwargs)
    prepared_query = await session.prepare(query)
    # logger.info(f'Prepared query: {prepared_query.yql_text}')

    result = await session.transaction().execute(
        prepared_query,
        params,
        commit_tx=True
    )
    await pool.release(session)

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
