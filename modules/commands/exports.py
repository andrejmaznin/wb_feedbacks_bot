import logging
from typing import Optional, Dict, List, Union, Tuple, Any

from modules.commands import internals
from modules.commands.consts import Commands

logger = logging.getLogger(__name__)


def initiate_command(
    client_id: str,
    telegram_id: int,
    command: Commands,
    metadata: Optional[Union[List, Dict]] = None
) -> Optional[str]:
    return internals.initiate_command(
        client_id=client_id,
        telegram_id=telegram_id,
        command=command,
        metadata=metadata
    )


def update_command_metadata(
    client_id: str,
    telegram_id: int,
    command: Commands,
    metadata: Optional[Union[List, Dict]] = None
) -> None:
    internals.update_command_metadata(
        client_id=client_id,
        telegram_id=telegram_id,
        command=command,
        metadata=metadata
    )


def finish_command(
    client_id: str,
    telegram_id: int,
    command: Commands
) -> None:
    internals.finish_command(
        client_id=client_id,
        telegram_id=telegram_id,
        command=command
    )


def get_user_command_and_metadata(client_id: str, telegram_id: int) -> Optional[Tuple[Optional[str], Any]]:
    return internals.get_user_command_and_metadata(client_id=client_id, telegram_id=telegram_id)
