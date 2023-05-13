from logic.purchases import internals


def check_has_purchase(client_id: str) -> bool:
    return internals.check_has_purchase(client_id=client_id)


def check_should_execute(client_id: str) -> bool:
    return internals.check_should_execute(client_id=client_id)
