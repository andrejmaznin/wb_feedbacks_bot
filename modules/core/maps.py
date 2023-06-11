from modules.feedbacks import (reply_cabinet_handler, scan_cabinet_handler,
                               update_feedbacks_handler)
from modules.microsoft.handlers import refresh_ms_token_handler
from modules.wb_bot.cabinets import (handle_cabinets_add_command,
                                     handle_cabinets_command,
                                     handle_cabinets_remove_command)
from modules.wb_bot.purchases import (handle_enter_promocode_purchase_command,
                                      handle_subscribe_purchase_command)
from modules.wb_bot.users import (handle_users_add_command,
                                  handle_users_command,
                                  handle_users_remove_command)
from settings import event_settings

COMMAND_FUNCTION_MAP = {
    'users': handle_users_command,
    'users_add': handle_users_add_command,
    'users_remove': handle_users_remove_command,
    'cabinets': handle_cabinets_command,
    'cabinets_add': handle_cabinets_add_command,
    'cabinets_remove': handle_cabinets_remove_command
}

PURCHASE_COMMAND_FUNCTION_MAP = {
    'enter_promocode': handle_enter_promocode_purchase_command,
    'subscribe': handle_subscribe_purchase_command
}

EVENT_FUNCTION_MAP = {
    event_settings.ms_refresh: refresh_ms_token_handler,
    event_settings.scan_cabinet: scan_cabinet_handler,
    event_settings.reply_cabinet: reply_cabinet_handler,
    event_settings.update_feedbacks: update_feedbacks_handler
}
