import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from database.db import get_or_create_user, get_user, update_balance, get_active_vpn, get_referrals, get_user_orders
from keyboards.kb import main_menu, back_to_main
from config import REFERRAL_BONUS_INVITED, REFERRAL_BONUS_INVITER

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, bot):
    user = message.from_user
    args = message.text.split()
    referred_by = None

    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referred_by = int(args[1].split("_")[1])
            if referred_by == user.id:
                referred_by = None
        except (ValueError, IndexError):
            referred_by = None

    db_user, is_new = get_or_create_user(
        user.id, user.username or "", user.full_name or "", referred_by=referred_by
    )

    if is_new and referred_by:
        update_balance(user.id, REFERRAL_BONUS_INVITED)
        update_balance(referred_by, REFERRAL_BONUS_INVITER)
        try:
            await bot.send_message(
                referred_by,
                f"🎉 По вашей ссылке зарегистрировался новый пользователь!\n"
                f"💰 Вам начислено +{REFERRAL_BONUS_INVITER} монет"
            )
        except Exception:
            pass

    text = (
        f"👋 Добро пожаловать, <b>{user.full_name}</b>!\n\n"
        f"Я — многофункциональный бот:\n"
        f"🛡 <b>VPN</b> — защищённый интернет (Trial + Pro)\n"
        f"🎮 <b>Игровые товары</b> — Brawl Stars, Clash Royale, Clash of Clans\n\n"
    )
    if is_new and referred_by:
        text += f"🎁 Вам начислено <b>+{REFERRAL_BONUS_INVITED} монет</b> за регистрацию!\n\n"
    text += "Выберите раздел в меню ниже 👇"

    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")


@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        await message.answer("Сначала запустите бота командой /start")
        return

    vpn = get_active_vpn(user_id)
    refs = get_referrals(user_id)
    orders = get_user_orders(user_id)

    vpn_status = "❌ Нет активной подписки"
    if vpn:
        exp = datetime.datetime.fromisoformat(vpn["expires_at"])
        days_left = max(0, (exp - datetime.datetime.now()).days)
        vpn_status = f"✅ {vpn['plan'].upper()} — ещё {days_left} дн. (до {exp.strftime('%d.%m.%Y')})"

    text = (
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Имя: {db_user['full_name']}\n"
        f"🪙 Баланс монет: <b>{db_user['balance']}</b>\n\n"
        f"🛡 VPN: {vpn_status}\n\n"
        f"👥 Рефералов: <b>{len(refs)}</b>\n"
        f"📦 Заказов: <b>{len(orders)}</b>\n\n"
        f"📅 Регистрация: {db_user['created_at'][:10]}"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=back_to_main())


@router.message(F.text == "📦 Мои заказы")
async def cmd_orders(message: Message):
    orders = get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📦 У вас пока нет заказов.", reply_markup=back_to_main())
        return

    text = "📦 <b>Ваши последние заказы:</b>\n\n"
    for o in orders:
        icon = "✅" if o["status"] == "completed" else "⏳"
        text += f"{icon} #{o['id']} — {o['item_name']}\n   💰 {o['amount']} ₽  📅 {o['created_at'][:16]}\n\n"

    await message.answer(text, parse_mode="HTML", reply_markup=back_to_main())


@router.callback_query(F.data == "back_main")
async def callback_back_main(call: CallbackQuery):
    await call.message.answer("Главное меню 👇", reply_markup=main_menu())
    await call.message.delete()
    await call.answer()


@router.callback_query(F.data == "cancel_state")
async def callback_cancel(call: CallbackQuery):
    await call.message.answer("Отменено.", reply_markup=main_menu())
    await call.message.delete()
    await call.answer()
