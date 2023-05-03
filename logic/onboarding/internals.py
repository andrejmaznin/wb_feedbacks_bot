from commands import initiate_command, Commands
from connections import bot
from markups.onboarding import get_yes_no_markup, get_yes_no_back_markup


def initiate_onboarding(message, client_id, required: bool = False):
    initiate_command(
        client_id=client_id,
        telegram_id=message.from_user.id,
        command=Commands.USER_ONBOARDING,
        metadata={'step': 0, 'required': required}
    )

    bot.send_message(
        chat_id=message.from_user.id,
        text='🤖 Ответьте на несколько вопросов, чтобы начать работу\n\n'
             'Должен ли бот жаловаться на отрицательные (рейтинг 1-3) отзывы?',
        reply_markup=get_yes_no_markup() if required else get_yes_no_back_markup()
    )

# TODO: finish_onboarding method
