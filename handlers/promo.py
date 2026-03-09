import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_user, update_balance, get_promo, has_used_promo, use_promo
from keyboards.kb import main_menu, cancel_kb

router = Router()


class PromoStates(StatesGroup):
    waiting_code = State()


@router.message(F.text == "🎟 Промокод")
async def ask_promo(message: Message, state: FSMContext):
    await state.set_state(PromoStates.waiting_code)
    await message.answer(
        "🎟 <b>Введите промокод:</b>\n\n"
        "Промокоды дают монеты или скидку на покупки.",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(PromoStates.waiting_code)
async def process_promo(message: Message, state: FSMContext):
    await state.clear()
    code = message.text.strip().upper()
    user_id = message.from_user.id

    promo = get_promo(code)
    if not promo:
        await message.answer("❌ Промокод не найден.", reply_markup=main_menu())
        return

    if promo["expires_at"]:
        try:
            if datetime.datetime.now() > datetime.datetime.fromisoformat(promo["expires_at"]):
                await message.answer("❌ Срок действия промокода истёк.", reply_markup=main_menu())
                return
        except ValueError:
            pass

    if promo["used_count"] >= promo["max_uses"]:
        await message.answer("❌ Лимит использований исчерпан.", reply_markup=main_menu())
        return

    if has_used_promo(user_id, code):
        await message.answer("❌ Вы уже использовали этот промокод.", reply_markup=main_menu())
        return

    use_promo(user_id, code)

    if promo["type"] == "coins":
        update_balance(user_id, promo["discount"])
        user = get_user(user_id)
        await message.answer(
            f"✅ <b>Промокод активирован!</b>\n\n"
            f"🪙 Начислено: <b>+{promo['discount']} монет</b>\n"
            f"💰 Баланс: {user['balance']} монет",
            parse_mode="HTML", reply_markup=main_menu()
        )
    else:
        await message.answer(
            f"✅ <b>Промокод активирован!</b>\n\n"
            f"🏷 Скидка: <b>{promo['discount']}%</b> на следующую покупку.",
            parse_mode="HTML", reply_markup=main_menu()
        )
