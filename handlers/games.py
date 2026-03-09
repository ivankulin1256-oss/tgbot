from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_user, update_balance, create_order, complete_order
from keyboards.kb import games_menu, game_items_menu, item_buy_menu, back_to_main, main_menu, cancel_kb
from config import GAME_CATALOG, PAYMENT_TOKEN, ADMIN_IDS

router = Router()


class GameStates(StatesGroup):
    waiting_game_id = State()


_purchase_data = {}


@router.message(F.text == "🎮 Игры")
async def show_games(message: Message):
    await message.answer("🎮 <b>Магазин игровых товаров</b>\n\nВыберите игру:", reply_markup=games_menu(), parse_mode="HTML")


@router.callback_query(F.data == "games_menu")
async def cb_games_menu(call: CallbackQuery):
    await call.message.edit_text("🎮 <b>Магазин игровых товаров</b>\n\nВыберите игру:", reply_markup=games_menu(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("game:"))
async def cb_game_select(call: CallbackQuery):
    game_id = call.data.split(":")[1]
    game = GAME_CATALOG.get(game_id)
    if not game:
        await call.answer("Игра не найдена")
        return
    await call.message.edit_text(f"{game['name']}\n\nВыберите товар:", reply_markup=game_items_menu(game_id), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("item:"))
async def cb_item_select(call: CallbackQuery):
    _, game_id, item_id = call.data.split(":")
    game = GAME_CATALOG.get(game_id)
    item = next((i for i in game["items"] if i["id"] == item_id), None)
    if not item:
        await call.answer("Товар не найден")
        return
    user = get_user(call.from_user.id)
    coins = user["balance"] if user else 0
    await call.message.edit_text(
        f"{game['emoji']} <b>{item['name']}</b>\n\n"
        f"💰 Цена: <b>{item['price']} ₽</b>\n"
        f"🪙 Ваши монеты: {coins}\n\n"
        f"⚠️ После выбора способа оплаты укажите <b>игровой ID</b>.",
        reply_markup=item_buy_menu(game_id, item_id, item["price"], coins),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("game_buy:"))
async def cb_game_buy(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    game_id, item_id, coins_str = parts[1], parts[2], parts[3]
    coins_used = int(coins_str)
    game = GAME_CATALOG.get(game_id)
    item = next((i for i in game["items"] if i["id"] == item_id), None)
    actual_price = max(0, item["price"] - coins_used)

    _purchase_data[call.from_user.id] = {
        "game_id": game_id, "item_id": item_id,
        "coins_used": coins_used, "actual_price": actual_price,
        "item_name": item["name"], "item_price": item["price"],
    }
    await state.set_state(GameStates.waiting_game_id)
    price_text = f"{actual_price} ₽" if actual_price > 0 else f"монетами ({coins_used})"
    await call.message.edit_text(
        f"🎮 <b>{game['name']} — {item['name']}</b>\n\n"
        f"💰 К оплате: {price_text}\n\n"
        f"📝 Введите ваш <b>игровой ID (тег игрока)</b>:",
        parse_mode="HTML", reply_markup=cancel_kb()
    )
    await call.answer()


@router.message(GameStates.waiting_game_id)
async def process_game_id(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    purchase = _purchase_data.get(user_id)
    if not purchase:
        await state.clear()
        await message.answer("Ошибка: начните заново.", reply_markup=main_menu())
        return

    game_id_input = message.text.strip()
    actual_price = purchase["actual_price"]
    coins_used = purchase["coins_used"]
    await state.clear()

    if actual_price == 0:
        user = get_user(user_id)
        if user["balance"] < coins_used:
            await message.answer("❌ Недостаточно монет.", reply_markup=main_menu())
            _purchase_data.pop(user_id, None)
            return
        update_balance(user_id, -coins_used)
        order_id = create_order(user_id, "game", purchase["item_id"], purchase["item_name"],
                                purchase["item_price"], coins_used, game_id=game_id_input)
        complete_order(order_id)
        _purchase_data.pop(user_id, None)

        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id,
                    f"🛒 <b>Новый заказ #{order_id}</b>\n👤 {user_id}\n"
                    f"🎮 {purchase['item_name']}\n🎯 ID: <code>{game_id_input}</code>\n"
                    f"🪙 Монет: {coins_used}", parse_mode="HTML")
            except Exception:
                pass

        await message.answer(
            f"✅ <b>Заказ #{order_id} оформлен!</b>\n\n"
            f"🎮 {purchase['item_name']}\n🎯 Ваш ID: <code>{game_id_input}</code>\n"
            f"🪙 Списано монет: {coins_used}\n\n⏳ Товар зачислят в течение 15 минут.",
            parse_mode="HTML", reply_markup=main_menu()
        )
    else:
        order_id = create_order(user_id, "game", purchase["item_id"], purchase["item_name"],
                                actual_price, coins_used, game_id=game_id_input)
        _purchase_data.pop(user_id, None)
        await bot.send_invoice(
            chat_id=user_id,
            title=purchase["item_name"],
            description=f"Игровой ID: {game_id_input}",
            payload=f"game:{purchase['game_id']}:{purchase['item_id']}:{order_id}",
            provider_token=PAYMENT_TOKEN,
            currency="RUB",
            prices=[LabeledPrice(label=purchase["item_name"], amount=actual_price * 100)],
        )
