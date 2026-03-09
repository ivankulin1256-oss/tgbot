import sqlite3
import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            full_name   TEXT,
            balance     INTEGER DEFAULT 0,
            referred_by INTEGER,
            ref_count   INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS vpn_subscriptions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            plan        TEXT,
            expires_at  TEXT,
            active      INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            item_type   TEXT,
            item_id     TEXT,
            item_name   TEXT,
            amount      INTEGER,
            coins_used  INTEGER DEFAULT 0,
            status      TEXT DEFAULT 'pending',
            game_id     TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT UNIQUE,
            discount    INTEGER,
            type        TEXT,
            max_uses    INTEGER DEFAULT 1,
            used_count  INTEGER DEFAULT 0,
            expires_at  TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses (
            user_id INTEGER,
            code    TEXT,
            PRIMARY KEY (user_id, code)
        )
    """)
    conn.commit()
    conn.close()


def get_or_create_user(user_id, username, full_name, referred_by=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    is_new = False
    if not row:
        is_new = True
        c.execute(
            "INSERT INTO users (user_id, username, full_name, referred_by) VALUES (?,?,?,?)",
            (user_id, username, full_name, referred_by)
        )
        conn.commit()
        if referred_by:
            c.execute("UPDATE users SET ref_count = ref_count + 1 WHERE user_id=?", (referred_by,))
            conn.commit()
        c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
    conn.close()
    return dict(row), is_new


def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_balance(user_id, delta):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (delta, user_id))
    conn.commit()
    conn.close()


def get_referrals(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE referred_by=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_active_vpn(user_id):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute(
        "SELECT * FROM vpn_subscriptions WHERE user_id=? AND active=1 AND expires_at > ? ORDER BY expires_at DESC LIMIT 1",
        (user_id, now)
    )
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def has_used_trial(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM vpn_subscriptions WHERE user_id=? AND plan='trial'", (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None


def create_vpn_subscription(user_id, plan, duration_days):
    conn = get_conn()
    c = conn.cursor()
    expires_at = (datetime.datetime.now() + datetime.timedelta(days=duration_days)).isoformat()
    c.execute(
        "INSERT INTO vpn_subscriptions (user_id, plan, expires_at) VALUES (?,?,?)",
        (user_id, plan, expires_at)
    )
    conn.commit()
    conn.close()
    return expires_at


def create_order(user_id, item_type, item_id, item_name, amount, coins_used=0, game_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (user_id, item_type, item_id, item_name, amount, coins_used, game_id) VALUES (?,?,?,?,?,?,?)",
        (user_id, item_type, item_id, item_name, amount, coins_used, game_id)
    )
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id


def complete_order(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE orders SET status='completed' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


def get_user_orders(user_id, limit=10):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_promo(code):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM promo_codes WHERE code=?", (code.upper(),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def has_used_promo(user_id, code):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM promo_uses WHERE user_id=? AND code=?", (user_id, code.upper()))
    row = c.fetchone()
    conn.close()
    return row is not None


def use_promo(user_id, code):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO promo_uses (user_id, code) VALUES (?,?)", (user_id, code.upper()))
    c.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE code=?", (code.upper(),))
    conn.commit()
    conn.close()


def create_promo(code, discount, type_, max_uses, expires_at=None):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO promo_codes (code, discount, type, max_uses, expires_at) VALUES (?,?,?,?,?)",
            (code.upper(), discount, type_, max_uses, expires_at)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_all_promos():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM promo_codes ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM users")
    total_users = c.fetchone()["cnt"]
    c.execute("SELECT COUNT(*) as cnt FROM vpn_subscriptions WHERE plan != 'trial'")
    paid_subs = c.fetchone()["cnt"]
    c.execute("SELECT COUNT(*) as cnt FROM orders WHERE status='completed'")
    total_orders = c.fetchone()["cnt"]
    c.execute("SELECT SUM(amount) as s FROM orders WHERE status='completed'")
    total_revenue = c.fetchone()["s"] or 0
    conn.close()
    return {
        "total_users": total_users,
        "paid_subs": paid_subs,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
    }
