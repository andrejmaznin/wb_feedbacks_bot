from typing import Optional, Union, List, Dict

from telebot.types import ReplyKeyboardRemove

from commands import Commands, finish_command, update_command_metadata
from connections import bot
from markups.common import get_back_button_markup
from markups.onboarding import get_yes_no_markup, get_yes_no_back_markup
from markups.root import get_root_reply_markup
from libs.ydb import get_or_generate_id, prepare_and_execute_query


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    if metadata is None or not isinstance(metadata, dict):
        return

    text = message.text
    required = metadata['required']

    if not text:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_back_button_markup() if not required else None
        )
        return

    if text == '◀️ Назад' and not required:
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_root_reply_markup(client_id)
        )
        return

    if metadata.get('step') == 0:
        if text not in ('Да', 'Нет'):
            bot.send_message(
                chat_id=message.from_user.id,
                text='Не поняли вас',
                reply_markup=get_yes_no_back_markup() if not required else get_yes_no_markup()
            )
            return

        metadata['complain'] = True if text == 'Да' else False
        metadata['step'] += 1

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING,
            metadata=metadata
        )

        bot.send_message(
            chat_id=message.from_user.id,
            text='Должен ли бот отвечать на отрицательные (рейтинг 1, 2, 3) отзывы?',
            reply_markup=get_yes_no_back_markup() if not required else get_yes_no_markup()
        )

    elif metadata.get('step') == 1:
        if text not in ('Да', 'Нет'):
            bot.send_message(
                chat_id=message.from_user.id,
                text='Не поняли вас',
                reply_markup=get_yes_no_back_markup() if not required else get_yes_no_markup()
            )
            return

        if text == 'Да':
            metadata['reply_neg'] = True
            metadata['step'] += 1
            bot.send_message(
                chat_id=message.from_user.id,
                text='Введите ответ по умолчанию на отрицательные (рейтинг 1, 2, 3) отзывы',
                reply_markup=get_back_button_markup() if not required else ReplyKeyboardRemove()
            )
        else:
            metadata['reply_neg'] = False
            metadata['step'] += 2
            bot.send_message(
                chat_id=message.from_user.id,
                text='Введите ответ по умолчанию на положительные (рейтинг 0, 4, 5) отзывы',
                reply_markup=get_back_button_markup() if not required else ReplyKeyboardRemove()
            )

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING,
            metadata=metadata
        )

    elif metadata.get('step') == 2:
        metadata['neg_feedback'] = text
        metadata['step'] += 1
        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите ответ по умолчанию на положительные (рейтинг 0, 4, 5) отзывы',
            reply_markup=get_back_button_markup() if not required else ReplyKeyboardRemove()
        )

    elif metadata.get('step') == 3:
        metadata['pos_feedback'] = text
        metadata['step'] += 1

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите ключ WILDAUTHNEW_V3 от вашего аккаунта продавца',
            reply_markup=get_back_button_markup() if not required else ReplyKeyboardRemove()
        )

    elif metadata.get('step') == 4:
        metadata['wildauthnew_v3'] = text
        metadata['step'] += 1

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING,
            metadata=metadata
        )

        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите WBToken от вашего аккаунта продавца',
            reply_markup=get_back_button_markup() if not required else ReplyKeyboardRemove()
        )

    elif metadata.get('step') == 5:
        metadata['wbtoken'] = text
        metadata['step'] += 1

        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING,
            metadata=metadata
        )

        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите Supplier ID вашего аккаунта продавца',
            reply_markup=get_back_button_markup() if not required else ReplyKeyboardRemove()
        )

    elif metadata.get('step') == 6:
        metadata['x_supplier_id'] = text

        settings_id = get_or_generate_id(
            f'SELECT id FROM settings WHERE client_id="{client_id}"'
        )
        cookie_id = get_or_generate_id(
            f'SELECT id FROM cookies WHERE client_id="{client_id}"'
        )
        feedback_id = get_or_generate_id(
            f'SELECT id FROM feedbacks WHERE client_id="{client_id}" AND barcode IS NULL AND brands IS NULL'
        )

        prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'DECLARE $cookieId AS String;'
            'DECLARE $wbToken AS String;'
            'DECLARE $wildAuthNewV3 AS String;'
            'DECLARE $xSupplierId AS String;'
            'DECLARE $settingsId AS String;'
            'DECLARE $complain AS Bool;'
            'DECLARE $replyNeg AS Bool;'
            'UPSERT INTO clients (id, onboarding) VALUES ($clientId, True);'
            'UPSERT INTO cookies (id, client_id, wbtoken, wildauthnew_v3, x_supplier_id) '
            'VALUES ($cookieId, $clientId, $wbToken, $wildAuthNewV3, $xSupplierId);'
            'UPSERT INTO settings (id, client_id, complain, reply_neg) '
            'VALUES ($settingsId, $clientId, $complain, $replyNeg);',
            clientId=client_id,
            cookieId=cookie_id,
            wbToken=metadata['wbtoken'],
            wildAuthNewV3=metadata['wildauthnew_v3'],
            xSupplierId=metadata['x_supplier_id'],
            settingsId=settings_id,
            complain=metadata['complain'],
            replyNeg=metadata['reply_neg']
        )

        if metadata['reply_neg']:
            prepare_and_execute_query(
                'DECLARE $feedbackId AS String;'
                'DECLARE $clientId AS String;'
                'DECLARE $posFeedback AS String;'
                'DECLARE $negFeedback AS String;'
                'UPSERT INTO feedbacks (id, client_id, pos_feedback, neg_feedback) '
                'VALUES ($feedbackId, $clientId, $posFeedback, $negFeedback);',
                feedbackId=feedback_id,
                clientId=client_id,
                posFeedback=metadata['pos_feedback'],
                negFeedback=metadata['neg_feedback']
            )
        else:
            prepare_and_execute_query(
                'DECLARE $feedbackId AS String;'
                'DECLARE $clientId AS String;'
                'DECLARE $posFeedback AS String;'
                'UPSERT INTO feedbacks (id, client_id, pos_feedback) '
                'VALUES ($feedbackId, $clientId, $posFeedback);',
                feedbackId=feedback_id,
                clientId=client_id,
                posFeedback=metadata['pos_feedback']
            )

        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.USER_ONBOARDING
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Бот готов к работе!',
            reply_markup=get_root_reply_markup(client_id)
        )
        '''
        table_url = get_or_create_user_excel_table(client_id).replace('.', '\\.')
        bot.send_message(
            chat_id=message.from_user.id,
            text=f'Вот ссылка на Яндекс\.Таблицу, в которую нужно добавить ответы на отзывы:\n\n'
                 f'{table_url}\n\n'
                 f'После того, как таблица будет заполнена, нажмите кнопку "🔄 Обновить данные"',
            reply_markup=get_root_reply_markup(client_id),
            parse_mode='MarkdownV2'
        )
        '''
