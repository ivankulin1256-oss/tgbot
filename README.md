# 🤖 VPN + Game Shop Telegram Bot

Многофункциональный Telegram-бот с продажей VPN и игровых товаров (Brawl Stars, Clash Royale, Clash of Clans).

---

## 📦 Структура проекта

```
vpn_bot/
├── bot.py               # Точка входа
├── config.py            # Настройки и каталог товаров
├── requirements.txt
├── database/
│   └── db.py            # SQLite база данных
├── handlers/
│   ├── start.py         # /start, профиль, заказы
│   ├── vpn.py           # VPN подписки
│   ├── games.py         # Игровые товары
│   ├── referrals.py     # Реферальная система
│   ├── promo.py         # Промокоды
│   └── admin.py         # Админ-панель
└── keyboards/
    └── kb.py            # Все клавиатуры
```

---

## 🚀 Установка и запуск

### 1. Создайте бота
Напишите @BotFather в Telegram:
```
/newbot
```
Скопируйте токен.

### 2. Установите зависимости
```bash
pip install -r requirements.txt
```

### 3. Настройте config.py
```python
BOT_TOKEN = "ВАШ_ТОКЕН"        # Токен от @BotFather
ADMIN_IDS = [ВАШ_TELEGRAM_ID]  # Узнать у @userinfobot
PAYMENT_TOKEN = "..."           # Токен платёжной системы
```

### 4. Запустите
```bash
python bot.py
```

---

## 💳 Подключение оплаты

### Юкасса (рекомендуется для РФ)
1. Зарегистрируйтесь на yookassa.ru
2. Напишите @BotFather → /mybots → Payments → Юкасса
3. Вставьте полученный токен в `PAYMENT_TOKEN`

### Тест без оплаты
Используйте тестовый токен `TEST:...` от @BotFather для тестирования.

---

## ⚙️ Функционал

### Для пользователей
- 🛡 **VPN** — Trial (7 дней бесплатно) + Pro планы (1/3/12 мес.)
- 🎮 **Игровые товары** — гемы, пасы, золото для BS/CR/CoC
- 🪙 **Монеты** — внутренняя валюта для скидок
- 👥 **Рефералы** — +50 монет за приглашённого
- 🎟 **Промокоды** — монеты или % скидка
- 📦 **История заказов**

### Для администратора
| Команда | Описание |
|---------|----------|
| `/admin` | Статистика бота |
| `/admin_promo КОД ТИП СКИДКА ЛИМИТ` | Создать промокод |
| `/admin_promos` | Список промокодов |
| `/admin_balance ID СУММА` | Пополнить баланс пользователя |

#### Примеры промокодов:
```
/admin_promo WELCOME coins 100 50
/admin_promo SALE20 percent 20 100
/admin_promo VIP500 coins 500 1
```

---

## 🔑 VPN-сервер

В файле `handlers/vpn.py` строки с `key = f"vpn://..."` — замените на реальную интеграцию с вашим VPN-сервером (Outline API, 3x-ui, Marzban и т.д.).

---

## 📝 Добавление товаров

В `config.py` в словаре `GAME_CATALOG` добавьте товары:
```python
{"id": "bs_gems_500", "name": "500 Гемов", "price": 799},
```

---

## 🛡 Стек
- Python 3.10+
- aiogram 2.x
- SQLite (без доп. зависимостей)
