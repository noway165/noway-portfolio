"""
Trang quản trị: /admin

Lần đầu mở /admin trên chính máy chạy web sẽ được hỏi tạo mật khẩu.
Quên mật khẩu: xoá dòng admin_password trong instance/site.db,
hoặc chạy  flask --app app set-password
"""
import re
import time
import unicodedata
from datetime import date, datetime
from functools import wraps

import click
from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import data
import db
from media import album_files, gallery_dir

bp = Blueprint("admin", __name__, url_prefix="/admin", cli_group=None)

LOCAL_ADDRS = {"127.0.0.1", "::1"}
MAX_FAILS, LOCK_SECONDS = 5, 600
_fails = {}   # ip -> (số lần sai, thời điểm bắt đầu khoá)


# ------------------------------------------------------------ ĐĂNG NHẬP
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def locked_out(ip):
    count, since = _fails.get(ip, (0, 0))
    if count >= MAX_FAILS and time.monotonic() - since < LOCK_SECONDS:
        return True
    if count >= MAX_FAILS:
        _fails.pop(ip, None)
    return False


def safe_next(target):
    """Chỉ cho quay lại đường dẫn nội bộ của trang quản trị."""
    return target if target and target.startswith("/admin") and not target.startswith("//") else None


@bp.route("/login", methods=["GET", "POST"])
def login():
    has_password = db.get_setting("admin_password") is not None
    is_local = request.remote_addr in LOCAL_ADDRS

    if request.method == "POST":
        password = request.form.get("password", "")

        if not has_password:
            # Tạo mật khẩu lần đầu — chỉ cho phép ngay trên máy chạy web
            if not is_local:
                abort(403)
            if len(password) < 8:
                flash("Mật khẩu cần ít nhất 8 ký tự.", "error")
            elif password != request.form.get("confirm", ""):
                flash("Hai lần nhập mật khẩu không khớp.", "error")
            else:
                db.set_setting("admin_password", generate_password_hash(password))
                session.clear()
                session["admin"] = True
                flash("Đã tạo mật khẩu. Chào mừng vào trang quản trị!", "ok")
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("admin.login"))

        ip = request.remote_addr
        if locked_out(ip):
            flash("Sai quá nhiều lần. Thử lại sau 10 phút.", "error")
        elif check_password_hash(db.get_setting("admin_password"), password):
            _fails.pop(ip, None)
            session.clear()           # đổi phiên mới sau khi đăng nhập
            session["admin"] = True
            return redirect(safe_next(request.args.get("next")) or url_for("admin.dashboard"))
        else:
            count, since = _fails.get(ip, (0, time.monotonic()))
            _fails[ip] = (count + 1, time.monotonic())
            flash("Sai mật khẩu.", "error")
        return redirect(url_for("admin.login", next=request.args.get("next")))

    return render_template("admin/login.html", setup=not has_password, is_local=is_local)


@bp.post("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


@bp.post("/password")
@login_required
def change_password():
    current = request.form.get("current", "")
    new = request.form.get("new", "")
    if not check_password_hash(db.get_setting("admin_password"), current):
        flash("Mật khẩu hiện tại không đúng.", "error")
    elif len(new) < 8:
        flash("Mật khẩu mới cần ít nhất 8 ký tự.", "error")
    else:
        db.set_setting("admin_password", generate_password_hash(new))
        flash("Đã đổi mật khẩu.", "ok")
    return redirect(url_for("admin.dashboard"))


@bp.cli.command("set-password")
@click.password_option()
def set_password_command(password):
    """Đặt lại mật khẩu quản trị từ dòng lệnh."""
    db.set_setting("admin_password", generate_password_hash(password))
    click.echo("Đã đặt mật khẩu quản trị.")


@bp.context_processor
def inject_admin():
    if not session.get("admin"):
        return {}
    unread = db.query("SELECT COUNT(*) AS n FROM messages WHERE is_read = 0", one=True)["n"]
    return {"unread": unread}


# ------------------------------------------------------------ TỔNG QUAN
@bp.route("/")
@login_required
def dashboard():
    one = lambda sql: db.query(sql, one=True)["n"]  # noqa: E731
    stats = [
        {"label": "Lượt xem trang", "value": db.total_page_views()},
        {"label": "Bài viết", "value": one("SELECT COUNT(*) AS n FROM posts")},
        {"label": "Lượt thích", "value": one("SELECT COALESCE(SUM(likes), 0) AS n FROM posts")},
        {"label": "Bình luận", "value": one("SELECT COUNT(*) AS n FROM comments")},
        {"label": "Tin nhắn chưa đọc", "value": one("SELECT COUNT(*) AS n FROM messages WHERE is_read = 0")},
    ]
    top_pages = db.query("SELECT path, count FROM page_views ORDER BY count DESC LIMIT 8")
    top_posts = db.query("SELECT title, slug, views, likes FROM posts ORDER BY views DESC LIMIT 5")
    recent = db.query("SELECT * FROM messages ORDER BY id DESC LIMIT 3")
    return render_template("admin/dashboard.html", stats=stats, top_pages=top_pages,
                           top_posts=top_posts, recent=recent)


# ------------------------------------------------------------ BÀI VIẾT
def slugify(text):
    """'Chuyển web sang Flask' -> 'chuyen-web-sang-flask'"""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "bai-viet"


def unique_slug(slug, exclude_id=None):
    base, n = slug, 2
    while db.query("SELECT 1 FROM posts WHERE slug = ? AND id IS NOT ?", (slug, exclude_id), one=True):
        slug = f"{base}-{n}"
        n += 1
    return slug


@bp.route("/posts")
@login_required
def posts():
    rows = db.query(
        "SELECT p.*, (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS n_comments "
        "FROM posts p ORDER BY date DESC, id DESC")
    return render_template("admin/posts.html", posts=rows)


@bp.route("/posts/new", methods=["GET", "POST"])
@bp.route("/posts/<int:post_id>", methods=["GET", "POST"])
@login_required
def post_form(post_id=None):
    row = db.query("SELECT * FROM posts WHERE id = ?", (post_id,), one=True) if post_id else None
    if post_id and not row:
        abort(404)

    if request.method == "POST":
        f = request.form
        title = f.get("title", "").strip()
        day = f.get("date", "").strip() or date.today().isoformat()
        try:
            date.fromisoformat(day)
        except ValueError:
            day = date.today().isoformat()

        if not title or not f.get("body", "").strip():
            flash("Bài viết cần có tiêu đề và nội dung.", "error")
            return render_template("admin/post_form.html", post=f, post_id=post_id)

        slug = unique_slug(slugify(f.get("slug", "").strip() or title), post_id)
        values = (slug, title, day, f.get("tags", "").strip(), f.get("excerpt", "").strip(),
                  f.get("body", "").strip(), 1 if f.get("published") else 0)
        if row:
            db.execute("UPDATE posts SET slug=?, title=?, date=?, tags=?, excerpt=?, body=?, published=? "
                       "WHERE id = ?", values + (post_id,))
            flash("Đã lưu bài viết.", "ok")
        else:
            post_id = db.execute("INSERT INTO posts (slug, title, date, tags, excerpt, body, published) "
                                 "VALUES (?, ?, ?, ?, ?, ?, ?)", values).lastrowid
            flash("Đã tạo bài viết mới.", "ok")
        return redirect(url_for("admin.post_form", post_id=post_id))

    blank = {"date": date.today().isoformat(), "published": 1}
    return render_template("admin/post_form.html", post=row or blank, post_id=post_id)


@bp.post("/posts/<int:post_id>/delete")
@login_required
def post_delete(post_id):
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    flash("Đã xoá bài viết (và các bình luận của nó).", "ok")
    return redirect(url_for("admin.posts"))


# ------------------------------------------------------------ DỰ ÁN
@bp.route("/projects")
@login_required
def projects():
    return render_template("admin/projects.html",
                           projects=db.query("SELECT * FROM projects ORDER BY position, id"))


@bp.route("/projects/new", methods=["GET", "POST"])
@bp.route("/projects/<int:project_id>", methods=["GET", "POST"])
@login_required
def project_form(project_id=None):
    row = db.query("SELECT * FROM projects WHERE id = ?", (project_id,), one=True) if project_id else None
    if project_id and not row:
        abort(404)

    if request.method == "POST":
        f = request.form
        if not f.get("title", "").strip():
            flash("Dự án cần có tên.", "error")
            return render_template("admin/project_form.html", project=f, project_id=project_id)
        try:
            position = int(f.get("position") or 0)
        except ValueError:
            position = 0
        values = (f["title"].strip(), f.get("year", "").strip(), f.get("status", "").strip(),
                  1 if f.get("live") else 0, f.get("text", "").strip(), f.get("tags", "").strip(),
                  f.get("links", "").strip(), position)
        if row:
            db.execute("UPDATE projects SET title=?, year=?, status=?, live=?, text=?, tags=?, links=?, "
                       "position=? WHERE id = ?", values + (project_id,))
        else:
            db.execute("INSERT INTO projects (title, year, status, live, text, tags, links, position) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)
        flash("Đã lưu dự án.", "ok")
        return redirect(url_for("admin.projects"))

    next_pos = db.query("SELECT COALESCE(MAX(position), -1) + 1 AS n FROM projects", one=True)["n"]
    blank = {"year": str(date.today().year), "position": next_pos}
    return render_template("admin/project_form.html", project=row or blank, project_id=project_id)


@bp.post("/projects/<int:project_id>/delete")
@login_required
def project_delete(project_id):
    db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    flash("Đã xoá dự án.", "ok")
    return redirect(url_for("admin.projects"))


# ------------------------------------------------------------ ẢNH
# Kiểm tra vài byte đầu để chắc file đúng là ảnh, không chỉ đổi đuôi
MAGIC = {
    ".jpg": [b"\xff\xd8\xff"], ".jpeg": [b"\xff\xd8\xff"], ".png": [b"\x89PNG"],
    ".gif": [b"GIF87a", b"GIF89a"], ".webp": [b"RIFF"], ".avif": [b"\x00\x00\x00"],
}


def album_or_404(slug):
    album = next((a for a in data.ALBUMS if a["slug"] == slug), None)
    if not album:
        abort(404)
    return album


@bp.route("/photos")
@login_required
def photos():
    albums = [{**a, "files": [p.name for p in album_files(a["slug"])]} for a in data.ALBUMS]
    return render_template("admin/photos.html", albums=albums)


@bp.post("/photos/<slug>/upload")
@login_required
def photo_upload(slug):
    album_or_404(slug)
    folder = gallery_dir() / slug
    folder.mkdir(parents=True, exist_ok=True)

    saved, skipped = 0, []
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for i, file in enumerate(request.files.getlist("photos")):
        if not file or not file.filename:
            continue
        ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        head = file.stream.read(12)
        file.stream.seek(0)
        if ext not in MAGIC or not any(head.startswith(m) for m in MAGIC[ext]):
            skipped.append(file.filename)
            continue
        stem = secure_filename(file.filename.rsplit(".", 1)[0])[:40] or "anh"
        file.save(folder / f"{stamp}-{i:02d}-{stem}{ext}")
        saved += 1

    if saved:
        flash(f"Đã tải lên {saved} ảnh vào album {slug}.", "ok")
    if skipped:
        flash("Bỏ qua (không phải ảnh hợp lệ): " + ", ".join(skipped), "error")
    if not saved and not skipped:
        flash("Chưa chọn ảnh nào.", "error")
    return redirect(url_for("admin.photos") + f"#album-{slug}")


@bp.post("/photos/<slug>/delete")
@login_required
def photo_delete(slug):
    album_or_404(slug)
    name = request.form.get("name", "")
    target = next((p for p in album_files(slug) if p.name == name), None)
    if target:
        target.unlink()
        flash(f"Đã xoá ảnh {name}.", "ok")
    return redirect(url_for("admin.photos") + f"#album-{slug}")


# ------------------------------------------------------------ CLIP TIKTOK
@bp.route("/clips", methods=["GET", "POST"])
@login_required
def clips():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        video_id = db.tiktok_id(url)
        if not video_id:
            flash("Cần link video đầy đủ dạng tiktok.com/@ten/video/123… "
                  "(mở video trên máy tính rồi chép link trên thanh địa chỉ).", "error")
        else:
            title = request.form.get("title", "").strip() or "Clip TikTok"
            db.execute("INSERT INTO clips (title, video_id, url, game, created) VALUES (?, ?, ?, ?, ?)",
                       (title, video_id, url, request.form.get("game", "").strip(), db.now()))
            flash("Đã thêm clip.", "ok")
        return redirect(url_for("admin.clips"))

    return render_template("admin/clips.html", clips=db.query("SELECT * FROM clips ORDER BY id DESC"),
                           games=[g["name"] for g in data.GAMES])


@bp.post("/clips/<int:clip_id>/delete")
@login_required
def clip_delete(clip_id):
    db.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
    flash("Đã xoá clip.", "ok")
    return redirect(url_for("admin.clips"))


# ------------------------------------------------------------ TIN NHẮN
@bp.route("/messages")
@login_required
def messages():
    return render_template("admin/messages.html",
                           messages=db.query("SELECT * FROM messages ORDER BY is_read, id DESC"))


@bp.post("/messages/<int:msg_id>/read")
@login_required
def message_read(msg_id):
    db.execute("UPDATE messages SET is_read = 1 - is_read WHERE id = ?", (msg_id,))
    return redirect(url_for("admin.messages"))


@bp.post("/messages/<int:msg_id>/delete")
@login_required
def message_delete(msg_id):
    db.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    flash("Đã xoá tin nhắn.", "ok")
    return redirect(url_for("admin.messages"))


# ------------------------------------------------------------ BÌNH LUẬN
@bp.route("/comments")
@login_required
def comments():
    rows = db.query("SELECT c.*, p.title AS post_title, p.slug AS post_slug "
                    "FROM comments c JOIN posts p ON p.id = c.post_id ORDER BY c.id DESC")
    return render_template("admin/comments.html", comments=rows)


@bp.post("/comments/<int:comment_id>/delete")
@login_required
def comment_delete(comment_id):
    db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    flash("Đã xoá bình luận.", "ok")
    return redirect(url_for("admin.comments"))
