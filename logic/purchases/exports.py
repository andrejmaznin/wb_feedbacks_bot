from logic.purchases import internals


def check_has_purchase(client_id: str) -> bool:
    return internals.check_has_purchase(client_id=client_id)
