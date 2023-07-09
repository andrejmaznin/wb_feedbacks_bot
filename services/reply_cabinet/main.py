from app.connections.ydb import dispose_connections_async
from modules.feedbacks import reply_cabinet_handler


async def handler(event, context):
    for message in event['messages']:
        await reply_cabinet_handler(message=message)
    dispose_connections_async()
