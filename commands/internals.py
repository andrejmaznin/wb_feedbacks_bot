import json
import logging
import uuid
from typing import Optional, Dict, List, Union, Tuple, Any

from commands.consts import Commands, COMMAND_PARENTS
from libs.ydb.utils import prepare_and_execute_query

logger = logging.getLogger()


def can_initiate_command(
    client_id: str,
    telegram_id: int,
    command: Commands,
) -> bool:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DECLARE $telegramId as String;'
        'SELECT command, created_at FROM commands '
        'WHERE client_id=$clientId AND telegram_id=$telegramId '
        'ORDER by created_at DESC LIMIT 1',
        clientId=client_id,
        telegramId=str(telegram_id)
    )

    if rows:
        existing_command = rows[0].command.decode('utf-8')
        if existing_command == COMMAND_PARENTS[command].value:
            return True
        return False

    return True


def initiate_command(
    client_id: str,
    telegram_id: int,
    command: Commands,
    metadata: Optional[Union[List, Dict]] = None
) -> Optional[str]:
    if not can_initiate_command(
        client_id=client_id,
        telegram_id=telegram_id,
        command=command
    ):
        logger.error(
            f'Cannot initiate command: client_id={client_id}, telegram_id={telegram_id}, command={command.value}'
        )
        return

    command_id = str(uuid.uuid4())
    prepare_and_execute_query(
        'DECLARE $commandId AS String;'
        'DECLARE $clientId AS String;'
        'DECLARE $telegramId as String;'
        'DECLARE $command as String;'
        'UPSERT INTO commands (id, client_id, telegram_id, command, created_at) '
        'VALUES ($commandId, $clientId, $telegramId, $command, CurrentUtcTimestamp())',
        commandId=command_id,
        clientId=client_id,
        telegramId=str(telegram_id),
        command=command.value
    )

    if parent_command := COMMAND_PARENTS.get(command):
        prepare_and_execute_query(
            'DECLARE $commandId AS String;'
            'DECLARE $clientId AS String;'
            'DECLARE $telegramId as String;'
            'DECLARE $parentCommand as String;'
            'DECLARE $parentId as String;'
            '$parentId = SELECT id FROM commands '
            'WHERE client_id=$clientId AND telegram_id=$telegramId AND command=$parentCommand;'
            'UPSERT INTO commands (id, parent) '
            'VALUES ($commandId, $parentId)',
            commandId=command_id,
            clientId=client_id,
            telegramId=str(telegram_id),
            parentCommand=parent_command.value
        )

    if metadata is not None:
        prepare_and_execute_query(
            'DECLARE $commandId AS String;'
            'DECLARE $metadata AS JsonDocument;'
            'UPSERT INTO commands (id, metadata) '
            'VALUES ($commandId, $metadata)',
            commandId=command_id,
            metadata=json.dumps(metadata)
        )

    return command_id


def update_command_metadata(
    client_id: str,
    telegram_id: int,
    command: Commands,
    metadata: Optional[Union[List, Dict]] = None
) -> None:
    rows = prepare_and_execute_query(
        'DECLARE $command AS String;'
        'DECLARE $clientId AS String;'
        'DECLARE $telegramId as String;'
        'SELECT id, created_at FROM commands '
        'WHERE client_id=$clientId AND telegram_id=$telegramId AND command=$command '
        'ORDER by created_at DESC LIMIT 1',
        clientId=client_id,
        telegramId=str(telegram_id),
        command=command.value
    )

    if not rows:
        return
    command_id = rows[0].id.decode('utf-8')

    prepare_and_execute_query(
        'DECLARE $commandId AS String;'
        'DECLARE $metadata AS String;'
        'UPSERT INTO commands (id, metadata, created_at) '
        'VALUES ($commandId, CAST(@@$metadata@@ AS JsonDocument), CurrentUtcTimestamp())',
        commandId=command_id,
        metadata=json.dumps(metadata)
    )


def finish_command(
    client_id: str,
    telegram_id: int,
    command: Commands
) -> None:
    prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DECLARE $telegramId as String;'
        'DECLARE $command as String;'
        '$command_id = SELECT id FROM commands '
        'WHERE client_id=$clientId AND telegram_id=$telegramId AND command=$command;'
        'DELETE FROM commands WHERE id=$command_id OR parent=$command_id',
        clientId=client_id,
        telegramId=str(telegram_id),
        command=command.value
    )


def get_user_command_and_metadata(client_id: str, telegram_id: int) -> Optional[Tuple[Optional[str], Any]]:
    rows = prepare_and_execute_query(
        'DECLARE $clientId AS String;'
        'DECLARE $telegramId AS String;'
        'SELECT command, created_at, metadata FROM commands '
        'WHERE client_id=$clientId and telegram_id=$telegramId '
        'ORDER BY created_at DESC LIMIT 1',
        clientId=client_id,
        telegramId=str(telegram_id)
    )

    if rows:
        command = rows[0].command.decode('utf-8')
        metadata = None
        if rows[0].metadata is not None:
            metadata = json.loads(rows[0].metadata)

        return command, metadata
    return None, None
