import aiosqlite
import json
from typing import Dict, List, Optional


class Database:
    def __init__(self, path: str):
        self.path = path
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.create_tables()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def create_tables(self):
        await self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS admins(
            user_id INTEGER PRIMARY KEY,
            is_main BOOLEAN DEFAULT 0,
            vacation BOOLEAN DEFAULT 0,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS submissions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message_id INTEGER,
            admin_messages TEXT,
            media_group_id TEXT,
            content_type TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS config(
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """)
        await self.conn.commit()

    async def add_admin(self, user_id: int, is_main: bool = False):
        await self.conn.execute(
            "INSERT OR IGNORE INTO admins(user_id, is_main) VALUES(?,?)",
            (user_id, int(is_main)),
        )
        await self.conn.commit()

    async def get_admin(self, user_id: int):
        cur = await self.conn.execute(
            "SELECT user_id, is_main, vacation FROM admins WHERE user_id=?",
            (user_id,),
        )
        return await cur.fetchone()

    async def get_active_admins(self) -> List[int]:
        cur = await self.conn.execute(
            "SELECT user_id FROM admins WHERE vacation=0"
        )
        rows = await cur.fetchall()
        return [r[0] for r in rows]

    async def active_admin_count(self) -> int:
        cur = await self.conn.execute(
            "SELECT COUNT(*) FROM admins WHERE vacation=0"
        )
        return (await cur.fetchone())[0]

    async def toggle_vacation(self, user_id: int) -> bool:
        cur = await self.conn.execute(
            "SELECT vacation FROM admins WHERE user_id=?",
            (user_id,),
        )
        row = await cur.fetchone()
        new_value = 0 if row[0] else 1
        await self.conn.execute(
            "UPDATE admins SET vacation=? WHERE user_id=?",
            (new_value, user_id),
        )
        await self.conn.commit()
        return bool(new_value)

    async def create_submission(
        self,
        user_id: int,
        message_id: int,
        content_type: str,
        media_group_id: Optional[str] = None,
    ) -> int:
        cur = await self.conn.execute(
            """INSERT INTO submissions(user_id,user_message_id,admin_messages,
            media_group_id,content_type,status)
            VALUES(?,?,?,?,?,'pending')""",
            (user_id, message_id, json.dumps({}), media_group_id, content_type),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def set_admin_message(self, submission_id: int, admin_id: int, msg_id: int):
        cur = await self.conn.execute(
            "SELECT admin_messages FROM submissions WHERE id=?",
            (submission_id,),
        )
        data = json.loads((await cur.fetchone())[0])
        data[str(admin_id)] = msg_id
        await self.conn.execute(
            "UPDATE submissions SET admin_messages=? WHERE id=?",
            (json.dumps(data), submission_id),
        )
        await self.conn.commit()

    async def get_submission(self, submission_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM submissions WHERE id=?",
            (submission_id,),
        )
        return await cur.fetchone()

    async def update_status_atomic(self, submission_id: int, new_status: str) -> bool:
        cur = await self.conn.execute(
            "UPDATE submissions SET status=? WHERE id=? AND status='pending'",
            (new_status, submission_id),
        )
        await self.conn.commit()
        return cur.rowcount > 0

    async def get_admin_messages(self, submission_id: int) -> Dict[str, int]:
        cur = await self.conn.execute(
            "SELECT admin_messages FROM submissions WHERE id=?",
            (submission_id,),
        )
        row = await cur.fetchone()
        return json.loads(row[0]) if row else {}
