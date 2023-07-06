from enum import Enum


class Commands(str, Enum):
    USERS = 'users'
    USERS_ADD = 'users_add'
    USERS_REMOVE = 'users_remove'
    UPDATE_AUTH_DATA = 'update_auth_data'
    ENTER_PROMOCODE = 'enter_promocode'
    SUBSCRIBE = 'subscribe'
    CABINETS = 'cabinets'
    CABINETS_ADD = 'cabinets_add'
    CABINETS_REMOVE = 'cabinets_remove'
    CABINETS_UPDATE = 'cabinets_update'


COMMAND_PARENTS = {
    Commands.USERS_ADD: Commands.USERS,
    Commands.USERS_REMOVE: Commands.USERS,
    Commands.CABINETS_ADD: Commands.CABINETS,
    Commands.CABINETS_REMOVE: Commands.CABINETS,
    Commands.CABINETS_UPDATE: Commands.CABINETS
}
