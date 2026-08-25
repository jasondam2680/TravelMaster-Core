# Module Scheduling - TravelMaster-Core

## Tổng quan
Module `scheduling` là một giải pháp tối ưu hóa lịch trình xe và guide cho các công ty du lịch, được tích hợp vào dự án TravelMaster-Core.

## Tính năng chính

### 1. Quản lý dữ liệu
- **TourDeparture**: Quản lý các đoàn tour (mã đoàn, ngày khởi hành, số ngày, số khách, tour premium)
- **Vehicle**: Quản lý xe (loại xe, sức chứa, có sẵn hay không)
- **Guide**: Quản lý hướng dẫn viên (tên, ngôn ngữ, có sẵn hay không)
- **Assignment**: Lưu trữ kết quả phân bổ xe và guide cho các đoàn

### 2. Tối ưu hóa tự động
- Sử dụng Linear Programming (PuLP) để tối ưu hóa phân bổ
- 4 mục tiêu ưu tiên:
  - **A**: Tối thiểu hóa số xe sử dụng
  - **C**: Tối thiểu hóa số guide sử dụng  
  - **B**: Tối đa hóa hiệu suất sử dụng xe (utilization)
  - **D**: Cân bằng workload giữa các guide

### 3. Phát hiện xung đột
- Phát hiện xung đột lịch trình xe
- Phát hiện xung đột lịch trình guide
- Cảnh báo khi không đủ tài nguyên

### 4. Giao diện web
- Dashboard tổng quan với thống kê
- Xem kết quả tối ưu chi tiết
- Xuất lịch dạng CSV:
  - `schedule.csv`: Lịch phân bổ từng đoàn
  - `vehicle_calendar.csv`: Lịch xe theo ngày
  - `guide_calendar.csv`: Lịch guide theo ngày

## Cấu trúc thư mục

```
scheduling/
├── __init__.py
├── models.py              # Định nghĩa models Django
├── views.py               # Views xử lý dashboard, optimizer, export
├── urls.py                # URL routing
├── admin.py               # Django admin configuration
├── apps.py                # App configuration
├── optimizer.py           # Core LP optimization logic
├── utils.py               # Utility functions
├── tests.py               # Unit tests
├── migrations/            # Database migrations
│   └── __init__.py
├── management/
│   └── commands/
│       ├── import_data.py     # Import CSV data command
│       └── run_optimizer.py   # Run optimizer command
└── templates/scheduling/
    ├── base.html              # Base template
    ├── dashboard.html         # Dashboard view
    └── optimizer_results.html # Results view
```

## Cài đặt

### 1. Thêm app vào settings.py

```python
INSTALLED_APPS = [
    # ...
    'scheduling',
]
```

### 2. Thêm URLs vào project urls.py

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('scheduling/', include('scheduling.urls')),
]
```

### 3. Cài đặt dependencies

```bash
pip install pulp
```

### 4. Chạy migrations

```bash
python manage.py makemigrations scheduling
python manage.py migrate
```

## Sử dụng

### Import dữ liệu từ CSV

```bash
python manage.py import_data \
    --tours data/tours_v2.csv \
    --vehicles data/vehicles_v2.csv \
    --guides data/guides_v2.csv
```

Định dạng file CSV:

**tours_v2.csv**:
```csv
tour_code,start_date,duration_days,pax,is_premium
HDV-001,2025-03-01,8,18,0
```

**vehicles_v2.csv**:
```csv
vehicle_id,vehicle_type,capacity
XE-001,29-seater,29
```

**guides_v2.csv**:
```csv
guide_id,name,languages
G-001,Nguyen Van A,vi;en
```

### Chạy optimizer qua command line

```bash
python manage.py run_optimizer
```

### Sử dụng qua web interface

1. Truy cập: `http://localhost:8000/scheduling/`
2. Xem dashboard với thống kê tổng quan
3. Click "Chạy Optimizer" để tối ưu hóa
4. Xem kết quả và xuất CSV nếu cần

## API Endpoints

- `GET /scheduling/` - Dashboard
- `POST /scheduling/run-optimizer/` - Chạy tối ưu hóa
- `GET /scheduling/results/` - Xem kết quả
- `GET /scheduling/export/schedule/` - Xuất lịch CSV
- `GET /scheduling/export/vehicle-calendar/` - Xuất lịch xe
- `GET /scheduling/export/guide-calendar/` - Xuất lịch guide

## Constraint Logic

Module tuân theo các ràng buộc:

1. **Loại xe**: Xe 29 chỗ cho đoàn 20 pax
2. **Guide assignment**: Mỗi đoàn 1 guide xuyên suốt
3. **Giờ làm việc**: "Chiếm trọn ngày" - không tính giờ cụ thể
4. **Premium tours**: Không bắt buộc phải có tài nguyên premium riêng
5. **Conflict detection**: Tự động phát hiện khi xe/guide bận trong cùng khoảng thời gian

## Testing

Chạy tests:

```bash
python manage.py test scheduling
```

Tests bao gồm:
- Model validation
- Optimizer logic
- Conflict detection
- View responses

## Troubleshooting

### Lỗi "No feasible solution"
- Kiểm tra xem có đủ xe và guide không
- Xem lại dữ liệu đầu vào (ngày, số lượng khách)
- Kiểm tra constraints trong optimizer.py

### Không hiển thị kết quả
- Đảm bảo đã chạy optimizer trước
- Kiểm tra database có dữ liệu Assignment không
- Xem Django logs để debug

## Tác giả

Module được phát triển cho TravelMaster-Core project.

## License

Tham khảo LICENSE của dự án TravelMaster-Core.
