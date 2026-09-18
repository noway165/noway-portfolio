"""
Cơ sở dữ liệu SQLite: bài viết, dự án, clip, tin nhắn, bình luận, lượt xem.

File dữ liệu nằm ở instance/site.db (không đưa lên GitHub).
Lần chạy đầu tiên, bảng bài viết và dự án được nạp sẵn từ data.py.
"""
import re
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import current_app, g

import data

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id        INTEGER PRIMARY KEY,
    slug      TEXT UNIQUE NOT NULL,
    title     TEXT NOT NULL,
    date      TEXT NOT NULL,
    tags      TEXT NOT NULL DEFAULT '',
    excerpt   TEXT NOT NULL DEFAULT '',
    body      TEXT NOT NULL DEFAULT '',
    published INTEGER NOT NULL DEFAULT 1,
    views     INTEGER NOT NULL DEFAULT 0,
    likes     INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS projects (
    id       INTEGER PRIMARY KEY,
    title    TEXT NOT NULL,
    year     TEXT NOT NULL DEFAULT '',
    status   TEXT NOT NULL DEFAULT '',
    live     INTEGER NOT NULL DEFAULT 0,
    text     TEXT NOT NULL DEFAULT '',
    tags     TEXT NOT NULL DEFAULT '',
    links    TEXT NOT NULL DEFAULT '',
    position INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS clips (
    id       INTEGER PRIMARY KEY,
    title    TEXT NOT NULL,
    video_id TEXT NOT NULL,
    url      TEXT NOT NULL,
    game     TEXT NOT NULL DEFAULT '',
    created  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS comments (
    id      INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    name    TEXT NOT NULL,
    body    TEXT NOT NULL,
    created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    contact TEXT NOT NULL DEFAULT '',
    body    TEXT NOT NULL,
    created TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS page_views (
    path  TEXT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


# ------------------------------------------------------------ KẾT NỐI
def db_path():
    return Path(current_app.instance_path) / "site.db"


def get_db():
    """Một kết nối cho mỗi request, tự đóng khi request xong."""
    if "db" not in g:
        g.db = sqlite3.connect(db_path())
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def query(sql, args=(), one=False):
    rows = get_db().execute(sql, args).fetchall()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    conn = get_db()
    cur = conn.execute(sql, args)
    conn.commit()
    return cur


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ------------------------------------------------------------ KHỞI TẠO
def init_app(app):
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        conn = get_db()
        conn.executescript(SCHEMA)
        seed(conn)
        conn.commit()
        app.secret_key = get_setting("secret_key") or _new_secret()


def _new_secret():
    key = secrets.token_hex(32)
    set_setting("secret_key", key)
    return key


def seed(conn):
    """Nạp bài viết và dự án mẫu từ data.py — chỉ khi bảng còn trống."""
    if not conn.execute("SELECT 1 FROM posts LIMIT 1").fetchone():
        for p in data.SEED_POSTS:
            conn.execute(
                "INSERT INTO posts (slug, title, date, tags, excerpt, body) VALUES (?, ?, ?, ?, ?, ?)",
                (p["slug"], p["title"], p["date"], ", ".join(p["tags"]), p["excerpt"], "\n\n".join(p["body"])),
            )
    if not conn.execute("SELECT 1 FROM projects LIMIT 1").fetchone():
        for i, p in enumerate(data.SEED_PROJECTS):
            links = "\n".join(f"{l['label']} | {l['url']}" for l in p.get("links", []))
            conn.execute(
                "INSERT INTO projects (title, year, status, live, text, tags, links, position) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (p["title"], p["year"], p["status"], int(p.get("live", False)), p["text"],
                 ", ".join(p["tags"]), links, i),
            )


# ------------------------------------------------------------ CÀI ĐẶT
def get_setting(key):
    row = query("SELECT value FROM settings WHERE key = ?", (key,), one=True)
    return row["value"] if row else None


def set_setting(key, value):
    execute("INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))


# ------------------------------------------------------------ CHUYỂN ĐỔI
def split_tags(text):
    return [t.strip() for t in (text or "").split(",") if t.strip()]


def split_blocks(text):
    """Thân bài: các đoạn cách nhau bằng một dòng trống."""
    return [b.strip() for b in re.split(r"\n\s*\n", (text or "").replace("\r\n", "\n")) if b.strip()]


def parse_links(text):
    """Mỗi dòng 'Tên | https://...' thành một nút. Link GitHub tự có icon GitHub."""
    links = []
    for line in (text or "").splitlines():
        if "|" not in line:
            continue
        label, url = (part.strip() for part in line.split("|", 1))
        if label and url.startswith(("http://", "https://")):
            icon = "bi-github" if "github.com" in url else "bi-box-arrow-up-right"
            links.append({"label": label, "url": url, "icon": icon})
    return links


TIKTOK_ID = re.compile(r"/video/(\d{8,25})")


def tiktok_id(url):
    """Lấy mã video từ link TikTok đầy đủ (…/@user/video/1234567890)."""
    m = TIKTOK_ID.search(url or "")
    return m.group(1) if m else None


# ------------------------------------------------------------ LƯỢT XEM
def bump_page_view(path):
    execute("INSERT INTO page_views (path, count) VALUES (?, 1) "
            "ON CONFLICT(path) DO UPDATE SET count = count + 1", (path,))


def total_page_views():
    row = query("SELECT COALESCE(SUM(count), 0) AS n FROM page_views", one=True)
    return row["n"]
