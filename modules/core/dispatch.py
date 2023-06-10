import logging
from typing import Dict

from modules.commands import get_user_command_and_metadata
from modules.core.maps import COMMAND_FUNCTION_MAP, PURCHASE_COMMAND_FUNCTION_MAP, EVENT_FUNCTION_MAP
from modules.wb_bot.purchases import handle_purchase_command
from modules.wb_bot.root import handle_root_command

logger = logging.getLogger(__name__)


def dispatch_commands(message, client_id: str):
    command, metadata = get_user_command_and_metadata(client_id=client_id, telegram_id=message.from_user.id)
    if command is not None:
        command_func = COMMAND_FUNCTION_MAP.get(command)
        command_func(message, client_id, metadata)
    else:
        handle_root_command(message, client_id)


def dispatch_purchase_command(message, client_id: str, user_id: str):
    command, metadata = get_user_command_and_metadata(client_id=client_id, telegram_id=message.from_user.id)
    if command is not None:
        purchase_command_func = PURCHASE_COMMAND_FUNCTION_MAP.get(command)
        purchase_command_func(message, client_id, metadata)
    else:
        handle_purchase_command(message=message, client_id=client_id, user_id=user_id)


def dispatch_event(message: Dict):
    if details := message.get('details'):
        resource_id = details.get('trigger_id') or details.get('queue_id') or None
        if event_func := EVENT_FUNCTION_MAP.get(resource_id):
            logger.info(f'Handling event from {resource_id} with {event_func.__name__}')
            event_func(message)
