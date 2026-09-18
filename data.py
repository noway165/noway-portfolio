"""
Toàn bộ nội dung của trang web nằm ở đây.

Muốn đổi chữ, thêm bài nhạc, thêm album hay mạng xã hội — chỉ cần sửa file này,
không phải đụng vào giao diện. Lưu lại rồi tải lại trình duyệt là thấy.
"""

# --------------------------------------------------------------------- HỒ SƠ
PROFILE = {
    "name": "Tăng Thoại Lâm",
    "first": "Tăng",
    "last": "Thoại Lâm",
    "alias": "Noway",
    "monogram": "TL",
    # Dòng chữ tự gõ ở trang chủ: "Tôi là ..."
    "roles": ["cựu tuyển thủ PUBG Mobile", "sinh viên IT", "content creator"],
    "quote": "Love is the best thing we do.",
    # Ảnh đại diện: đặt file vào static/img/avatar.jpg (chưa có thì hiện chữ lồng TL)
    "avatar": "img/avatar.jpg",
    "bio": [
        "Tôi là Tăng Thoại Lâm, mọi người hay gọi là Noway. Tôi thi đấu PUBG Mobile "
        "chuyên nghiệp từ cuối năm 2024 qua các mùa PMNC và PMPL, rồi chuyển sang "
        "làm huấn luyện viên. Hiện tôi không thi đấu — là sinh viên IT và người làm nội dung.",
        "Trang này là nơi tôi gom lại những thứ mình quý: vài tấm ảnh, "
        "vài bài nhạc nghe hoài không chán, và cách để bạn tìm thấy tôi.",
    ],
}

# ----------------------------------------------------- 3 THẺ "TÔI THEO ĐUỔI"
FOCUS = [
    {
        "title": "Lập trình",
        "icon": "bi-terminal",
        "text": "Học và làm về công nghệ thông tin — web, phần mềm, "
                "và những công cụ nhỏ giải quyết việc thật.",
    },
    {
        "title": "Sáng tạo nội dung",
        "icon": "bi-record-circle",
        "text": "Quay dựng khoảnh khắc đời thường và những pha xử lý trong game, "
                "chia sẻ trên TikTok và Instagram.",
    },
    {
        "title": "PUBG Mobile",
        "icon": "bi-crosshair",
        "text": "Thi đấu chuyên nghiệp từ cuối 2024 qua 4 mùa PMNC và PMPL, "
                "nổi bật nhất là PMNC mùa Tổng kết 2025 cùng Five Brothers (FBT).",
    },
]

# ------------------------------------------------------------------- MENU
# "also": các trang con cũng làm sáng mục menu này
NAV = [
    {"label": "Home", "endpoint": "index"},
    {"label": "About", "endpoint": "about"},
    {"label": "Projects", "endpoint": "projects"},
    {"label": "Blog", "endpoint": "blog", "also": ["post"]},
    {"label": "Gaming", "endpoint": "gaming"},
    {"label": "Music", "endpoint": "music"},
    {"label": "Gallery", "endpoint": "gallery", "also": ["album"]},
    {"label": "Contact", "endpoint": "contact"},
]

# ------------------------------------------------------------------- NHẠC
# Mã bài trên Spotify: mở bài hát > Chia sẻ > Sao chép liên kết,
# lấy đoạn giữa "track/" và "?"
TRACKS = [
    "71luUs5K7N1fdf7ecMKg04",
    "190jyVPHYjAqEaOGmMzdyk",
    "5xVCfx47vCXuLdpfbepqEo",
    "7uUuftbcr94tzGOCJSM25u",
    "4nXrVH5xwN1w6TpmP7uu8n",
    "6Zoi4ue74UdUeYmHXItXnf",
]

# ---------------------------------------------------------------- ALBUM ẢNH
# Ảnh tự được quét từ static/img/gallery/<slug>/ — thả ảnh vào là hiện.
# Ảnh đầu tiên (theo tên file) làm bìa album.
ALBUMS = [
    {"slug": "me", "name": "Me", "title": "Bản thân", "note": "Hình ảnh cá nhân"},
    {"slug": "view", "name": "View", "title": "Phong cảnh", "note": "Góc nhìn và phong cảnh"},
    {"slug": "friends", "name": "Friends", "title": "Bạn bè", "note": "Những người anh em"},
]

# --------------------------------------------------------------- LIÊN HỆ
# Có "url"  -> bấm vào mở trang mới.
# Có "copy" -> bấm vào chép chữ đó vào bộ nhớ tạm.
# Tên icon tra ở https://icons.getbootstrap.com
SOCIALS = [
    {"name": "Facebook", "handle": "Tang Lam", "icon": "bi-facebook",
     "url": "https://www.facebook.com/tanglam1605/"},
    {"name": "Instagram", "handle": "@tlam_1605", "icon": "bi-instagram",
     "url": "https://www.instagram.com/tlam_1605/"},
    {"name": "TikTok", "handle": "Noway16", "icon": "bi-tiktok",
     "url": "https://www.tiktok.com/@tlam_1605"},
    {"name": "Discord", "handle": "Noway#7373", "icon": "bi-discord",
     "copy": "Noway#7373"},
    {"name": "PUBG Mobile", "handle": "ID 5189112695", "icon": "bi-crosshair",
     "copy": "5189112695"},
    {"name": "TFT", "handle": "Yêu Cô Ấy#0615", "icon": "bi-controller",
     "copy": "Yêu Cô Ấy#0615"},
]

# ------------------------------------------------------------ TRANG ABOUT
# Nhóm kỹ năng: mỗi nhóm một tiêu đề và danh sách kỹ năng.
SKILLS = [
    {"group": "Lập trình", "icon": "bi-code-slash",
     "items": ["Python", "Flask", "HTML & CSS", "JavaScript", "Bootstrap 5", "Git"]},
    {"group": "Sáng tạo", "icon": "bi-camera-reels",
     "items": ["Quay & dựng video", "Chụp ảnh", "TikTok", "Instagram"]},
    {"group": "Game", "icon": "bi-controller",
     "items": ["Thi đấu PUBG Mobile", "Chiến thuật đội hình", "Teamfight Tactics"]},
]

# Dòng thời gian, mới nhất ở trên. Thêm mốc mới: chép một dòng rồi sửa.
TIMELINE = [
    {"when": "09 / 2026", "title": "Chuyển web cá nhân sang Flask",
     "text": "Viết lại toàn bộ trang bằng Python + Flask, nội dung gom vào một file cho dễ sửa."},
    {"when": "2026", "title": "Web cá nhân đầu tiên",
     "text": "Tự dựng bản HTML/CSS/JavaScript thuần — nơi gom ảnh, nhạc và cách liên lạc."},
    {"when": "2026", "title": "Từ tuyển thủ thành huấn luyện viên",
     "text": "Thi đấu PMPL Spring 2026, rồi làm huấn luyện viên cho not team (not) ở PMPL Fall 2026."},
    {"when": "2025", "title": "Ba mùa PMNC, ba đội tuyển",
     "text": "Japan Gaming (JP), linncutii (lc) và Five Brothers (FBT) — nổi bật nhất là PMNC mùa Tổng kết 2025."},
    {"when": "Cuối 2024", "title": "Trở thành tuyển thủ PUBG Mobile",
     "text": "Giải chuyên nghiệp đầu tiên: PMNC 2024 cùng Vnus Royal (VR)."},
    {"when": "Hiện tại", "title": "Sinh viên Công nghệ thông tin",
     "text": "Học lập trình, làm nội dung và chơi game song song."},
]

# ------------------------------------------------ DỰ ÁN & BLOG (DỮ LIỆU MẪU)
# Hai danh sách dưới chỉ được nạp vào database ở LẦN CHẠY ĐẦU TIÊN.
# Sau đó thêm / sửa / xoá dự án và bài viết trong trang quản trị: /admin
SEED_PROJECTS = [
    {
        "title": "Web cá nhân — bản Flask",
        "year": "2026",
        "status": "Đang phát triển",
        "live": True,  # chấm trạng thái nhấp nháy
        "text": "Chính trang bạn đang xem. Flask phục vụ các trang từ một khung chung, "
                "album ảnh tự quét thư mục, có chế độ sáng/tối và chạy tốt trên điện thoại.",
        "tags": ["Python", "Flask", "Jinja2", "Bootstrap 5", "JavaScript"],
        "links": [{"label": "GitHub", "url": "https://github.com/noway165/noway-portfolio"}],
    },
    {
        "title": "Web cá nhân — bản HTML",
        "year": "2026",
        "status": "Đã hoàn thành",
        "text": "Phiên bản đầu tiên, viết tay bằng HTML, CSS và JavaScript thuần: "
                "trang chủ, nhạc, thư viện ảnh và liên hệ.",
        "tags": ["HTML", "CSS", "JavaScript"],
        "links": [],
    },
]

SEED_POSTS = [
    {
        "slug": "chao-mung",
        "title": "Chào mừng đến góc nhỏ của tôi",
        "date": "2026-09-18",
        "tags": ["Cá nhân"],
        "excerpt": "Vì sao có trang này, và bạn sẽ tìm thấy gì ở đây.",
        "body": [
            "Đã lâu tôi muốn có một chỗ riêng trên mạng — không phải trang mạng xã hội "
            "nơi mọi thứ trôi đi sau vài ngày, mà là một nơi mình tự dựng và tự giữ.",
            "## Ở đây có gì",
            "Vài album ảnh về bản thân, phong cảnh và bạn bè. Một danh sách nhạc tôi nghe "
            "hoài không chán. Những dự án lập trình đang làm, góc chơi game, "
            "và blog này để ghi lại những gì tôi học được.",
            "## Tiếp theo",
            "Tôi sẽ viết đều hơn về lập trình, về những pha xử lý trong game và những thứ "
            "nhỏ nhặt thường ngày. Nếu bạn muốn nói gì, trang liên hệ luôn mở.",
            "> Love is the best thing we do.",
        ],
    },
    {
        "slug": "chuyen-web-sang-flask",
        "title": "Chuyển web cá nhân từ HTML sang Flask",
        "date": "2026-09-17",
        "tags": ["Lập trình", "Python"],
        "excerpt": "Bản HTML chạy ổn, nhưng mỗi lần sửa là phải đụng vào nhiều file. Đây là lý do tôi đổi.",
        "body": [
            "Bản đầu tiên của trang này là HTML thuần: mỗi trang một file, menu và chân trang "
            "chép đi chép lại ở từng file. Muốn thêm một mục menu là phải sửa bốn chỗ.",
            "## Vì sao chọn Flask",
            "Flask nhỏ, dễ đọc, và đủ cho một trang cá nhân. Với Jinja2, phần khung chung "
            "chỉ cần viết một lần trong base.html, các trang con chỉ lo phần nội dung của mình.",
            "## Nội dung tách khỏi giao diện",
            "Toàn bộ chữ, bài nhạc, album và mạng xã hội giờ nằm trong một file data.py. "
            "Muốn đổi gì chỉ cần sửa đúng một chỗ, lưu lại rồi tải lại trình duyệt.",
            "## Album tự quét ảnh",
            "Thư viện ảnh không còn phải khai báo từng tấm. Thả ảnh vào đúng thư mục là "
            "chúng tự hiện, ảnh đầu tiên theo tên file làm bìa album.",
        ],
    },
]

# --------------------------------------------------------------- GAMING
# "copy": bấm vào thẻ ID để chép. "stats": vài dòng thông tin ngắn —
# thêm rank, chế độ yêu thích... tuỳ ý: {"label": "Rank", "value": "..."}
GAMES = [
    {
        "name": "PUBG Mobile",
        "icon": "bi-crosshair",
        "style": "pubg",    # giao diện thẻ: pubg = tâm ngắm, tft = lưới lục giác
        "platform": "Mobile",
        "id_label": "Character ID",
        "copy": "5189112695",
        "text": "Thi đấu chuyên nghiệp từ cuối 2024 ở PMNC và PMPL Việt Nam, sau đó làm "
                "huấn luyện viên. Giờ vẫn chơi mỗi ngày — những pha xử lý hay được đăng lên TikTok.",
        # Thêm dòng tuỳ ý, ví dụ {"label": "Vị trí sở trường", "value": "..."}
        "stats": [{"label": "Thi đấu từ", "value": "Cuối 2024"}, {"label": "Giải đã dự", "value": "5"},
                  {"label": "Hiện tại", "value": "Không thi đấu"}],
        # Hành trình thi đấu — hiện thành một mục riêng ở trang Gaming, mới nhất ở trên
        # "role": vai trò ở giải đó; "note": ghi chú kết quả; "highlight": True = đánh dấu nổi bật
        "career": [
            {"when": "Hiện tại", "title": "Tạm dừng thi đấu", "team": "", "role": "",
             "text": "Không thi đấu chuyên nghiệp — tập trung học và làm nội dung."},
            {"when": "Fall 2026", "title": "PMPL Fall 2026", "team": "not team (not)",
             "role": "Huấn luyện viên", "text": "Chuyển sang vai trò huấn luyện viên."},
            {"when": "Spring 2026", "title": "PMPL Spring 2026", "team": "not team (not)",
             "role": "Tuyển thủ", "text": "Lần đầu thi đấu ở PMPL.", "note": "Bị loại sớm"},
            {"when": "Tổng kết 2025", "title": "PMNC mùa Tổng kết 2025", "team": "Five Brothers (FBT)",
             "role": "Tuyển thủ", "text": "Dấu mốc nổi bật nhất sự nghiệp.", "highlight": True},
            {"when": "Thu 2025", "title": "PMNC mùa Thu 2025", "team": "linncutii (lc)",
             "role": "Tuyển thủ", "text": ""},
            {"when": "Xuân 2025", "title": "PMNC mùa Xuân 2025", "team": "Japan Gaming (JP)",
             "role": "Tuyển thủ", "text": ""},
            {"when": "2024", "title": "PMNC 2024", "team": "Vnus Royal (VR)",
             "role": "Tuyển thủ", "text": "Giải chuyên nghiệp đầu tiên."},
        ],
    },
    {
        "name": "Teamfight Tactics",
        "icon": "bi-hexagon",
        "style": "tft",
        "platform": "PC",
        "id_label": "Riot ID",
        "copy": "Yêu Cô Ấy#0615",
        "text": "Cờ chiến thuật của Riot. Chậm hơn, cần tính toán hơn — "
                "cách tôi thư giãn sau những trận bắn súng căng thẳng.",
        "stats": [{"label": "Nền tảng", "value": "PC"}, {"label": "Thể loại", "value": "Chiến thuật"}],
    },
]
