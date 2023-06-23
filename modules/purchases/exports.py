from modules.purchases import internals


def check_has_purchase(client_id: str) -> bool:
    return internals.check_has_purchase(client_id=client_id)


def check_should_execute(client_id: str) -> bool:
    return internals.check_should_execute(client_id=client_id)


def create_payment(client_id: str, telegram_id: int, amount: int, cabinets_cap: int) -> str:
    return internals.create_payment(
        client_id=client_id,
        telegram_id=telegram_id,
        amount=amount,
        cabinets_cap=cabinets_cap
    )


def handle_successful_payment(payment_id: str, cabinets_cap: int) -> None:
    return internals.handle_successful_payment(payment_id=payment_id, cabinets_cap=cabinets_cap)
