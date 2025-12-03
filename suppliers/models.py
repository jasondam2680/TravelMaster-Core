from django.db import models

class Supplier(models.Model):
    # --- 1. Định nghĩa các lựa chọn (Dropdown list) ---
    # Để tránh gõ sai, ta quy định sẵn các loại hình
    HOTEL = 'HTL'
    RESTAURANT = 'RES'
    TRANSPORT = 'TRP'
    SIGHTSEEING = 'SIG'
    GUIDE = 'GUI'
    INSURANCE = 'INS'

    SUPPLIER_TYPE_CHOICES = [
        (HOTEL, 'Khách sạn'),
        (RESTAURANT, 'Nhà hàng'),
        (TRANSPORT, 'Xe du lịch'),
        (SIGHTSEEING, 'Vé thắng cảnh'),
        (GUIDE, 'Hướng dẫn viên'),
        (INSURANCE, 'Bảo hiểm du lịch'),
    ]

    PAYMENT_CREDIT = 'CREDIT'
    PAYMENT_PREPAID = 'PREPAID'

    PAYMENT_CHOICES = [
        (PAYMENT_CREDIT, 'Công nợ'),
        (PAYMENT_PREPAID, 'Thanh toán trước'),
    ]

    # --- 2. Các cột dữ liệu thực tế ---

    # Cột 1: Loại hình (Chọn từ danh sách trên)
    type = models.CharField(
        max_length=3,
        choices=SUPPLIER_TYPE_CHOICES,
        default=HOTEL,
        verbose_name="Loại hình"
    )

    # Cột 2: Tên nhà cung cấp (Dạng văn bản ngắn)
    name = models.CharField(max_length=200, verbose_name="Tên nhà cung cấp")

    # Cột 2: Sếp Hạng (Số tự nhiên)
    chart = models.CharField(max_length=1, blank=True, verbose_name="Tiêu chuẩn")


    # Cột 3: Địa chỉ & SĐT bàn
    address = models.TextField(blank=True, verbose_name="Địa chỉ")
    landline = models.CharField(max_length=20, blank=True, verbose_name="SĐT Bàn")

    # Cột 4: Phụ trách Agent (SĐT di động)
    agent_contact = models.CharField(max_length=20, verbose_name="SĐT Phụ trách (Agent)")

    # Cột 5: Loại hình thanh toán
    payment_term = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_PREPAID,
        verbose_name="Hình thức thanh toán"
    )

    # Cột 6: Hình thức báo giá
    # (Tạm thời dùng Text để ghi chú, ví dụ: "Giá net theo phòng, ăn sáng riêng")
    quotation_note = models.TextField(blank=True, verbose_name="Ghi chú báo giá")

    # Tự động lưu ngày tạo để quản lý
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
