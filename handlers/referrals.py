from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import get_user, get_referrals
from config import REFERRAL_BONUS_INVITER, REFERRAL_BONUS_INVITED

router = Router()


@router.message(F.text == "👥 Рефералы")
async def show_referrals(message: Message, bot: Bot):
    user_id = message.from_user.id
    user = get_user(user_id)
    refs = get_referrals(user_id)
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start=ref_{user_id}"

    text = (
        f"👥 <b>Реферальная система</b>\n\n"
        f"🔗 Ваша ссылка:\n<code>{ref_link}</code>\n\n"
        f"💰 <b>Вознаграждение:</b>\n"
        f"• За каждого приглашённого: +{REFERRAL_BONUS_INVITER} монет\n"
        f"• Новый пользователь получает: +{REFERRAL_BONUS_INVITED} монет\n\n"
        f"👥 Приглашено: <b>{len(refs)}</b> человек\n"
        f"💎 Заработано: <b>{len(refs) * REFERRAL_BONUS_INVITER}</b> монет\n"
        f"🪙 Ваш баланс: <b>{user['balance']}</b> монет"
    )

    if refs:
        text += "\n\n📋 <b>Рефералы:</b>\n"
        for r in refs[:10]:
            name = r["full_name"] or r["username"] or f"id{r['user_id']}"
            text += f"  • {name} — {r['created_at'][:10]}\n"
        if len(refs) > 10:
            text += f"  ...и ещё {len(refs) - 10}\n"

    kb = InlineKeyboardBuilder()
    kb.button(text="📤 Поделиться ссылкой", switch_inline_query=f"Присоединяйся! {ref_link}")
    await message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())
