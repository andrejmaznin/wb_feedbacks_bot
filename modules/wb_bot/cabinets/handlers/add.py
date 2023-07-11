import logging
import uuid
from typing import Dict, List, Optional, Union

from app.connections import bot, get_scan_queue
from libs.microsoft import get_ms_client
from libs.microsoft.consts import BASE_DIR_PARENT_REFERENCE
from modules.cabinets.internals import (check_cabinet_exists,
                                        get_formatted_list_of_cabinets)
from modules.cabinets.schemas import CabinetSchema
from modules.commands import Commands, finish_command, update_command_metadata
from modules.feedbacks.schemas import ScanCabinetTask
from modules.wb_bot.markups.cabinets import get_cabinets_reply_markup
from modules.wb_bot.markups.common import get_back_button_markup

logger = logging.getLogger(__name__)


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    text = message.text

    if text == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(client_id=client_id),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
        return

    if metadata['step'] == 'title':
        if check_cabinet_exists(client_id=client_id, title=text):
            bot.send_message(
                chat_id=message.from_user.id,
                text='Кабинет с таким названием уже существует! Введите название, которое еще не занято',
                reply_markup=get_back_button_markup()
            )
            return

        metadata['title'] = text
        metadata['step'] = 'token'
        update_command_metadata(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_ADD,
            metadata=metadata
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Введите Стандартный API токен от вашего аккаунта продавца',
            reply_markup=get_back_button_markup()
        )

    elif metadata['step'] == 'token':
        if not text.isascii():
            bot.send_message(
                chat_id=message.from_user.id,
                text='Не поняли вас',
                reply_markup=get_back_button_markup()
            )
            return

        ms_client = get_ms_client()
        print('got MS client')
        table_item_id = ms_client.copy_item(
            item_id='3A822AFD6B06B1F4!358',
            parent_reference=BASE_DIR_PARENT_REFERENCE,
            name=f'{str(uuid.uuid4())}.xlsx'
        )
        print('copied table')
        table_url = ms_client.create_url_for_item(
            item_id=table_item_id,
            url_type='edit',
            scope='anonymous'
        )
        print('created url')

        cabinet = CabinetSchema.create(
            client_id=client_id,
            title=metadata['title'],
            token=text
        )
        print('created cabinet')

        CabinetSchema.update_table_data(
            id_=cabinet.id,
            table_url=table_url,
            table_id=table_item_id
        )
        print('updated table data')

        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Кабинет селлера успешно добавлен!',
            reply_markup=get_cabinets_reply_markup(client_id=client_id)
        )
        '''
        bot.send_message(
            chat_id=message.from_user.id,
            text='Теперь занесите в онлайн\-таблицу ответы на отзывы:\n'
                 '`1.` На первом листе можно добавить ответы для конкретных товаров \(по их артикулам на WB\)\n'
                 '`2.` На втором — ответы для брендов в целом \(по названиям брендов\)',
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2',
        )
        '''
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(client_id=client_id),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
        try:
            scan_queue = get_scan_queue()
            scan_queue.send_message(
                MessageBody=ScanCabinetTask(clientId=client_id, cabinetId=cabinet.id).json(by_alias=True)
            )
        except Exception as e:
            logger.error(e, exc_info=True)
