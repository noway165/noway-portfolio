# Web cá nhân — Tăng Thoại Lâm (Noway)

Flask (Python) + SQLite + Bootstrap 5 + JavaScript.

## Chạy

Nhấp đúp `chay-web.bat`, hoặc:

```
pip install -r requirements.txt
python app.py
```

Mở http://127.0.0.1:5000 — trang quản trị ở http://127.0.0.1:5000/admin

## Trang quản trị (/admin)

Lần đầu mở `/admin` **trên chính máy chạy web** sẽ được hỏi tạo mật khẩu (ít nhất 8 ký tự).
Trong đó có thể:

- viết / sửa / ẩn bài blog
- thêm / sửa dự án
- tải ảnh lên album, xoá ảnh
- thêm clip TikTok (hiện ở trang Gaming)
- đọc tin nhắn gửi từ trang Liên hệ, xoá bình luận
- xem lượt xem, lượt thích

Quên mật khẩu: `flask --app app set-password`

Dữ liệu (bài viết, tin nhắn, bình luận, mật khẩu…) nằm trong `instance/site.db` —
file này **không** đưa lên GitHub. Muốn sao lưu thì chép file đó ra chỗ khác.

## Sửa gì ở đâu

| Muốn đổi | Sửa ở |
|---|---|
| Bài blog, dự án, clip TikTok, ảnh album | trang `/admin` |
| Tên, giới thiệu, dòng chữ tự gõ, câu quote | `data.py` → `PROFILE` |
| Kỹ năng, dòng thời gian (trang About) | `data.py` → `SKILLS`, `TIMELINE` |
| Game, ID trong game | `data.py` → `GAMES` |
| Bài nhạc Spotify | `data.py` → `TRACKS` |
| Tên album | `data.py` → `ALBUMS` |
| Facebook, Discord, ID game... | `data.py` → `SOCIALS` |
| Ảnh đại diện | đặt file vào `static/img/avatar.jpg` |
| Màu nhấn, màu nền sáng/tối, font | `static/css/style.css` (mục 1 — TOKEN, có sẵn vài bảng màu gợi ý) |
| Bố cục từng trang | `templates/` |

## Cấu trúc

```
app.py              các trang công khai, form liên hệ, bình luận, thả tim, đếm lượt xem
admin.py            trang quản trị
db.py               database SQLite (tạo bảng, nạp dữ liệu mẫu lần đầu)
media.py            đọc thư mục ảnh album
data.py             nội dung cố định + dữ liệu mẫu
templates/          giao diện (Jinja2): base.html là khung chung, admin/ là trang quản trị
static/css/         style.css đặt lên trên Bootstrap
static/js/app.js    hiệu ứng, sáng/tối, thả tim, chép ID, xem ảnh phóng to
static/img/         ảnh
instance/site.db    dữ liệu (tự tạo khi chạy lần đầu)
```
