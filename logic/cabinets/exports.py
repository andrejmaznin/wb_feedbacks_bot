from logic.cabinets import internals


def get_formatted_list_of_cabinets(client_id: str) -> str:
    return internals.get_formatted_list_of_cabinets(client_id=client_id)


def delete_invalid_cabinets_for_client(client_id: str) -> None:
    return internals.delete_invalid_cabinets_for_client(client_id=client_id)
