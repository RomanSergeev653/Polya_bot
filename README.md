# Polya_bot

Telegram-бот каталога на **aiogram 3** с каруселью товаров и админ-панелью в боте.

## Возможности

- Главное меню с категориями и контактами
- Карусель товаров (◀ позиция ▶) и фото внутри товара (◀ фото ▶), обе зациклены
- Кнопка «Хочу заказать» с инструкцией и ссылкой в ЛС
- Админка `/admin`: категории, товары (несколько фото на товар), текст меню, контакты

## Быстрый старт (VPS)

```bash
git clone <your-repo-url> Polya_bot
cd Polya_bot
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
docker compose up -d --build
docker compose logs -f bot
```

## Переменные окружения

| Переменная        | Описание                          |
|-------------------|-----------------------------------|
| `BOT_TOKEN`       | Токен от [@BotFather](https://t.me/BotFather) |
| `ADMIN_USER_IDS`  | Один или несколько Telegram user id через запятую (например `123` или `123,456`). Первый id — основной контакт для кнопки «Написать сейчас». |

Узнать свой id: [@userinfobot](https://t.me/userinfobot).

## Админка

1. Напишите боту `/admin` (только с аккаунтов из `ADMIN_USER_IDS`)
2. Добавьте категории (Браслеты, Ожерелья, Картины и т.д.)
3. Добавьте товары — можно загрузить несколько фото (при добавлении или позже в «📷 Фото»)
4. В админке → «📝 Текст меню» и «📞 Контакты» — настройте тексты для покупателей

## Обновление на сервере

```bash
git pull
docker compose up -d --build
```

База `data/shop.db` и `.env` не в git — не перезапишутся.

## Локальный запуск без Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заполните вручную
python -m bot
```

## Структура

```
bot/           — код бота
data/          — SQLite (shop.db)
scripts/       — setup_env.sh
```
