from django.contrib import admin
from .models import Tour, TourService, TourDay, TourServiceCost
from finance.models import Receipt, Payment

# --- 1. Giao diện nhập Phiếu Thu ---
class ReceiptInline(admin.TabularInline):
    model = Receipt
    extra = 0
    classes = ['collapse']
    verbose_name = "Phiếu Thu (Khách đóng tiền)"
    verbose_name_plural = "QUẢN LÝ THU (RECEIPTS)"

# --- 2. Giao diện nhập Phiếu Chi ---
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    classes = ['collapse']
    verbose_name = "Phiếu Chi (Trả NCC)"
    verbose_name_plural = "QUẢN LÝ CHI (PAYMENTS)"

# --- 3. Giao diện Lịch trình từng ngày (Ma trận & Chi tiết) ---
class TourDayInline(admin.StackedInline):
    model = TourDay
    extra = 0
    fieldsets = (
        ('Thông tin ngày & Tiêu đề', {
            'fields': (('day_number', 'day_date_str', 'title'),)
        }),
        ('Dành cho Bảng Hành Trình Tổng Quát (Ma Trận)', {
            'fields': (
                'routing_flight',
                ('morning_desc', 'afternoon_desc', 'evening_desc'),
                ('hotel_name', 'meal_breakfast', 'meal_lunch', 'meal_dinner')
            ),
        }),
        ('Dành cho Báo Giá Tour Chi Tiết (Brochure)', {
            'fields': ('description',),
            'classes': ('collapse',),
        }),
    )

# --- 4. Bóc tách chi phí nhiều NCC con (Dành cho Landtour) ---
class TourServiceCostInline(admin.TabularInline):
    model = TourServiceCost
    extra = 1
    autocomplete_fields = ['supplier']
    fields = ('supplier', 'cost_name', 'quantity', 'times', 'contract_unit_price', 'contract_total_price', 'note')
    verbose_name = "Khoản chi phí Nhà cung cấp con"
    verbose_name_plural = "BÓC TÁCH CHI PHÍ TỪNG NHÀ CUNG CẤP TRONG LANDTOUR"

# --- 5. Giao diện Bảng chi phí tạm tính / Dịch vụ trên Tour ---
class TourServiceInline(admin.TabularInline):
    model = TourService
    extra = 1
    autocomplete_fields = ['supplier']
    fields = (
        'order_index', 'category', 'service_name', 
        'check_in', 'check_out', 'quantity', 'nights',
        'unit_price', 'selling_total_price',
        'supplier', 'contract_unit_price', 'contract_total_price',
        'note'
    )
    class Media:
        js = ('admin/js/tour_service_calc.js',)

# Quản trị TourService riêng biệt (cho phép bóc tách nhiều NCC con cho Landtour)
@admin.register(TourService)
class TourServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'tour', 'category', 'total_selling', 'total_supplier_cost', 'profit')
    list_filter = ('category', 'tour')
    search_fields = ('service_name', 'tour__code', 'tour__title')
    inlines = [TourServiceCostInline]
    autocomplete_fields = ['supplier', 'tour']
    class Media:
        js = ('admin/js/tour_service_calc.js',)

# --- 6. Tổng hợp vào Tour Admin ---
@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'title', 'start_date', 'days', 'guest_count', 
        'total_price', 'deposit_amount', 'balance_receivable', 'status'
    )
    list_filter = ('status', 'pricing_method', 'start_date')
    search_fields = ('code', 'title', 'group_code', 'customer_name', 'quoter_name')

    class Media:
        js = ('admin/js/tour_service_calc.js',)

    inlines = [
        TourDayInline,
        TourServiceInline,
        ReceiptInline,
        PaymentInline,
    ]

    fieldsets = (
        ('1. Thông tin chung chương trình Tour', {
            'fields': (
                ('title', 'subtitle'),
                ('code', 'group_code', 'status', 'tour_type'),
                ('start_date', 'end_date', 'days', 'nights'),
                ('guest_count', 'guest_detail', 'room_count_desc'),
                ('vehicle_info', 'guide_info', 'leader_info'),
                'flights_summary',
            )
        }),
        ('2. Thông tin Báo giá & Khách hàng', {
            'fields': (
                ('quoter_name', 'quoter_phone'),
                ('quote_date', 'valid_until'),
                ('customer_name', 'customer_phone'),
            )
        }),
        ('3. Thiết lập tính giá & Điều kiện thanh toán', {
            'fields': (
                ('currency', 'pricing_method'),
                ('margin_percent', 'margin_amount'),
                ('custom_total_price', 'deposit_amount'),
            )
        }),
        ('4. Tiêu chuẩn & Điều khoản chi tiết (Brochure & Báo giá)', {
            'classes': ('collapse',),
            'fields': (
                'hotel_standards',
                'inclusions',
                'exclusions',
                'tips',
                'terms',
                'notes',
            )
        }),
        ('5. Thông tin đơn vị phát hành (Footer)', {
            'classes': ('collapse',),
            'fields': (
                ('company_name', 'company_hotline'),
                ('company_address', 'company_landline'),
            )
        }),
    )


