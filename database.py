import sqlite3

db = sqlite3.connect("bot.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    phone TEXT UNIQUE,
    status TEXT DEFAULT 'waiting'
)
""")

db.commit()


def save_phone(user_id, phone):
    try:
        cursor.execute(
            "INSERT INTO users (user_id, phone) VALUES (?, ?)",
            (user_id, phone)
        )
        db.commit()
        return True

    except sqlite3.IntegrityError:
        return False


def get_saved_phone(user_id):
    cursor.execute(
        "SELECT phone FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return None
def phone_exists(phone):
    cursor.execute(
        "SELECT 1 FROM users WHERE phone = ?",
        (phone,)
    )

    return cursor.fetchone() is not None