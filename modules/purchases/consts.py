from app.settings import settings

OFFER_TEXT = '''
Добро пожаловать\!

✅ Этот бот упростит вам работу с отзывами на Wildberries, он способен:
`1\.` Автоматически отвечать на отзывы по вашим шаблонам \(в ответе вы можете предложить купить какой\-либо товар\)
`2\.` Автоматически жаловаться на негативные отзывы, чтобы исключать их из рейтинга

✅ Вы сможете удобно ввести шаблоны ответов через `онлайн-таблицу` — ссылку на нее бот пришлет сразу после добавления кабинета селлера
💼 Бот поддерживает работу сразу с несколькими кабинетами селлера — ответы на отзывы хранятся `отдельно` для каждого кабинета

Используя этот сервис, вы получаете возможность:
🫂 Повысить лояльность клиентов
🕔 Сэкономить ценное время сотрудников
🔼 Поднять свои кабинеты селлера в рейтинге

💰 Стоимость месячной подписки начинается от `{price_1}` рублей
'''

SUBSCRIPTION_PLANS_TEXT = '''
💰 Доступны следующие тарифные планы:

1️⃣ До *1* кабинета селлера — `{price_1}` _рублей/месяц_

2️⃣ До *3* кабинетов селлера — `{price_3}` _рублей/месяц_

3️⃣ До *5* кабинетов селлера — `{price_5}` _рублей/месяц_
'''

PLANS_PRICES_MAP = {
    '1️⃣ До 1 кабинета': settings.LOGIC.price_1,
    '2️⃣ До 3 кабинетов': settings.LOGIC.price_3,
    '3️⃣ До 5 кабинетов': settings.LOGIC.price_5
}

PLANS_CAPS_MAP = {
    '1️⃣ До 1 кабинета': 1,
    '2️⃣ До 3 кабинетов': 3,
    '3️⃣ До 5 кабинетов': 5
}
