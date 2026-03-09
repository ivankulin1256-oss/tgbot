from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_stats, create_promo, get_all_promos, update_balance, get_user
from config import ADMIN_IDS

router = Router()


def is_admin(user_id):
    return user_id in ADMIN_IDS


class AdminStates(StatesGroup):
    waiting_promo = State()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats = get_stats()
    await message.answer(
        f"🔧 <b>Админ-панель</b>\n\n"
        f"👥 Пользователей: {stats['total_users']}\n"
        f"🛡 Платных VPN: {stats['paid_subs']}\n"
        f"📦 Заказов выполнено: {stats['total_orders']}\n"
        f"💰 Общая выручка: {stats['total_revenue']} ₽\n\n"
        f"<b>Команды:</b>\n"
        f"/admin_promo — создать промокод\n"
        f"/admin_promos — список промокодов\n"
        f"/admin_balance [id] [сумма] — изменить баланс",
        parse_mode="HTML"
    )


@router.message(Command("admin_promo"))
async def cmd_admin_promo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_promo)
    await message.answer(
        "📝 Введите данные промокода:\n"
        "<code>КОД ТИП СКИДКА ЛИМИТ</code>\n\n"
        "Типы: <b>coins</b> | <b>percent</b>\n\n"
        "Пример: <code>WELCOME coins 100 50</code>",
        parse_mode="HTML"
    )


@router.message(AdminStates.waiting_promo)
async def process_promo_creation(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    parts = message.text.strip().split()
    if len(parts) < 4:
        await message.answer("❌ Неверный формат. Пример: WELCOME coins 100 50")
        return
    code, type_, discount_str, max_uses_str = parts[0], parts[1], parts[2], parts[3]
    if type_ not in ("coins", "percent"):
        await message.answer("❌ Тип: coins или percent")
        return
    try:
        discount, max_uses = int(discount_str), int(max_uses_str)
    except ValueError:
        await message.answer("❌ Скидка и лимит — числа")
        return

    success = create_promo(code, discount, type_, max_uses)
    await state.clear()
    if success:
        await message.answer(f"✅ Промокод <code>{code.upper()}</code> создан!\n{type_} | {discount} | лимит {max_uses}", parse_mode="HTML")
    else:
        await message.answer("❌ Промокод с таким кодом уже существует.")


@router.message(Command("admin_promos"))
async def cmd_promos(message: Message):
    if not is_admin(message.from_user.id):
        return
    promos = get_all_promos()
    if not promos:
        await message.answer("Промокодов нет.")
        return
    text = "🎟 <b>Промокоды:</b>\n\n"
    for p in promos:
        status = "✅" if p["used_count"] < p["max_uses"] else "❌"
        text += f"{status} <code>{p['code']}</code> — {p['type']} | -{p['discount']} | {p['used_count']}/{p['max_uses']}\n"
    await message.answer(text, parse_mode="HTML")


@router.message(Command("admin_balance"))
async def cmd_balance(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Использование: /admin_balance [user_id] [сумма]")
        return
    try:
        target_id, amount = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("Неверный формат")
        return
    if not get_user(target_id):
        await message.answer("Пользователь не найден")
        return
    update_balance(target_id, amount)
    user = get_user(target_id)
    await message.answer(f"✅ Готово. Баланс {target_id}: {user['balance']} монет")
    try:
        sign = "+" if amount > 0 else ""
        await bot.send_message(target_id, f"💰 Администратор изменил ваш баланс: {sign}{amount} монет\n🪙 Текущий: {user['balance']}")
    except Exception:
        pass


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.")
