from django.contrib import admin
from .models import Tour, TourService, TourDay
from finance.models import Receipt, Payment # <--- Import từ app finance

# --- 1. Giao diện nhập Phiếu Thu ---
class ReceiptInline(admin.TabularInline):
    model = Receipt
    extra = 0
    classes = ['collapse'] # Mặc định thu gọn lại cho đỡ rối
    verbose_name = "Phiếu Thu (Khách đóng tiền)"
    verbose_name_plural = "QUẢN LÝ THU (RECEIPTS)"

# --- 2. Giao diện nhập Phiếu Chi ---
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    classes = ['collapse']
    verbose_name = "Phiếu Chi (Trả NCC)"
    verbose_name_plural = "QUẢN LÝ CHI (PAYMENTS)"

# --- 3. Giao diện các phần cũ ---
class TourDayInline(admin.StackedInline):
    model = TourDay
    extra = 0

class TourServiceInline(admin.TabularInline):
    model = TourService
    extra = 1
    autocomplete_fields = ['supplier']
    fields = ('supplier', 'service_name', 'service_date', 'end_date', 'quantity', 'price_net')

# --- 4. Tổng hợp vào Tour Admin ---
@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    # Hiển thị thêm các cột tài chính ra danh sách ngoài
    list_display = ('code', 'title', 'total_price', 'total_collected', 'remaining_receivable', 'status')

    # Sắp xếp thứ tự các bảng con bên trong
    inlines = [
        ReceiptInline,      # Nhập thu trước
        PaymentInline,      # Nhập chi sau
        TourDayInline,      # Rồi đến nội dung
        TourServiceInline   # Cuối cùng là dịch vụ
    ]

    fieldsets = (
        ('Thông tin chung', {
            'fields': ('title', 'code', 'status', 'start_date', 'days', 'guest_count')
        }),
        ('Cài đặt tính giá', {
            'fields': ('pricing_method', 'margin_amount', 'margin_percent'),
        }),
    )
