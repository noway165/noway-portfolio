"""Thư mục ảnh album: static/img/gallery/<slug>/"""
from pathlib import Path

from flask import current_app

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def gallery_dir():
    return Path(current_app.static_folder) / "img" / "gallery"


def album_files(slug):
    """Các file ảnh của một album, xếp theo tên file (ảnh đầu tiên làm bìa)."""
    folder = gallery_dir() / slug
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS)
