"""
Web cá nhân Tăng Thoại Lâm — chạy bằng Flask.

    pip install -r requirements.txt
    python app.py            ->  mở http://127.0.0.1:5000

Nội dung sửa ở data.py, giao diện ở templates/ và static/.
"""
import math
from datetime import date
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

import data

app = Flask(__name__)

STATIC_DIR = Path(app.static_folder)
GALLERY_DIR = STATIC_DIR / "img" / "gallery"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


# ------------------------------------------------------------------ TIỆN ÍCH
def static_url_if_exists(rel_path):
    """URL của file trong static/ nếu file có thật, không thì None."""
    if rel_path and (STATIC_DIR / rel_path).is_file():
        return url_for("static", filename=rel_path)
    return None


def album_photos(slug):
    """Quét static/img/gallery/<slug>/ và trả về URL các ảnh, xếp theo tên file."""
    folder = GALLERY_DIR / slug
    if not folder.is_dir():
        return []
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    return [url_for("static", filename=f"img/gallery/{slug}/{p.name}") for p in files]


def load_albums():
    albums = []
    for album in data.ALBUMS:
        photos = album_photos(album["slug"])
        albums.append({**album, "photos": photos, "cover": photos[0] if photos else None})
    return albums


def load_posts():
    """Bài blog mới nhất lên đầu, kèm ngày dạng date và số phút đọc."""
    posts = []
    for post in data.POSTS:
        words = sum(len(block.split()) for block in post["body"])
        posts.append({
            **post,
            "day": date.fromisoformat(post["date"]),
            "minutes": max(1, math.ceil(words / 200)),
        })
    return sorted(posts, key=lambda p: p["day"], reverse=True)


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
    return {"profile": data.PROFILE, "nav": nav, "social_links": links, "year": date.today().year}


# -------------------------------------------------------------------- TRANG
@app.route("/")
def index():
    albums = load_albums()
    photo_total = sum(len(a["photos"]) for a in albums)

    posts = load_posts()

    stats = [
        {"value": len(data.PROJECTS), "label": "Dự án"},
        {"value": len(posts), "label": "Bài viết"},
        {"value": len(data.TRACKS), "label": "Bài nhạc tuyển"},
        {"value": photo_total or len(albums), "label": "Tấm ảnh" if photo_total else "Album ảnh"},
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
    return render_template("projects.html", projects=data.PROJECTS)


@app.route("/blog")
def blog():
    return render_template("blog.html", posts=load_posts())


@app.route("/blog/<slug>")
def post(slug):
    posts = load_posts()
    slugs = [p["slug"] for p in posts]
    if slug not in slugs:
        abort(404)

    i = slugs.index(slug)
    # Danh sách xếp mới -> cũ: bài "mới hơn" đứng trước, bài "cũ hơn" đứng sau
    return render_template(
        "post.html",
        post=posts[i],
        newer=posts[i - 1] if i > 0 else None,
        older=posts[i + 1] if i + 1 < len(posts) else None,
    )


@app.route("/gaming")
def gaming():
    clips = next((s for s in data.SOCIALS if s["name"] == "TikTok"), None)
    discord = next((s for s in data.SOCIALS if s["name"] == "Discord"), None)
    return render_template("gaming.html", games=data.GAMES, clips=clips, discord=discord)


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


@app.route("/contact")
def contact():
    return render_template("contact.html", socials=data.SOCIALS)


@app.route("/favicon.ico")
def favicon():
    # Trình duyệt luôn tự hỏi /favicon.ico — chỉ sang icon SVG
    return redirect(url_for("static", filename="favicon.svg"), code=301)


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
