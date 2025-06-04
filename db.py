import aiosqlite

DB_PATH = "cards.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                front TEXT,
                back TEXT,
                ease INTEGER DEFAULT 2,
                due INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def add_card(user_id: int, front: str, back: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO cards (user_id, front, back) VALUES (?, ?, ?)",
            (user_id, front, back)
        )
        await db.commit()

async def get_due_cards(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, front, back, ease FROM cards WHERE user_id = ? AND due <= strftime('%s','now') ORDER BY due ASC",
            (user_id,)
        )
        return await cursor.fetchall()

async def update_card_ease_and_due(card_id: int, ease: int, interval: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE cards SET ease = ?, due = strftime('%s','now') + ? WHERE id = ?",
            (ease, interval, card_id)
        )
        await db.commit()

async def get_all_cards(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, front, back FROM cards WHERE user_id = ?",
            (user_id,)
        )
        return await cursor.fetchall()

async def get_card(card_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, front, back FROM cards WHERE id = ?",
            (card_id,)
        )
        return await cursor.fetchone()

async def update_card(card_id: int, new_front: str, new_back: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE cards SET front = ?, back = ? WHERE id = ?",
            (new_front, new_back, card_id)
        )
        await db.commit()

async def delete_card(card_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM cards WHERE id = ?",
            (card_id,)
        )
        await db.commit()

async def reset_due_cards(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE cards SET due = 0 WHERE user_id = ?", (user_id,))
        await db.commit()
