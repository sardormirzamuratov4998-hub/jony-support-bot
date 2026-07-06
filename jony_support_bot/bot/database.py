import sqlite3
from datetime import datetime
from bot.config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            branch TEXT,
            role TEXT DEFAULT 'pending',      -- pending / support / examiner / admin
            status TEXT DEFAULT 'pending',    -- pending / approved / rejected
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            support_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            branch TEXT,
            day_type TEXT,   -- toq / juft
            time TEXT,
            created_at TEXT,
            FOREIGN KEY (support_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


# ---------------- USERS ----------------

def get_user_by_telegram_id(telegram_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def create_pending_user(telegram_id: int, first_name: str, last_name: str, phone: str, branch: str = None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO users (telegram_id, first_name, last_name, phone, branch, role, status, created_at)
           VALUES (?, ?, ?, ?, ?, 'pending', 'pending', ?)""",
        (telegram_id, first_name, last_name, phone, branch, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def approve_user(user_id: int, role: str):
    conn = get_connection()
    conn.execute("UPDATE users SET role = ?, status = 'approved' WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()


def reject_user(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE users SET status = 'rejected' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def delete_user(user_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM groups WHERE support_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def update_user_field(user_id: int, field: str, value: str):
    allowed = {"first_name", "last_name", "phone", "branch"}
    if field not in allowed:
        raise ValueError("Ruxsat etilmagan maydon")
    conn = get_connection()
    conn.execute(f"UPDATE users SET {field} = ? WHERE id = ?", (value, user_id))
    conn.commit()
    conn.close()


def search_supports(query: str):
    conn = get_connection()
    like = f"%{query.strip()}%"
    rows = conn.execute(
        """SELECT * FROM users
           WHERE role = 'support' AND status = 'approved'
           AND (first_name LIKE ? OR last_name LIKE ?)""",
        (like, like),
    ).fetchall()
    conn.close()
    return rows


def get_pending_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users WHERE status = 'pending'").fetchall()
    conn.close()
    return rows


def get_all_supports():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM users WHERE role = 'support' AND status = 'approved' ORDER BY branch, last_name"
    ).fetchall()
    conn.close()
    return rows


def get_branch_stats():
    conn = get_connection()
    rows = conn.execute(
        """SELECT branch, COUNT(*) as support_count
           FROM users WHERE role = 'support' AND status = 'approved'
           GROUP BY branch"""
    ).fetchall()
    group_rows = conn.execute(
        """SELECT u.branch as branch, COUNT(g.id) as group_count
           FROM groups g JOIN users u ON u.id = g.support_id
           GROUP BY u.branch"""
    ).fetchall()
    conn.close()
    return rows, group_rows


# ---------------- GROUPS ----------------

def add_group(support_id: int, name: str, branch: str, day_type: str, time: str):
    conn = get_connection()
    conn.execute(
        """INSERT INTO groups (support_id, name, branch, day_type, time, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (support_id, name, branch, day_type, time, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def update_group(group_id: int, name: str, branch: str, day_type: str, time: str):
    conn = get_connection()
    conn.execute(
        "UPDATE groups SET name = ?, branch = ?, day_type = ?, time = ? WHERE id = ?",
        (name, branch, day_type, time, group_id),
    )
    conn.commit()
    conn.close()


def delete_group(group_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
    conn.commit()
    conn.close()


def get_group_by_id(group_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
    conn.close()
    return row


def get_groups_by_support(support_id: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM groups WHERE support_id = ? ORDER BY day_type, time", (support_id,)
    ).fetchall()
    conn.close()
    return rows
