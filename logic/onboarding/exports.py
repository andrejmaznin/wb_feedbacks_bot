from logic.onboarding import internals


def initiate_onboarding(message, client_id, required: bool = False):
    internals.initiate_onboarding(
        message=message,
        client_id=client_id,
        required=required
    )
