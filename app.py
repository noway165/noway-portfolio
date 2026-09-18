"""
Web cá nhân Tăng Thoại Lâm — chạy bằng Flask.

    pip install -r requirements.txt
    python app.py            ->  mở http://127.0.0.1:5000
                                 trang quản trị: http://127.0.0.1:5000/admin

Nội dung cố định (hồ sơ, nhạc, mạng xã hội...) sửa ở data.py.
Bài viết, dự án, clip, tin nhắn, bình luận nằm trong database — quản lý ở /admin.
"""
import math
import secrets
import time
from datetime import date, timedelta
from pathlib import Path

from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)

import data
import db
from media import album_files

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=25 * 1024 * 1024,         # tổng dung lượng một lần tải ảnh lên
    PERMANENT_SESSION_LIFETIME=timedelta(days=365),
    SESSION_COOKIE_SAMESITE="Lax",
)
db.init_app(app)

STATIC_DIR = Path(app.static_folder)


# ------------------------------------------------------------ CHỐNG GIẢ MẠO FORM
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


# Toàn cục cho Jinja để cả macro được import (không kèm context) cũng gọi được
app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def check_csrf():
    """Mọi request POST phải mang mã bí mật đã phát cho trình duyệt này."""
    session.permanent = True
    if request.method != "POST":
        return
    sent = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
    if not sent or not secrets.compare_digest(sent, session.get("_csrf", "")):
        abort(400, "Phiên làm việc đã hết hạn — tải lại trang rồi thử lại.")


# Chặn gửi dồn dập: mỗi địa chỉ IP phải chờ vài giây giữa hai lần gửi
_last_sent = {}


def too_soon(kind, seconds):
    key = (kind, request.remote_addr)
    t = time.monotonic()
    if t - _last_sent.get(key, -1e9) < seconds:
        return True
    _last_sent[key] = t
    return False


# ------------------------------------------------------------------ TIỆN ÍCH
def static_url_if_exists(rel_path):
    """URL của file trong static/ nếu file có thật, không thì None."""
    if rel_path and (STATIC_DIR / rel_path).is_file():
        return url_for("static", filename=rel_path)
    return None


def album_photos(slug):
    return [url_for("static", filename=f"img/gallery/{slug}/{p.name}") for p in album_files(slug)]


def load_albums():
    albums = []
    for album in data.ALBUMS:
        photos = album_photos(album["slug"])
        albums.append({**album, "photos": photos, "cover": photos[0] if photos else None})
    return albums


def to_post(row):
    """Dòng trong database -> bài viết sẵn sàng cho template."""
    blocks = db.split_blocks(row["body"])
    words = sum(len(b.split()) for b in blocks)
    return {
        **dict(row),
        "tags": db.split_tags(row["tags"]),
        "blocks": blocks,
        "day": date.fromisoformat(row["date"]),
        "minutes": max(1, math.ceil(words / 200)),
    }


def load_posts(include_drafts=False):
    """Bài blog mới nhất lên đầu."""
    sql = "SELECT * FROM posts" + ("" if include_drafts else " WHERE published = 1")
    return [to_post(r) for r in db.query(sql + " ORDER BY date DESC, id DESC")]


def load_projects():
    return [
        {**dict(r), "tags": db.split_tags(r["tags"]), "links": db.parse_links(r["links"])}
        for r in db.query("SELECT * FROM projects ORDER BY position, id")
    ]


@app.template_filter("vndate")
def vndate(value):
    """date(2026, 9, 17) -> '17.09.2026'"""
    return value.strftime("%d.%m.%Y")


@app.context_processor
def inject_site():
    """Biến dùng chung cho mọi template: hồ sơ, menu, năm hiện tại."""
    endpoint = request.endpoint
    nav = [
        {**item, "active": endpoint == item["endpoint"] or endpoint in item.get("also", [])}
        for item in data.NAV
    ]
    # Chỉ những kênh có đường dẫn — dùng cho menu điện thoại
    links = [s for s in data.SOCIALS if s.get("url")]
    return {"profile": data.PROFILE, "nav": nav, "social_links": links,
            "year": date.today().year}


# ------------------------------------------------------------ ĐẾM LƯỢT XEM
@app.after_request
def count_view(response):
    """Mỗi trang công khai được đếm một lần cho mỗi người xem."""
    if (request.method == "GET" and response.status_code == 200
            and response.mimetype == "text/html"
            and request.blueprint != "admin" and not session.get("admin")):
        seen = session.get("seen_pages", [])
        if request.path not in seen:
            db.bump_page_view(request.path)
            session["seen_pages"] = (seen + [request.path])[-200:]
    return response


# -------------------------------------------------------------------- TRANG
@app.route("/")
def index():
    albums = load_albums()
    photo_total = sum(len(a["photos"]) for a in albums)
    posts = load_posts()

    stats = [
        {"value": len(load_projects()), "label": "Dự án"},
        {"value": len(posts), "label": "Bài viết"},
        {"value": photo_total or len(albums), "label": "Tấm ảnh" if photo_total else "Album ảnh"},
        {"value": db.total_page_views(), "label": "Lượt xem"},
    ]

    return render_template(
        "index.html",
        avatar=static_url_if_exists(data.PROFILE["avatar"]),
        stats=stats,
        focus=data.FOCUS,
        latest_posts=posts[:2],
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        avatar=static_url_if_exists(data.PROFILE["avatar"]),
        skills=data.SKILLS,
        timeline=data.TIMELINE,
    )


@app.route("/projects")
def projects():
    return render_template("projects.html", projects=load_projects())


@app.route("/blog")
def blog():
    posts = load_posts()
    all_tags = sorted({t for p in posts for t in p["tags"]}, key=str.casefold)

    tag = request.args.get("tag", "").strip()
    q = request.args.get("q", "").strip()
    shown = posts
    if tag:
        shown = [p for p in shown if tag in p["tags"]]
    if q:
        needle = q.casefold()
        shown = [p for p in shown
                 if needle in f"{p['title']} {p['excerpt']} {p['body']} {' '.join(p['tags'])}".casefold()]

    return render_template("blog.html", posts=shown, total=len(posts), all_tags=all_tags, tag=tag, q=q)


@app.route("/blog/<slug>")
def post(slug):
    posts = load_posts()
    slugs = [p["slug"] for p in posts]
    if slug not in slugs:
        abort(404)
    i = slugs.index(slug)
    current = posts[i]

    # Mỗi người xem chỉ tính một lượt cho mỗi bài
    read = session.get("read_posts", [])
    if current["id"] not in read and not session.get("admin"):
        db.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (current["id"],))
        current["views"] += 1
        session["read_posts"] = read + [current["id"]]

    comments = db.query("SELECT * FROM comments WHERE post_id = ? ORDER BY id", (current["id"],))

    # Danh sách xếp mới -> cũ: bài "mới hơn" đứng trước, bài "cũ hơn" đứng sau
    return render_template(
        "post.html",
        post=current,
        comments=comments,
        liked=current["id"] in session.get("liked", []),
        newer=posts[i - 1] if i > 0 else None,
        older=posts[i + 1] if i + 1 < len(posts) else None,
    )


@app.post("/blog/<slug>/comments")
def add_comment(slug):
    row = db.query("SELECT id FROM posts WHERE slug = ? AND published = 1", (slug,), one=True)
    if not row:
        abort(404)
    back = redirect(url_for("post", slug=slug) + "#comments")

    name = request.form.get("name", "").strip()[:60]
    body = request.form.get("body", "").strip()
    if request.form.get("website"):          # ô bẫy: người thật không thấy ô này
        return back
    if not name or len(body) < 2:
        flash("Nhập tên và nội dung bình luận nhé.", "error")
        return back
    if len(body) > 1500:
        flash("Bình luận dài quá — tối đa 1500 ký tự.", "error")
        return back
    if too_soon("comment", 20):
        flash("Bạn gửi nhanh quá, đợi vài giây rồi thử lại.", "error")
        return back

    db.execute("INSERT INTO comments (post_id, name, body, created) VALUES (?, ?, ?, ?)",
               (row["id"], name, body, db.now()))
    session["comment_name"] = name
    flash("Đã đăng bình luận. Cảm ơn bạn!", "ok")
    return back


@app.post("/api/posts/<int:post_id>/like")
def toggle_like(post_id):
    """Thả tim / bỏ tim. Mỗi trình duyệt một tim cho mỗi bài."""
    if not db.query("SELECT 1 FROM posts WHERE id = ? AND published = 1", (post_id,), one=True):
        abort(404)
    liked = session.get("liked", [])
    if post_id in liked:
        db.execute("UPDATE posts SET likes = MAX(likes - 1, 0) WHERE id = ?", (post_id,))
        liked = [i for i in liked if i != post_id]
    else:
        db.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
        liked = liked + [post_id]
    session["liked"] = liked
    count = db.query("SELECT likes FROM posts WHERE id = ?", (post_id,), one=True)["likes"]
    return jsonify(likes=count, liked=post_id in liked)


@app.route("/gaming")
def gaming():
    clips_link = next((s for s in data.SOCIALS if s["name"] == "TikTok"), None)
    discord = next((s for s in data.SOCIALS if s["name"] == "Discord"), None)
    videos = db.query("SELECT * FROM clips ORDER BY created DESC, id DESC")
    return render_template("gaming.html", games=data.GAMES, clips=clips_link,
                           discord=discord, videos=videos)


@app.route("/music")
def music():
    return render_template("music.html", tracks=data.TRACKS)


@app.route("/gallery")
def gallery():
    return render_template("gallery.html", albums=load_albums())


@app.route("/gallery/<slug>")
def album(slug):
    albums = load_albums()
    slugs = [a["slug"] for a in albums]
    if slug not in slugs:
        abort(404)

    i = slugs.index(slug)
    return render_template(
        "album.html",
        album=albums[i],
        prev_album=albums[i - 1],
        next_album=albums[(i + 1) % len(albums)],
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        back = redirect(url_for("contact") + "#form")
        name = request.form.get("name", "").strip()[:80]
        reach = request.form.get("contact", "").strip()[:120]
        body = request.form.get("body", "").strip()

        if request.form.get("website"):      # ô bẫy chống máy gửi rác
            return back
        if not name or len(body) < 2:
            flash("Nhập tên và lời nhắn giúp tôi nhé.", "error")
            return back
        if len(body) > 3000:
            flash("Lời nhắn dài quá — tối đa 3000 ký tự.", "error")
            return back
        if too_soon("message", 30):
            flash("Bạn vừa gửi rồi, đợi chút rồi gửi tiếp nhé.", "error")
            return back

        db.execute("INSERT INTO messages (name, contact, body, created) VALUES (?, ?, ?, ?)",
                   (name, reach, body, db.now()))
        flash("Đã gửi! Tôi sẽ đọc và trả lời sớm.", "ok")
        return back

    return render_template("contact.html", socials=data.SOCIALS)


@app.route("/favicon.ico")
def favicon():
    # Trình duyệt luôn tự hỏi /favicon.ico — chỉ sang icon SVG
    return redirect(url_for("static", filename="favicon.svg"), code=301)


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


# Trang quản trị nằm ở admin.py
from admin import bp as admin_bp  # noqa: E402

app.register_blueprint(admin_bp)


if __name__ == "__main__":
    app.run(debug=True)
