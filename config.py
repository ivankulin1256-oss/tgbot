BOT_TOKEN = "8700479723:AAFfK1E7aP0b2z1avVnSty6pH3dUo4-g0VA"
ADMIN_IDS = [8116066444]
PAYMENT_TOKEN = "YOUR_PAYMENT_TOKEN"

VPN_PLANS = {
    "trial": {
        "name": "🆓 Trial",
        "duration_days": 7,
        "price": 0,
        "description": "7 дней бесплатно. Скорость до 50 Мбит/с. 1 устройство.",
        "speed": "50 Мбит/с",
        "devices": 1,
    },
    "pro_month": {
        "name": "⚡ Pro — 1 месяц",
        "duration_days": 30,
        "price": 199,
        "description": "30 дней. Безлимит. До 1 Гбит/с. 5 устройств.",
        "speed": "1 Гбит/с",
        "devices": 5,
    },
    "pro_3month": {
        "name": "🔥 Pro — 3 месяца",
        "duration_days": 90,
        "price": 499,
        "description": "90 дней. Безлимит. До 1 Гбит/с. 5 устройств. Выгода 16%.",
        "speed": "1 Гбит/с",
        "devices": 5,
    },
    "pro_year": {
        "name": "👑 Pro — 1 год",
        "duration_days": 365,
        "price": 1499,
        "description": "365 дней. Безлимит. До 1 Гбит/с. 10 устройств. Выгода 37%.",
        "speed": "1 Гбит/с",
        "devices": 10,
    },
}

REFERRAL_BONUS_INVITER = 50
REFERRAL_BONUS_INVITED = 25

GAME_CATALOG = {
    "brawlstars": {
        "name": "🥊 Brawl Stars",
        "emoji": "🥊",
        "items": [
            {"id": "bs_gems_30",   "name": "30 Гемов",          "price": 59},
            {"id": "bs_gems_80",   "name": "80 Гемов",          "price": 149},
            {"id": "bs_gems_170",  "name": "170 Гемов",         "price": 299},
            {"id": "bs_gems_360",  "name": "360 Гемов",         "price": 599},
            {"id": "bs_gems_950",  "name": "950 Гемов",         "price": 1499},
            {"id": "bs_gems_2000", "name": "2000 Гемов",        "price": 2999},
            {"id": "bs_pass",      "name": "Brawl Pass",        "price": 169},
            {"id": "bs_pass_plus", "name": "Brawl Pass+",       "price": 349},
            {"id": "bs_starr_300", "name": "300 StarrDrops",    "price": 399},
            {"id": "bs_coins_200", "name": "200 монет",         "price": 49},
        ],
    },
    "clashroyale": {
        "name": "👑 Clash Royale",
        "emoji": "👑",
        "items": [
            {"id": "cr_gems_80",    "name": "80 Гемов",         "price": 149},
            {"id": "cr_gems_500",   "name": "500 Гемов",        "price": 749},
            {"id": "cr_gems_1200",  "name": "1200 Гемов",       "price": 1699},
            {"id": "cr_gems_6500",  "name": "6500 Гемов",       "price": 7999},
            {"id": "cr_pass",       "name": "Royale Pass",      "price": 269},
            {"id": "cr_gold_1000",  "name": "1000 золота",      "price": 79},
            {"id": "cr_gold_5000",  "name": "5000 золота",      "price": 349},
            {"id": "cr_chest_mega", "name": "Мега-сундук",      "price": 499},
        ],
    },
    "clashofclans": {
        "name": "⚔️ Clash of Clans",
        "emoji": "⚔️",
        "items": [
            {"id": "coc_gems_80",   "name": "80 Гемов",         "price": 149},
            {"id": "coc_gems_500",  "name": "500 Гемов",        "price": 749},
            {"id": "coc_gems_1200", "name": "1200 Гемов",       "price": 1699},
            {"id": "coc_gems_2500", "name": "2500 Гемов",       "price": 3399},
            {"id": "coc_gems_6500", "name": "6500 Гемов",       "price": 7999},
            {"id": "coc_pass",      "name": "Gold Pass",        "price": 269},
            {"id": "coc_builder",   "name": "Builder Base Pass","price": 169},
            {"id": "coc_wall_ring", "name": "10 колец стен",    "price": 199},
        ],
    },
}

DB_PATH = "bot_database.db"
