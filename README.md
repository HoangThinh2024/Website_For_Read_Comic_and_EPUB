# KomicLib – Website đọc truyện & tài liệu

Web đọc truyện, manga và tài liệu hỗ trợ các định dạng **CBZ**, **PDF**, **DOCX**, **EPUB**.

## Tính năng

- 📚 **Thư viện sách** với giao diện lưới hoặc danh sách
- 🔍 **Tìm kiếm** theo tiêu đề hoặc tác giả
- 🏷️ **Lọc** theo định dạng (CBZ / PDF / DOCX / EPUB) và thể loại
- 📖 **Đọc trực tuyến** với các trình đọc chuyên biệt:
  - **CBZ**: Trình đọc manga/comic ảnh trang theo trang
  - **PDF**: Trình đọc PDF (PDF.js) với zoom và điều hướng trang
  - **EPUB**: Trình đọc EPUB (epub.js) với phân trang
  - **DOCX**: Chuyển đổi sang HTML và hiển thị trực tiếp
- ✏️ **Chỉnh sửa metadata**: tiêu đề, tác giả, mô tả, thể loại
- 🗑️ **Xoá sách** khỏi thư viện
- 📊 **Tiến trình đọc**: lưu trang đang đọc
- 🌙 **Giao diện tối** hiện đại

## Cài đặt

### Yêu cầu hệ thống

- Python 3.10+
- pip

### Các bước cài đặt

```bash
# 1. Clone repository
git clone https://github.com/HoangThinh2024/Website_For_Read_Comic_and_EPUB.git
cd Website_For_Read_Comic_and_EPUB

# 2. Tạo virtual environment (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Chạy ứng dụng
python app.py
```

Sau khi chạy, truy cập **http://localhost:5000** trên trình duyệt.

## Cấu trúc dự án

```
├── app.py                  # Flask app entry point
├── models.py               # Database models (SQLAlchemy)
├── requirements.txt        # Python dependencies
├── routes/
│   ├── library.py          # Library & reader routes
│   └── upload.py           # Upload & edit routes
├── utils/
│   └── file_handler.py     # Metadata & cover extraction, CBZ/DOCX helpers
├── templates/
│   ├── base.html           # Base template
│   ├── library.html        # Library page
│   ├── reader.html         # Universal reader page
│   ├── upload.html         # Upload page
│   └── edit.html           # Edit metadata page
├── static/
│   ├── css/main.css        # Main stylesheet
│   └── img/                # Placeholder cover images
└── uploads/                # Uploaded files (auto-created)
    └── covers/             # Extracted cover thumbnails
```

## Định dạng hỗ trợ

| Định dạng | Mô tả | Trình đọc |
|-----------|-------|-----------|
| `.cbz`    | Comic Book ZIP (manga, truyện tranh) | Image viewer trang theo trang |
| `.pdf`    | Portable Document Format | PDF.js (render canvas) |
| `.epub`   | Electronic Publication | epub.js (phân trang) |
| `.docx`   | Microsoft Word Document | Chuyển đổi HTML |

## Biến môi trường

| Biến | Mặc định | Mô tả |
|------|----------|-------|
| `SECRET_KEY` | `dev-secret-key-change-in-prod` | Flask secret key (đổi khi deploy) |

## Tham khảo

- [Kavita](https://github.com/Kareadita/Kavita) – thư viện manga/truyện
- [TruyenDex](https://github.com/zennomi/truyendex) – đọc truyện online
