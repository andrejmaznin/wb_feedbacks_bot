from typing import List

from modules.cabinets.schemas import CabinetSchema


def format_list_of_cabinets(cabinets: List[CabinetSchema]) -> str:
    active_list = [cab for cab in cabinets if cab.invalid is False]
    invalid_list = [cab for cab in cabinets if cab.invalid is True]

    title = 'Вот список кабинетов селлера в вашем аккаунте'
    active_title = '✅ Активные кабинеты:'
    invalid_title = '🚫 Неактивные кабинеты \(бот не может авторизоваться\):'
    active_text = ''
    invalid_text = ''

    for counter, cab in enumerate(active_list + invalid_list, start=1):
        if cab.invalid is False:
            active_text += f'*{counter}*\. `{cab.title}`    [📎 Ответы]({cab.table_url})\n'
        else:
            invalid_text += f'*{counter}*\. `{cab.title}`   [📎 Ответы]({cab.table_url})\n'

    if invalid_list:
        formatted_text = f'{title}\n\n{active_title}\n{active_text}\n{invalid_title}\n{invalid_text}'
    else:
        formatted_text = f'{title}\n\n{active_title}\n{active_text}'
    return formatted_text
