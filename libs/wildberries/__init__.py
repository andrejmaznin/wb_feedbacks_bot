from libs.wildberries.client import WildberriesAPIClient

wb_client = None


def get_wb_client():
    global wb_client

    if wb_client is None:
        wb_client = WildberriesAPIClient()
    return wb_client
