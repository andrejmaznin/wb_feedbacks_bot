import json
import pipes

import pandas as pd
import ydb
from ydb import Driver

from app.connections import get_driver, get_redis_client
from app.settings import settings
from modules.feedbacks.schemas import (BarcodeFeedbackSchema,
                                       BrandFeedbackSchema)


def import_barcode_feedbacks(ydb_driver: Driver, table_content: bytes, cabinet_id: str) -> None:
    excel = pd.read_excel(table_content, sheet_name=0)
    excel.columns = 0, 1

    items = excel.to_dict('list')

    if len(items[0]) == 0 or len(items[0]) != len(items[1]):
        return None

    redis_client = get_redis_client()
    # pipeline = redis_client.pipeline()

    rows = []
    for i in range(len(items[0])):
        if not isinstance(items[0][i], int):
            continue

        feedback_str = pipes.quote(items[1][i]).strip("'")
        # pipeline.delete(f'no-feedback:{cabinet_id}:{items[0][i]}')
        rows.append(
            BarcodeFeedbackSchema(
                barcode=str(items[0][i]).encode('utf-8'),
                cabinet_id=cabinet_id.encode('utf-8'),
                pos_feedback=feedback_str.encode('utf-8')
            )
        )

    column_types = (
        ydb.BulkUpsertColumns().add_column(
            'barcode', ydb.OptionalType(ydb.PrimitiveType.String)
        ).add_column(
            'cabinet_id', ydb.OptionalType(ydb.PrimitiveType.String)
        ).add_column(
            'pos_feedback', ydb.OptionalType(ydb.PrimitiveType.String)
        )
    )
    ydb_driver.table_client.bulk_upsert(settings.YDB.database + '/barcode_feedbacks', rows, column_types)

    # pipeline.execute()


def import_brand_feedbacks(ydb_driver: Driver, table_content: bytes, cabinet_id: str) -> None:
    excel = pd.read_excel(table_content, sheet_name=1)
    excel.columns = 0, 1

    items = excel.to_dict('list')
    if len(items[0]) == 0 or len(items[0]) != len(items[1]):
        return None

    brands_data = {}
    for i in range(len(items[0])):
        pos_feedback = pipes.quote(items[0][i])
        brands = list(map(str.strip, items[1][i].split(',')))
        for brand in brands:
            brands_data[brand] = brands_data.get(brand, []) + [pos_feedback]
    rows = []
    for brand, pos_feedbacks in brands_data.items():
        rows.append(
            BrandFeedbackSchema(
                brand=brand.encode('utf-8'),
                cabinet_id=cabinet_id.encode('utf-8'),
                pos_feedbacks=json.dumps(pos_feedbacks).encode('utf-8')
            )
        )

    column_types = (
        ydb.BulkUpsertColumns().add_column(
            'brand', ydb.OptionalType(ydb.PrimitiveType.String)
        ).add_column(
            'cabinet_id', ydb.OptionalType(ydb.PrimitiveType.String)
        ).add_column(
            'pos_feedbacks', ydb.OptionalType(ydb.PrimitiveType.JsonDocument)
        )
    )
    ydb_driver.table_client.bulk_upsert(settings.YDB.database + '/brand_feedbacks', rows, column_types)


def import_feedbacks_from_table(table_content: bytes, cabinet_id: str):
    ydb_driver = get_driver()

    import_barcode_feedbacks(ydb_driver, table_content, cabinet_id)
    import_brand_feedbacks(ydb_driver, table_content, cabinet_id)
