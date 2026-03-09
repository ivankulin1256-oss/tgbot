from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import VPN_PLANS, GAME_CATALOG


def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🛡 VPN"), KeyboardButton(text="🎮 Игры"))
    kb.row(KeyboardButton(text="👤 Профиль"), KeyboardButton(text="👥 Рефералы"))
    kb.row(KeyboardButton(text="🎟 Промокод"), KeyboardButton(text="📦 Мои заказы"))
    return kb.as_markup(resize_keyboard=True)


def vpn_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for plan_id, plan in VPN_PLANS.items():
        price_text = "Бесплатно" if plan["price"] == 0 else f"{plan['price']} ₽"
        kb.button(text=f"{plan['name']} — {price_text}", callback_data=f"vpn_plan:{plan_id}")
    kb.button(text="◀️ Назад", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()


def vpn_plan_detail(plan_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    plan = VPN_PLANS[plan_id]
    if plan["price"] == 0:
        kb.button(text="✅ Активировать Trial", callback_data=f"vpn_activate:{plan_id}")
    else:
        kb.button(text=f"💳 Купить за {plan['price']} ₽", callback_data=f"vpn_buy:{plan_id}")
    kb.button(text="◀️ Назад", callback_data="vpn_menu")
    kb.adjust(1)
    return kb.as_markup()


def vpn_buy_menu(plan_id: str, coins: int) -> InlineKeyboardMarkup:
    plan = VPN_PLANS[plan_id]
    kb = InlineKeyboardBuilder()
    kb.button(text=f"💳 Оплатить {plan['price']} ₽", callback_data=f"invoice:vpn:{plan_id}:0")
    if coins >= plan["price"]:
        kb.button(text=f"🪙 Полностью монетами ({coins})", callback_data=f"invoice:vpn:{plan_id}:{plan['price']}")
    elif coins >= 10:
        discounted = max(1, plan["price"] - coins)
        kb.button(text=f"🪙 -{coins} монет → {discounted} ₽", callback_data=f"invoice:vpn:{plan_id}:{coins}")
    kb.button(text="◀️ Назад", callback_data=f"vpn_plan:{plan_id}")
    kb.adjust(1)
    return kb.as_markup()


def games_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for game_id, game in GAME_CATALOG.items():
        kb.button(text=game["name"], callback_data=f"game:{game_id}")
    kb.button(text="◀️ Назад", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()


def game_items_menu(game_id: str) -> InlineKeyboardMarkup:
    game = GAME_CATALOG[game_id]
    kb = InlineKeyboardBuilder()
    for item in game["items"]:
        kb.button(text=f"{item['name']} — {item['price']} ₽", callback_data=f"item:{game_id}:{item['id']}")
    kb.button(text="◀️ К играм", callback_data="games_menu")
    kb.adjust(2)
    return kb.as_markup()


def item_buy_menu(game_id: str, item_id: str, price: int, coins: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f"💳 Купить за {price} ₽", callback_data=f"game_buy:{game_id}:{item_id}:0")
    if coins >= price:
        kb.button(text=f"🪙 Полностью монетами ({coins})", callback_data=f"game_buy:{game_id}:{item_id}:{price}")
    elif coins >= 10:
        discounted = max(1, price - coins)
        kb.button(text=f"🪙 -{coins} монет → {discounted} ₽", callback_data=f"game_buy:{game_id}:{item_id}:{coins}")
    kb.button(text="◀️ Назад", callback_data=f"game:{game_id}")
    kb.adjust(1)
    return kb.as_markup()


def back_to_main() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ На главную", callback_data="back_main")
    return kb.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="cancel_state")
    return kb.as_markup()
