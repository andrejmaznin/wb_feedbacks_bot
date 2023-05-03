import json
import os
import pipes
import uuid
from typing import Optional, Union, List, Dict

import pandas as pd
import ydb
from pydantic import BaseModel

from commands import Commands, finish_command
from connections import bot, get_driver
from libs.ydb import prepare_and_execute_query
from markups.common import get_back_button_markup
from markups.feedbacks import get_feedbacks_reply_markup


class BarcodeFeedbackSchema(BaseModel):
    barcode: bytes
    client_id: bytes
    pos_feedback: bytes


def import_feedbacks_by_barcodes(file, client_id):
    excel = pd.read_excel(file, sheet_name=0)
    excel.columns = 0, 1

    items = excel.to_dict('list')

    if len(items[0]) == 0:
        return None

    if len(items[0]) != len(items[1]):
        return None

    column_types = (
        ydb.BulkUpsertColumns()
            .add_column('barcode', ydb.OptionalType(ydb.PrimitiveType.String))
            .add_column('client_id', ydb.OptionalType(ydb.PrimitiveType.String))
            .add_column('pos_feedback', ydb.OptionalType(ydb.PrimitiveType.String))
    )

    rows = []
    for i in range(len(items[0])):
        if not isinstance(items[0][i], int):
            continue

        feedback_str = pipes.quote(items[1][i]).strip("'")
        rows.append(
            BarcodeFeedbackSchema(
                barcode=str(items[0][i]).encode('utf-8'),
                client_id=client_id.encode('utf-8'),
                pos_feedback=feedback_str.encode('utf-8')
            )
        )
    driver = get_driver()
    driver.table_client.bulk_upsert(os.getenv('YDB_DATABASE') + '/barcode_feedbacks', rows, column_types)

    return True


def import_feedbacks_by_brands(file, client_id):
    excel = pd.read_excel(file, sheet_name=1)
    excel.columns = 0, 1

    items = excel.to_dict('list')

    if len(items[0]) == 0:
        return None

    if len(items[0]) != len(items[1]):
        return None

    for i in range(len(items[0])):
        brands_str = pipes.quote(items[0][i])
        prepare_and_execute_query(
            'DECLARE $clientId AS String;'
            'DECLARE $feedbackId AS String;'
            'DECLARE $brands AS String;'
            'DECLARE $posFeedback AS String;'
            'UPSERT INTO feedbacks (id, brands, client_id, pos_feedback, created_at) '
            'VALUES ($feedbackId, CAST(@@$brands@@ as JsonDocument), '
            '$clientId, $posFeedback, CurrentUtcTimestamp())',
            clientId=client_id,
            feedbackId=str(uuid.uuid4()),
            brands=json.dumps(list(map(str.strip, items[1][i].split(",")))),
            posFeedback=brands_str
        )
    return True


def table_collector(message, client_id: str):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    import_feedbacks_by_brands(downloaded_file, client_id)
    import_feedbacks_by_barcodes(downloaded_file, client_id)


def handler(
    message,
    client_id: str,
    metadata: Optional[Union[List, Dict]] = None
):
    if message.text == '◀️ Назад':
        finish_command(
            client_id=client_id,
            telegram_id=message.from_user.id,
            command=Commands.FEEDBACKS_FILE_IMPORT
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text='Вы вернулись назад',
            reply_markup=get_feedbacks_reply_markup()
        )
        return

    if message.content_type == 'document':
        if message.document.file_name.split('.')[-1] in ('xlsx', 'csv'):
            try:
                table_collector(message, client_id)
            except Exception:
                bot.send_message(
                    chat_id=message.from_user.id,
                    text=f'Видимо, вы прислали файл некорректного формата или с файл с неверными данными\.\n'
                         f'Попробуйте еще раз позже',
                    reply_markup=get_feedbacks_reply_markup(),
                    parse_mode='MarkdownV2'
                )
            else:
                bot.send_message(
                    chat_id=message.from_user.id,
                    text=f'Ответы на отзывы успешно добавлены!',
                    reply_markup=get_feedbacks_reply_markup()
                )
            finish_command(
                client_id=client_id,
                telegram_id=message.from_user.id,
                command=Commands.FEEDBACKS_FILE_IMPORT
            )
        else:
            bot.send_message(
                chat_id=message.from_user.id,
                text='Этот файл не является таблицей',
                reply_markup=get_back_button_markup()
            )
    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Не поняли вас',
            reply_markup=get_back_button_markup()
        )
