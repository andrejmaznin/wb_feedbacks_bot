import json
import logging
from typing import Optional, Union, List, Dict

from modules.commands import finish_command, Commands, update_command_metadata
from connections import bot
from connections.ymq import get_cabinets_queue
from libs.microsoft import get_ms_client
from libs.microsoft.consts import BASE_DIR_PARENT_REFERENCE
from modules.cabinets.internals import get_formatted_list_of_cabinets, check_cabinet_exists
from modules.cabinets.schemas import CabinetSchema
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
            reply_markup=get_cabinets_reply_markup(),
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
        cabinet = CabinetSchema.create(
            client_id=client_id,
            title=metadata['title'],
            token=text
        )
        ms_client = get_ms_client()

        table_item_id = ms_client.copy_item(
            item_id='3A822AFD6B06B1F4!358',
            parent_reference=BASE_DIR_PARENT_REFERENCE,
            name=f'{cabinet.id}.xlsx'
        )
        table_url = ms_client.create_url_for_item(
            item_id=table_item_id,
            url_type='edit',
            scope='anonymous'
        )

        CabinetSchema.update_table_data(
            id_=cabinet.id,
            table_url=table_url,
            table_id=table_item_id
        )

        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.CABINETS_ADD
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=f'Кабинет селлера успешно добавлен!\n',
            reply_markup=get_cabinets_reply_markup()
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=get_formatted_list_of_cabinets(client_id),
            reply_markup=get_cabinets_reply_markup(),
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
        try:
            cabinets_queue = get_cabinets_queue()
            cabinets_queue.send_message(
                MessageBody=json.dumps({'clientId': client_id, 'cabinetId': cabinet.id})
            )
        except Exception as e:
            logger.error(e, exc_info=True)
