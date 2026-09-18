# Web cá nhân — Tăng Thoại Lâm (Noway)

Flask (Python) + Bootstrap 5 + JavaScript.

## Chạy

Nhấp đúp `chay-web.bat`, hoặc:

```
pip install -r requirements.txt
python app.py
```

Mở http://127.0.0.1:5000

## Sửa gì ở đâu

| Muốn đổi | Sửa file |
|---|---|
| Tên, giới thiệu, dòng chữ tự gõ, câu quote | `data.py` → `PROFILE` |
| Bài nhạc Spotify | `data.py` → `TRACKS` |
| Tên album | `data.py` → `ALBUMS` |
| Facebook, Discord, ID game... | `data.py` → `SOCIALS` |
| Kỹ năng, dòng thời gian (trang About) | `data.py` → `SKILLS`, `TIMELINE` |
| Dự án | `data.py` → `PROJECTS` |
| Bài blog | `data.py` → `POSTS` (`## ` = tiêu đề nhỏ, `> ` = trích dẫn) |
| Game, ID trong game | `data.py` → `GAMES` |
| Ảnh đại diện | đặt file vào `static/img/avatar.jpg` |
| Ảnh album | thả ảnh vào `static/img/gallery/me/`, `view/`, `friends/` — tự hiện, ảnh đầu tiên theo tên file làm bìa |
| Màu nhấn, màu nền sáng/tối, font | `static/css/style.css` (mục 1 — TOKEN, có sẵn vài bảng màu gợi ý) |
| Bố cục từng trang | `templates/` |

## Cấu trúc

```
app.py              server Flask, các trang, quét thư mục ảnh
data.py             toàn bộ nội dung
templates/          giao diện (Jinja2): base.html là khung chung
static/css/         style.css đặt lên trên Bootstrap
static/js/app.js    hiệu ứng, sáng/tối, xem ảnh phóng to, chép ID
static/img/         ảnh
```
