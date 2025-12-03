import google as genai
from django.conf import settings

from django.db import models
from suppliers.models import Supplier
from datetime import timedelta

class Tour(models.Model):
    # --- 1. Các trạng thái ---
    DRAFT = 'DRAFT'
    CONFIRMED = 'CONF'
    CANCELLED = 'CAN'

    STATUS_CHOICES = [
        (DRAFT, 'Bản nháp'),
        (CONFIRMED, 'Đã chốt'),
        (CANCELLED, 'Đã hủy'),
    ]

    # --- 2. Các phương thức tính giá ---
    METHOD_PROFIT = 'PROFIT'
    METHOD_PERCENT = 'PERCENT'

    PRICING_CHOICES = [
        (METHOD_PROFIT, 'Theo lợi nhuận cố định'),
        (METHOD_PERCENT, 'Theo % lợi nhuận'),
    ]

    # --- 3. Thông tin cơ bản ---
    title = models.CharField(max_length=200, verbose_name="Tên chương trình Tour")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã Tour (Code)")
    guest_count = models.IntegerField(default=1, verbose_name="Số lượng khách (Pax)")
    start_date = models.DateField(verbose_name="Ngày khởi hành")
    days = models.IntegerField(default=1, verbose_name="Số ngày")

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=DRAFT, verbose_name="Trạng thái"
    )

    # --- 4. Nhập liệu tính giá ---
    pricing_method = models.CharField(
        max_length=10, choices=PRICING_CHOICES, default=METHOD_PERCENT, verbose_name="Cách tính giá"
    )
    margin_amount = models.DecimalField(
        default=0, max_digits=12, decimal_places=0, verbose_name="Lợi nhuận mong muốn (VND)"
    )
    margin_percent = models.IntegerField(
        default=10, verbose_name="% Lợi nhuận"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.code}] {self.title}"

    # --- LOGIC TÍNH GIÁ (SALES) ---
    @property
    def total_cost(self):
        """Tổng giá vốn (Net) dự kiến"""
        total = 0
        for service in self.services.all():
            total += service.total_net
        return total

    @property
    def total_price(self):
        """Tổng giá bán (Sales)"""
        cost = self.total_cost
        if self.pricing_method == self.METHOD_PROFIT:
            return cost + self.margin_amount
        else:
            return cost + (cost * self.margin_percent / 100)

    @property
    def profit(self):
        return self.total_price - self.total_cost

    @property
    def price_per_pax(self):
        if self.guest_count > 0:
            return self.total_price / self.guest_count
        return 0

    # ==========================================
    # LOGIC TÀI CHÍNH (FINANCE & CASHFLOW) - MỚI
    # ==========================================
    @property
    def total_collected(self):
        """Tổng tiền ĐÃ THU từ khách"""
        total = 0
        # receipts là related_name ta đặt bên file finance/models.py
        for receipt in self.receipts.all():
            total += receipt.amount
        return total

    @property
    def remaining_receivable(self):
        """Công nợ khách hàng (Phải thu - Đã thu)"""
        return self.total_price - self.total_collected

    @property
    def total_paid(self):
        """Tổng tiền ĐÃ CHI cho nhà cung cấp"""
        total = 0
        for payment in self.payments.all():
            total += payment.amount
        return total

    @property
    def cashflow_profit(self):
        """Lợi nhuận thực tế (Tiền túi hiện tại: Thu - Chi)"""
        return self.total_collected - self.total_paid


# --- QUẢN LÝ NGÀY TRONG TOUR ---
class TourDay(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='tour_days')
    day_number = models.IntegerField(verbose_name="Ngày thứ")
    title = models.CharField(max_length=200, verbose_name="Tiêu đề (VD: Tham quan Bà Nà Hills)")
    description = models.TextField(verbose_name="Nội dung chi tiết", blank=True) # Cho phép để trống để AI viết

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Ngày {self.day_number}: {self.title}"

    # --- ĐOẠN CODE MAGIC NẰM Ở ĐÂY ---
    def save(self, *args, **kwargs):
        # Kiểm tra: Nếu có Tiêu đề nhưng chưa có Nội dung -> Gọi AI
        if self.title and not self.description:
            try:
                # 1. Cấu hình AI
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.Client('gemini-1.0')

                # 2. Ra lệnh cho AI (Prompt)
                prompt = f"""
                Bạn là một hướng dẫn viên du lịch chuyên nghiệp tại Việt Nam.
                Hãy viết một đoạn giới thiệu hấp dẫn, lôi cuốn (khoảng 3-4 câu) bằng tiếng Việt cho địa điểm hoặc hoạt động sau: "{self.title}".
                Văn phong tự nhiên, mời gọi khách du lịch. Không dùng các ký tự markdown (như ** hoặc #).
                """

                # 3. Chờ AI trả lời
                response = client.model.generate_content(prompt)

                # 4. Điền câu trả lời vào ô description
                self.description = response.text

            except Exception as e:
                # Nếu mạng lỗi hoặc AI bị ốm thì ghi tạm dòng này
                self.description = f"(Tự động điền lỗi: {str(e)}. Vui lòng nhập tay.)"

        # Lưu dữ liệu như bình thường
        super().save(*args, **kwargs)


# --- QUẢN LÝ DỊCH VỤ ---
class TourService(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='services')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    service_name = models.CharField(max_length=200, verbose_name="Tên dịch vụ")

    service_date = models.DateField(verbose_name="Ngày sử dụng / Check-in")
    end_date = models.DateField(null=True, blank=True, verbose_name="Ngày Check-out (Nếu là KS)")

    quantity = models.IntegerField(default=1, verbose_name="Số lượng")
    price_net = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Đơn giá Net (VND)")

    @property
    def days_duration(self):
        if self.supplier and self.supplier.type == 'HTL' and self.end_date:
            delta = self.end_date - self.service_date
            return max(1, delta.days)
        return 1

    @property
    def total_net(self):
        return self.quantity * self.price_net * self.days_duration

    def __str__(self):
        return f"{self.service_name} ({self.service_date})"
