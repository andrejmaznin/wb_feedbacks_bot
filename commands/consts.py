from enum import Enum


class Commands(str, Enum):
    USER_FIRST_ONBOARDING = 'user_first_onboarding'
    USER_ONBOARDING = 'user_onboarding'
    USERS = 'users'
    USERS_ADD = 'users_add'
    USERS_REMOVE = 'users_remove'
    UPDATE_AUTH_DATA = 'update_auth_data'
    ENTER_PROMOCODE = 'enter_promocode'
    FEEDBACKS = 'feedbacks'
    FEEDBACKS_ADD_BARCODE = 'feedbacks_add_barcode'
    FEEDBACKS_ADD_TEXT = 'feedbacks_add_text'
    FEEDBACKS_FILE_IMPORT = 'feedbacks_file_import'
    FEEDBACKS_EXCLUDE = 'feedbacks_exclude'
    FEEDBACKS_DEFAULT = 'feedbacks_default'
    FEEDBACKS_DEFAULT_ADD = 'feedbacks_default_add'
    FEEDBACKS_DEFAULT_REMOVE = 'feedbacks_default_remove'
    CABINETS = 'cabinets'
    CABINETS_ADD = 'cabinets_add'
    CABINETS_REMOVE = 'cabinets_remove'


COMMAND_PARENTS = {
    Commands.USERS_ADD: Commands.USERS,
    Commands.USERS_REMOVE: Commands.USERS,
    Commands.FEEDBACKS_ADD_BARCODE: Commands.FEEDBACKS,
    Commands.FEEDBACKS_ADD_TEXT: Commands.FEEDBACKS,
    Commands.FEEDBACKS_FILE_IMPORT: Commands.FEEDBACKS,
    Commands.FEEDBACKS_EXCLUDE: Commands.FEEDBACKS,
    Commands.FEEDBACKS_DEFAULT: Commands.FEEDBACKS,
    Commands.FEEDBACKS_DEFAULT_ADD: Commands.FEEDBACKS_DEFAULT,
    Commands.FEEDBACKS_DEFAULT_REMOVE: Commands.FEEDBACKS_DEFAULT,
    Commands.CABINETS_ADD: Commands.CABINETS,
    Commands.CABINETS_REMOVE: Commands.CABINETS
}
