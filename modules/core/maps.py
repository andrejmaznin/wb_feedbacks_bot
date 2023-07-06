from app.settings import settings
from modules.feedbacks import (reply_cabinet_handler, scan_cabinet_handler,
                               update_feedbacks_handler)
from modules.microsoft.handlers import refresh_ms_token_handler
from modules.wb_bot.cabinets import (handle_cabinets_add_command,
                                     handle_cabinets_command,
                                     handle_cabinets_remove_command,
                                     handle_cabinets_update_command)
from modules.wb_bot.purchases import (handle_enter_promocode_purchase_command,
                                      handle_subscribe_purchase_command)
from modules.wb_bot.users import (handle_users_add_command,
                                  handle_users_command,
                                  handle_users_remove_command)

COMMAND_FUNCTION_MAP = {
    'users': handle_users_command,
    'users_add': handle_users_add_command,
    'users_remove': handle_users_remove_command,
    'cabinets': handle_cabinets_command,
    'cabinets_add': handle_cabinets_add_command,
    'cabinets_remove': handle_cabinets_remove_command,
    'cabinets_update': handle_cabinets_update_command
}

PURCHASE_COMMAND_FUNCTION_MAP = {
    'enter_promocode': handle_enter_promocode_purchase_command,
    'subscribe': handle_subscribe_purchase_command
}

EVENT_FUNCTION_MAP = {
    settings.TRIGGERS.ms_refresh: refresh_ms_token_handler,
    settings.YMQ.scan_id: scan_cabinet_handler,
    settings.YMQ.reply_id: reply_cabinet_handler,
    settings.YMQ.update_id: update_feedbacks_handler
}
