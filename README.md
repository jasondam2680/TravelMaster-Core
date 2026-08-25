# TravelMaster-Core

**Hệ thống điều hành tour du lịch nội bộ** — backend Django cho toàn bộ quy trình từ tiếp nhận báo giá, quản lý nhà cung cấp, đến điều phối lịch trình và theo dõi tài chính.

> Tích hợp trực tiếp với **[TourQuote Pro](https://github.com/jasondam2680/TourQuotePro)** — hệ thống báo giá frontend (React/Vite). Khi nhân viên chốt báo giá, dữ liệu được đẩy tự động sang TravelMaster-Core qua REST API để bắt đầu quy trình điều hành.

---

## Tổng Quan Hệ Thống

```
TourQuote Pro  ──── POST /api/import-quote/ ────►  TravelMaster-Core
  (React/Vite)       X-API-Key header               (Django 5.x + SQLite)
                                                          │
                                              ┌───────────┴───────────┐
                                              │  tours / suppliers    │
                                              │  finance / scheduling │
                                              └───────────────────────┘
```

Luồng hoạt động:
1. Nhân viên lập báo giá trên **TourQuote Pro** (tính chi phí, markup, VAT)
2. Nhấn **🚀 Chốt & Điều hành** → payload JSON chuẩn được gửi sang backend
3. TravelMaster-Core tiếp nhận, lưu vào DB và tạo tour trong hệ thống điều hành
4. Quản lý theo dõi tiến độ qua giao diện Django Admin hoặc các view nội bộ

---

## Cấu Trúc Project

```
TravelMaster-Core/
├── config/
│   ├── settings.py          # Cấu hình Django (đọc từ .env)
│   ├── urls.py              # URL routing gốc
│   ├── wsgi.py / asgi.py
│   └── __init__.py
│
├── tours/                   # App cốt lõi — quản lý tour & import báo giá
│   ├── models.py            # Tour, TourService, Pax
│   ├── views.py
│   ├── api_import.py        # Endpoint nhận JSON từ TourQuote Pro
│   ├── auth.py              # Decorator xác thực X-API-Key
│   └── urls.py
│
├── suppliers/               # Quản lý nhà cung cấp (khách sạn, xe, HDV...)
├── finance/                 # Theo dõi chi phí thực tế, công nợ
├── scheduling/              # Lịch trình, phân công nhân sự
├── templates/               # Django HTML templates
│
├── manage.py
├── requirements.txt
├── .env.example             # Mẫu file môi trường (KHÔNG chứa key thật)
└── README.md
```

---

## Yêu Cầu Hệ Thống

| Thành phần | Phiên bản |
|---|---|
| Python | 3.11+ |
| Django | 5.x |
| Database | SQLite (dev) / PostgreSQL (production) |
| OS | macOS / Linux / Windows (WSL) |

---

## Cài Đặt & Chạy Local

### 1. Clone repository

```bash
git clone https://github.com/jasondam2680/TravelMaster-Core.git
cd TravelMaster-Core
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Cài dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường

Sao chép file mẫu và điền thông tin thật:

```bash
cp .env.example .env
```

Mở `.env` và cập nhật:

```env
# .env — KHÔNG commit file này lên Git

SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# API Key để xác thực request từ TourQuote Pro
TOURQUOTE_API_KEY=your-api-key-here

# CORS — domain được phép gọi API
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

> Để tạo `SECRET_KEY` mạnh: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
>
> Để tạo `TOURQUOTE_API_KEY` ngẫu nhiên: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 5. Migrate database & tạo superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Chạy server

```bash
python manage.py runserver
```

Server khởi động tại `http://localhost:8000`  
Django Admin tại `http://localhost:8000/admin/`

---

## API Endpoint

### `POST /api/import-quote/`

Tiếp nhận báo giá đã chốt từ **TourQuote Pro** và tạo tour trong hệ thống điều hành.

**Headers bắt buộc:**

| Header | Giá trị |
|---|---|
| `Content-Type` | `application/json` |
| `X-API-Key` | Key khớp với `TOURQUOTE_API_KEY` trong `.env` |

**Request body (JSON chuẩn):**

```json
{
  "quote_id": "DN-HA-001",
  "confirmed_at": "2026-04-29T14:00:00.000Z",
  "customer": {
    "name": "Công ty TNHH ABC",
    "pax": 20,
    "pax_detail": { "adult": 18, "child": 2 }
  },
  "tour": {
    "name": "Đà Nẵng – Hội An 4N3Đ",
    "start_date": "2026-05-10",
    "end_date": "2026-05-13",
    "prepared_by": "Jason"
  },
  "services": [
    {
      "category": "accommodation",
      "name": "Khách sạn 3 sao (3 đêm)",
      "qty": 20,
      "unit_price": 600000,
      "currency": "VND",
      "unit_price_vnd": 600000,
      "times": 3,
      "total_vnd": 36000000,
      "note": ""
    }
  ],
  "pricing": {
    "base_cost_vnd": 85000000,
    "markup_pct": 18,
    "discount_pct": 0,
    "vat_pct": 0,
    "selling_price_vnd": 100300000,
    "display_currency": "VND"
  }
}
```

**Response thành công (`200 OK`):**

```json
{
  "status": "ok",
  "tour_id": 42,
  "message": "Tour đã được tạo thành công trong hệ thống điều hành."
}
```

**Response lỗi:**

| HTTP Status | Nguyên nhân |
|---|---|
| `401 Unauthorized` | Thiếu hoặc sai `X-API-Key` |
| `400 Bad Request` | JSON thiếu trường bắt buộc |
| `405 Method Not Allowed` | Không phải POST request |

---

## Bảo Mật

### Nguyên tắc chính

- **Không bao giờ** hardcode `SECRET_KEY`, API Key, hoặc password vào source code
- File `.env` được liệt kê trong `.gitignore` — không commit lên GitHub
- `DEBUG=False` bắt buộc ở môi trường production
- Mọi request từ TourQuote Pro phải mang header `X-API-Key` hợp lệ

### Cấu hình CORS

Backend sử dụng `django-cors-headers`. Chỉ các origin được khai báo trong `CORS_ALLOWED_ORIGINS` (`.env`) mới được phép gọi API. Mặc định chỉ cho phép method `POST` và `OPTIONS`.

### Xác thực API Key

Mọi endpoint nhận dữ liệu từ TourQuote Pro đều được bảo vệ bằng decorator `@require_api_key` trong `tours/auth.py`. Key được đọc từ header `X-API-Key` và so sánh với `TOURQUOTE_API_KEY` trong settings.

---

## Các App Django

| App | Chức năng chính |
|---|---|
| `tours` | Quản lý tour, dịch vụ, số pax; endpoint import báo giá |
| `suppliers` | Danh mục nhà cung cấp: khách sạn, hãng xe, HDV, nhà hàng |
| `finance` | Chi phí thực tế, đối chiếu báo giá vs thực chi, công nợ |
| `scheduling` | Lịch trình từng ngày, phân công HDV và tài xế |

---

## Môi Trường Production

Trước khi deploy, kiểm tra lại toàn bộ danh sách sau:

- [ ] `DEBUG=False` trong `.env`
- [ ] `SECRET_KEY` là chuỗi ngẫu nhiên dài, không phải giá trị mặc định
- [ ] `ALLOWED_HOSTS` chứa đúng domain production
- [ ] `CORS_ALLOWED_ORIGINS` chứa đúng domain TourQuote Pro
- [ ] `TOURQUOTE_API_KEY` là chuỗi ngẫu nhiên 32+ ký tự
- [ ] Chuyển database từ SQLite sang PostgreSQL
- [ ] Cấu hình Nginx + Gunicorn hoặc dùng Railway / Render
- [ ] File `.env` **không** có trong Git history

---

## Dự Án Liên Quan

| Repo | Mô tả |
|---|---|
| [TourQuote Pro](https://github.com/jasondam2680/TourQuotePro) | Frontend báo giá tour — React/Vite, hỗ trợ 3 ngôn ngữ (VI/EN/ZH) |

---

## Tác Giả

**Jason** — Tour operator & developer  
Ho Chi Minh City, Vietnam
