import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.filters import Command

from database.db import get_user, update_balance, has_used_trial, create_vpn_subscription, get_active_vpn, create_order, complete_order
from keyboards.kb import vpn_menu, vpn_plan_detail, vpn_buy_menu, back_to_main, main_menu
from config import VPN_PLANS, PAYMENT_TOKEN

router = Router()


@router.message(F.text == "🛡 VPN")
async def show_vpn(message: Message):
    active = get_active_vpn(message.from_user.id)
    header = ""
    if active:
        exp = datetime.datetime.fromisoformat(active["expires_at"])
        days_left = max(0, (exp - datetime.datetime.now()).days)
        header = f"✅ Активная подписка: <b>{active['plan'].upper()}</b> — {days_left} дн.\n\n"
    await message.answer(header + "🛡 <b>VPN-подписки</b>\n\nВыберите тариф:", reply_markup=vpn_menu(), parse_mode="HTML")


@router.callback_query(F.data == "vpn_menu")
async def cb_vpn_menu(call: CallbackQuery):
    active = get_active_vpn(call.from_user.id)
    header = ""
    if active:
        exp = datetime.datetime.fromisoformat(active["expires_at"])
        days_left = max(0, (exp - datetime.datetime.now()).days)
        header = f"✅ Активная подписка: <b>{active['plan'].upper()}</b> — {days_left} дн.\n\n"
    await call.message.edit_text(header + "🛡 <b>VPN-подписки</b>\n\nВыберите тариф:", reply_markup=vpn_menu(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("vpn_plan:"))
async def cb_vpn_plan(call: CallbackQuery):
    plan_id = call.data.split(":")[1]
    plan = VPN_PLANS.get(plan_id)
    if not plan:
        await call.answer("Тариф не найден")
        return
    text = (
        f"{plan['name']}\n\n"
        f"📋 {plan['description']}\n\n"
        f"⚡ Скорость: {plan['speed']}\n"
        f"📱 Устройств: {plan['devices']}\n"
        f"⏳ Срок: {plan['duration_days']} дней\n"
        f"💰 Цена: {'Бесплатно' if plan['price'] == 0 else str(plan['price']) + ' ₽'}"
    )
    await call.message.edit_text(text, reply_markup=vpn_plan_detail(plan_id))
    await call.answer()


@router.callback_query(F.data.startswith("vpn_activate:"))
async def cb_vpn_trial(call: CallbackQuery):
    user_id = call.from_user.id
    if has_used_trial(user_id):
        await call.answer("❌ Trial уже был использован", show_alert=True)
        return
    if get_active_vpn(user_id):
        await call.answer("У вас уже есть активная подписка", show_alert=True)
        return
    plan = VPN_PLANS["trial"]
    expires = create_vpn_subscription(user_id, "trial", plan["duration_days"])
    exp_date = datetime.datetime.fromisoformat(expires).strftime("%d.%m.%Y")
    key = f"vpn://trial_{user_id}_{datetime.datetime.now().strftime('%Y%m%d')}"
    await call.message.edit_text(
        f"✅ <b>Trial VPN активирован!</b>\n\n"
        f"⏳ Действует до: {exp_date}\n"
        f"📱 Устройств: {plan['devices']}\n"
        f"⚡ Скорость: {plan['speed']}\n\n"
        f"🔑 Ключ подключения:\n<code>{key}</code>\n\n"
        f"📖 Используйте приложение Outline или V2Ray",
        parse_mode="HTML", reply_markup=back_to_main()
    )
    await call.answer("🎉 Trial активирован!")


@router.callback_query(F.data.startswith("vpn_buy:"))
async def cb_vpn_buy(call: CallbackQuery):
    plan_id = call.data.split(":")[1]
    plan = VPN_PLANS.get(plan_id)
    if not plan or plan["price"] == 0:
        return
    user = get_user(call.from_user.id)
    coins = user["balance"] if user else 0
    await call.message.edit_text(
        f"💳 <b>Покупка {plan['name']}</b>\n\n"
        f"💰 Сумма: <b>{plan['price']} ₽</b>\n"
        f"🪙 Ваши монеты: {coins}",
        reply_markup=vpn_buy_menu(plan_id, coins),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("invoice:vpn:"))
async def cb_vpn_invoice(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    plan_id, coins_str = parts[2], parts[3]
    coins_used = int(coins_str)
    user_id = call.from_user.id
    user = get_user(user_id)
    plan = VPN_PLANS.get(plan_id)
    if not plan:
        await call.answer("Ошибка")
        return

    actual_price = max(0, plan["price"] - coins_used)

    if actual_price == 0:
        if user["balance"] < coins_used:
            await call.answer("❌ Недостаточно монет", show_alert=True)
            return
        update_balance(user_id, -coins_used)
        order_id = create_order(user_id, "vpn", plan_id, plan["name"], plan["price"], coins_used)
        complete_order(order_id)
        expires = create_vpn_subscription(user_id, plan_id, plan["duration_days"])
        exp_date = datetime.datetime.fromisoformat(expires).strftime("%d.%m.%Y")
        key = f"vpn://pro_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        await call.message.edit_text(
            f"✅ <b>VPN {plan['name']} активирован!</b>\n\n"
            f"🪙 Списано монет: {coins_used}\n"
            f"⏳ Действует до: {exp_date}\n\n"
            f"🔑 Ваш ключ:\n<code>{key}</code>",
            parse_mode="HTML", reply_markup=back_to_main()
        )
        await call.answer("✅ Оплачено монетами!")
        return

    order_id = create_order(user_id, "vpn", plan_id, plan["name"], actual_price, coins_used)
    await bot.send_invoice(
        chat_id=user_id,
        title=plan["name"],
        description=plan["description"],
        payload=f"vpn:{plan_id}:{order_id}:{coins_used}",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label=plan["name"], amount=actual_price * 100)],
    )
    await call.answer()


@router.pre_checkout_query()
async def pre_checkout(query, bot: Bot):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    parts = payload.split(":")
    item_type, user_id = parts[0], message.from_user.id

    if item_type == "vpn":
        plan_id, order_id, coins_used = parts[1], int(parts[2]), int(parts[3]) if len(parts) > 3 else 0
        plan = VPN_PLANS[plan_id]
        if coins_used:
            update_balance(user_id, -coins_used)
        complete_order(order_id)
        expires = create_vpn_subscription(user_id, plan_id, plan["duration_days"])
        exp_date = datetime.datetime.fromisoformat(expires).strftime("%d.%m.%Y")
        key = f"vpn://pro_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        await message.answer(
            f"✅ <b>Оплата прошла!</b>\n\n🛡 VPN <b>{plan['name']}</b> активирован\n"
            f"⏳ До: {exp_date}\n\n🔑 Ключ:\n<code>{key}</code>",
            parse_mode="HTML", reply_markup=main_menu()
        )
    elif item_type == "game":
        game_id, item_id, order_id = parts[1], parts[2], int(parts[3])
        complete_order(order_id)
        from config import GAME_CATALOG
        game = GAME_CATALOG.get(game_id, {})
        item = next((i for i in game.get("items", []) if i["id"] == item_id), None)
        await message.answer(
            f"✅ <b>Оплата прошла!</b>\n\n🎮 {game.get('name','')}: <b>{item['name'] if item else item_id}</b>\n\n"
            f"Заказ #{order_id} будет выполнен в течение 15 минут.",
            parse_mode="HTML", reply_markup=main_menu()
        )
